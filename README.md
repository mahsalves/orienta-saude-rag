# orienta-saude-rag
> Assistente Inteligente de Acolhimento, Triagem e Orientação de Fluxo Clínico Baseado em Protocolos Oficiais do SUS.

---

## Sobre o projeto
Projeto prático desenvolvido para a 1ª Unidade da disciplina de **Tópicos Especiais em Inteligência Artificial (TEIA)**. Esta aplicação é um protótipo acadêmico para fins estritamente educacionais e informativos. Não realiza diagnósticos médicos, não prescreve tratamentos farmacológicos e não substitui uma consulta presencial com profissionais de saúde. Em casos de emergência médica evidente, acione imediatamente o SAMU (192) ou procure a unidade de pronto atendimento mais próxima.

## Equipe
- Marcela Helena
- Jennifer de Oliveira

## Sobre o Problema

A desinformação sobre sintomas e saúde na internet frequentemente leva a dois extremos: automedicação perigosa ou sobrecarga desnecessária de unidades de urgência e emergência (UPAs e hospitais) com demandas que poderiam ser resolvidas na Atenção Primária (UBS). Por outro lado, o uso ingênuo de Modelos de Linguagem de Grande Porte (LLMs) em saúde sem restrições gera alucinações críticas.

O **OrientaSaúde RAG** resolve esse desafio funcionando como uma camada de acolhimento e direcionamento informativo. O sistema recebe queixas em linguagem natural do usuário, identifica sinais de alerta clínicos e determina a porta de entrada recomendada (Atenção Básica, Especialista ou Emergência), embasando cada orientação exclusivamente em **protocolos clínicos e cadernos oficiais do Ministério da Saúde e Telessaúde**.

---

## Conteúdos da Unidade Aplicados

O projeto implementa e evidencia os cinco pilares fundamentais da unidade de TEIA:

| Conceito | Implementação Prática no Projeto |
| :--- | :--- |
| **Tokenização** | Monitoramento e exibição em tempo real do consumo de tokens (prompt de entrada, contexto recuperado dos manuais e resposta gerada), demonstrando a gestão dos limites da janela de contexto (*context window*). |
| **Embeddings** | Fatiamento (*chunking*) dos documentos oficiais e conversão para representações vetoriais densas com o modelo `all-MiniLM-L6-v2` (ou `BAAI/bge-m3`), permitindo busca semântica por proximidade angular e similaridade de cosseno. |
| **Funcionamento do Transformer** | Parametrização e ajuste fino dos hiperparâmetros de inferência (`temperature` baixa para evitar inventividade em saúde, `top_p` e controle de atenção), explicitando a relação entre a camada de atenção e os trechos recuperados. |
| **Engenharia de Prompt** | Uso de *System Prompts* com papéis estritos, *Few-Shot Prompting* para formatação estruturada de saídas em JSON, *Chain-of-Thought* (raciocínio em etapas para triagem de risco) e regras rigorosas de segurança contra alucinações. |
| **RAG (Retrieval-Augmented Generation)** | Pipeline completo: ingestão de PDFs oficiais | fatiamento em blocos com sobreposição (*overlap*) | indexação vetorial no ChromaDB | recuperação semântica | injeção de contexto com citação de fontes oficiais. |

---

## Arquitetura do Sistema

O fluxo de processamento do AcolheSUS RAG é estruturado em quatro etapas sequenciais, garantindo que nenhuma resposta seja gerada sem validação prévia contra as diretrizes oficiais:

- Entrada do Usuário e Pré-processamento:
O usuário insere seu relato de sintomas em linguagem natural e coloquial por meio da interface web (Streamlit).

- Extração Estruturada via Engenharia de Prompt:
Antes de consultar a base de conhecimento, o modelo de linguagem atua como um extrator de entidades clínicas (few-shot prompting com restrição de esquema). Ele normaliza a linguagem cotidiana e devolve um objeto estruturado em JSON contendo: queixa principal padronizada, tempo de evolução e sinais de alerta explícitos relatados pelo usuário.

- Recuperação Vetorial com Grounding Estrito (RAG):
Os termos normalizados são convertidos em vetores densos via modelo de embeddings e comparados contra o banco vetorial local (ChromaDB), que armazena os cadernos e protocolos clínicos oficiais fatiados em blocos com sobreposição (chunking with overlap). O sistema recupera apenas os fragmentos com maior índice de similaridade semântica de cosseno, descartando trechos abaixo do limiar de relevância estabelecido para prevenir alucinações.

- Raciocínio Clínico e Geração com Citação Oficial:
O LLM recebe os trechos oficiais recuperados injetados em seu contexto, junto a um system prompt estrito que implementa raciocínio passo a passo (Chain-of-Thought). O modelo confronta os sintomas do usuário com os critérios de gravidade e encaminhamento dos manuais, gerando a resposta final em linguagem clara e acessível ao cidadão. A saída categoriza a porta de entrada recomendada (Atenção Básica, Especialista ou Emergência), transcreve o trecho de referência do protocolo e exibe as métricas de tokens e similaridade calculadas.
