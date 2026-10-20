import os
import re
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

PASTA_PDFS = "data/raw"
CAMINHO_CHROMA = "chroma_db"
NOME_COLECAO = "telecondutas_sus"
MODELO_EMBEDDING = "paraphrase-multilingual-MiniLM-L12-v2"

def limpar_espacos(texto: str) -> str:
    texto = re.sub(r"\n\s*\n+", "\n\n", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto.strip()

def extrair_e_fatiar():
    arquivos = [f for f in os.listdir(PASTA_PDFS) if f.endswith(".pdf")]
    if not arquivos:
        print("Nenhum PDF encontrado em data/raw.")
        return [], []

    # Chunking com ~800 caracteres e boa sobreposição
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", "; ", " ", ""]
    )

    todos_chunks = []
    todos_metadados = []

    print(f"Iniciando leitura e fatiamento contextual de {len(arquivos)} documentos...\n")

    for nome_arquivo in arquivos:
        caminho = os.path.join(PASTA_PDFS, nome_arquivo)
        nome_tema = nome_arquivo.replace(".pdf", "").replace("_", " ")
        try:
            reader = PdfReader(caminho)
            chunks_doc = 0
            
            for num_pag, pagina in enumerate(reader.pages):
                texto_pag = pagina.extract_text() or ""
                texto_limpo = limpar_espacos(texto_pag)
                
                # Ignora páginas puramente burocráticas ou muito curtas
                if len(texto_limpo) < 80:
                    continue
                
                sub_chunks = text_splitter.split_text(texto_limpo)
                for chunk in sub_chunks:
                    # Injeção de contexto estruturado: ajuda diretamente o cálculo de similaridade
                    chunk_enriquecido = f"Protocolo: {nome_tema} | Página {num_pag + 1}\n{chunk}"
                    
                    todos_chunks.append(chunk_enriquecido)
                    todos_metadados.append({
                        "fonte": nome_tema,
                        "pagina": num_pag + 1
                    })
                    chunks_doc += 1

            print(f"✔️ {nome_arquivo}: {chunks_doc} chunks.")
        except Exception as e:
            print(f" --- Erro ao processar {nome_arquivo}: {e} ---")

    return todos_chunks, todos_metadados

def criar_banco_vetorial():
    chunks, metadados = extrair_e_fatiar()
    total = len(chunks)
    print(f"\nTotal geral de chunks enriquecidos: {total}")

    if total == 0:
        return

    print(f"Carregando modelo multilíngue: {MODELO_EMBEDDING}...")
    embed_model = SentenceTransformer(MODELO_EMBEDDING)

    print(f"Indexando no ChromaDB em '{CAMINHO_CHROMA}'...")
    client = chromadb.PersistentClient(path=CAMINHO_CHROMA)
    
    try:
        client.delete_collection(name=NOME_COLECAO)
    except Exception:
        pass

    colecao = client.create_collection(
        name=NOME_COLECAO,
        metadata={"hnsw:space": "cosine"}
    )

    tamanho_lote = 128
    for i in range(0, total, tamanho_lote):
        lote_chunks = chunks[i:i + tamanho_lote]
        lote_meta = metadados[i:i + tamanho_lote]
        lote_ids = [f"doc_{j}" for j in range(i, i + len(lote_chunks))]

        embeddings = embed_model.encode(lote_chunks, show_progress_bar=False).tolist()

        colecao.add(
            documents=lote_chunks,
            embeddings=embeddings,
            metadatas=lote_meta,
            ids=lote_ids
        )
        print(f" -> Processados {min(i + tamanho_lote, total)} de {total} chunks...")

    print("\n --- Base vetorial multilíngue reconstruída com sucesso! ---")

if __name__ == "__main__":
    criar_banco_vetorial()