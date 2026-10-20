import os
from pypdf import PdfReader

PASTA_PDFS = "data/raw"

def testar_leitura():
    arquivos = [f for f in os.listdir(PASTA_PDFS) if f.endswith(".pdf")]
    
    if not arquivos:
        print(f"Nenhum PDF encontrado em '{PASTA_PDFS}'. Coloque seus arquivos lá!")
        return

    print(f"Encontrados {len(arquivos)} arquivo(s) PDF para teste.\n")

    for nome_arquivo in arquivos:
        caminho = os.path.join(PASTA_PDFS, nome_arquivo)
        print(f"Lendo: {nome_arquivo}...")
        
        try:
            reader = PdfReader(caminho)
            total_paginas = len(reader.pages)
            
            # Tenta extrair texto das primeiras 3 páginas
            texto_amostra = ""
            for i in range(min(3, total_paginas)):
                texto_pagina = reader.pages[i].extract_text() or ""
                texto_amostra += texto_pagina

            print(f" -> Total de páginas: {total_paginas}")
            print(f" -> Caracteres extraídos (amostra de até 3 páginas): {len(texto_amostra)}")
            
            if len(texto_amostra.strip()) < 50:
                print(" ⚠️ ALERTA: Pouco ou nenhum texto extraído. O PDF pode ser imagem escaneada.")
            else:
                print(" ✅ Sucesso: Texto legível extraído.")
                print(f" Trecho inicial: {texto_amostra[:200]}...\n")
                
        except Exception as e:
            print(f" ❌ Erro ao ler {nome_arquivo}: {e}\n")

if __name__ == "__main__":
    testar_leitura()