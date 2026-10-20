import chromadb
from sentence_transformers import SentenceTransformer

def testar_busca():
    client = chromadb.PersistentClient(path="chroma_db")
    colecao = client.get_collection(name="telecondutas_sus")
    
    # Mesmo modelo multilíngue usado na indexação
    embed_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    pergunta = "Estou com fraqueza súbita em um lado do corpo e boca torta, o que pode ser?"
    print(f"Pergunta: \"{pergunta}\"\n")

    query_vector = embed_model.encode([pergunta]).tolist()
    resultados = colecao.query(
        query_embeddings=query_vector,
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    print("=== Resultados Mais Semelhantes Encontrados ===")
    for idx, (doc, meta, dist) in enumerate(zip(resultados["documents"][0], resultados["metadatas"][0], resultados["distances"][0])):
        similaridade = 1.0 - dist
        print(f"\n[Resultado {idx + 1}] - Similaridade: {similaridade:.4f}")
        print(f"Fonte: {meta['fonte']} (Página {meta['pagina']})")
        print(f"Trecho:\n{doc}\n{'-'*40}")

if __name__ == "__main__":
    testar_busca()