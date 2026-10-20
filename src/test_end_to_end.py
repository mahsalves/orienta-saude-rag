from rag_engine import gerar_orientacao_clinica

pergunta = "Estou com fraqueza súbita em um lado do corpo e boca torta, o que pode ser?"
print(f"Testando: \"{pergunta}\"\nProcessando com Query Expansion + RAG...")

resultado = gerar_orientacao_clinica(pergunta)

print("\n=== EXPANSÃO DE TERMOS (ENGENHARIA DE PROMPT) ===")
print(f"Termos identificados: {resultado['analise_clinica'].get('sintomas_tecnicos')}")
print(f"Query semântica gerada: {resultado['metricas']['query_enriquecida']}")

print("\n=== FONTES RECUPERADAS ===")
for c in resultado["chunks"]:
    print(f"-> {c['fonte']} (Pág {c['pagina']}) - Similaridade: {c['similaridade']}")

print("\n=== RESPOSTA FINAL DO ORIENTA-SAUDE ===")
print(resultado["resposta"])

print("\n=== CONSUMO DE TOKENS ===")
print(resultado["metricas"])