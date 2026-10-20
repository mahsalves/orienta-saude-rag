import os
import json
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

client_llm = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)
MODELO_LLM = "qwen/qwen3.8-27b"


client_chroma = chromadb.PersistentClient(path="chroma_db")
colecao = client_chroma.get_collection(name="telecondutas_sus")
embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Tokenizador para contabilizar consumo na interface
enc = tiktoken.get_encoding("cl100k_base")

def contar_tokens(texto: str) -> int:
    return len(enc.encode(texto))

def traduzir_queixa_para_termos_clinicos(relato_usuario: str) -> dict:
    """Etapa de Engenharia de Prompt: converte linguagem popular em descritores clínicos do SUS."""
    prompt_sistema = """Você é um especialista em acolhimento e terminologia clínica do SUS.
Analise o relato leigo do paciente e devolva APENAS um JSON válido no formato:
{
  "queixas_principais": ["termo1", "termo2"],
  "sintomas_tecnicos": ["termo_medico1", "termo_medico2"],
  "hipoteses_protocolos": ["nome de possíveis doenças ou protocolos relacionados"],
  "sinais_alerta_sugeridos": ["possíveis bandeiras vermelhas"],
  "query_busca": "frase sintetizada com termos técnicos para busca em banco vetorial"
}
Não adicione explicações fora do JSON."""

    resposta = client_llm.chat.completions.create(
        model=MODELO_LLM,
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": relato_usuario}
        ],
        temperature=0.1
    )
    
    conteudo = resposta.choices[0].message.content.strip()
    # Limpa possíveis marcadores markdown ```json
    if conteudo.startswith("```"):
        conteudo = conteudo.split("\n", 1)[1].rsplit("\n", 1)[0]
    
    try:
        return json.loads(conteudo)
    except Exception:
        return {"query_busca": relato_usuario, "sintomas_tecnicos": []}

def buscar_contexto(query_text: str, n_resultados: int = 4):
    query_vector = embed_model.encode([query_text]).tolist()
    resultados = colecao.query(
        query_embeddings=query_vector,
        n_results=n_resultados,
        include=["documents", "metadatas", "distances"]
    )
    
    chunks_recuperados = []
    for doc, meta, dist in zip(resultados["documents"][0], resultados["metadatas"][0], resultados["distances"][0]):
        similaridade = 1.0 - dist
        chunks_recuperados.append({
            "texto": doc,
            "fonte": meta["fonte"],
            "pagina": meta["pagina"],
            "similaridade": round(similaridade, 4)
        })
    return chunks_recuperados

def gerar_orientacao_clinica(relato_usuario: str, temperatura: float = 0.2):
    print(" [1/4] Traduzindo queixa para termos clínicos (LLM)...")
    analise_clinica = traduzir_queixa_para_termos_clinicos(relato_usuario)
    query_otimizada = analise_clinica.get("query_busca", relato_usuario)
    
    print(f" [2/4] Buscando no ChromaDB com a query: '{query_otimizada}'...")
    chunks = buscar_contexto(query_otimizada, n_resultados=4)
    
    contexto_formatado = "\n\n---\n\n".join([
        f"[DOCUMENTO: {c['fonte']} | PÁGINA: {c['pagina']} | SIMILARIDADE: {c['similaridade']}]\n{c['texto']}"
        for c in chunks
    ])

    system_prompt = f"""Você é o Orienta-SAUDE, assistente de acolhimento e orientação em saúde fundamentado estritamente nas diretrizes oficiais do SUS e Telessaúde.

DIRETRIZES FUNDAMENTAIS:
1. Baseie-se ESTRITAMENTE nos trechos oficiais fornecidos no CONTEXTO.
2. Identifique sinais de alarme. Se houver suspeita de risco imediato (ex: AVC, infarto, parada), oriente com clareza a procura imediata de UPA/Emergência ou ligação para o SAMU (192).
3. Se a queixa for de manejo crônico ou leve, oriente a Unidade Básica de Saúde (UBS/Clínico Geral).
4. Indique a especialidade médica correlata se os critérios dos protocolos forem atendidos.
5. Ao final, cite explicitamente os documentos e páginas que embasaram a resposta.
6. Mantenha tom empático, claro e cidadão, evitando termos herméticos sem explicação.

CONTEXTO OFICIAL DISPONÍVEL:
{contexto_formatado}
"""

    tokens_prompt = contar_tokens(system_prompt) + contar_tokens(relato_usuario)

    print("⏳ [3/4] Gerando resposta fundamentada nos protocolos (LLM)...")
    resposta_llm = client_llm.chat.completions.create(
        model=MODELO_LLM,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Relato do paciente: {relato_usuario}"}
        ],
        temperature=temperatura,
        max_tokens=900
    )

    print(" [4/4] Concluído com sucesso!\n")
    texto_final = resposta_llm.choices[0].message.content
    tokens_resposta = contar_tokens(texto_final)

    return {
        "resposta": texto_final,
        "analise_clinica": analise_clinica,
        "chunks": chunks,
        "metricas": {
            "tokens_prompt": tokens_prompt,
            "tokens_resposta": tokens_resposta,
            "tokens_total": tokens_prompt + tokens_resposta,
            "query_enriquecida": query_otimizada
        }
    }