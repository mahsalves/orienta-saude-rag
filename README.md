# orienta-saude-rag

**Assistente Inteligente de Acolhimento, Triagem Informativa e Orientação de Fluxo Clínico Baseado em Documentos Oficiais de Saúde.**

## Sobre o projeto

O **Orienta-SAUDE RAG** é um projeto prático desenvolvido para a 1ª unidade da disciplina de **Tópicos Especiais em Inteligência Artificial (TEIA)**.

A aplicação é um protótipo acadêmico destinado a fins educacionais e informativos. Não realiza diagnósticos médicos, não prescreve tratamentos farmacológicos e não substitui a avaliação de profissionais de saúde.

Em caso de emergência médica, procure atendimento imediatamente ou ligue para o **SAMU (192)**.

## Equipe

- Marcela Helena
- Jennifer de Oliveira

## Sobre o problema

A desinformação sobre sintomas e saúde na internet pode levar à automedicação, à interpretação equivocada de sintomas e à procura inadequada pelos serviços de saúde. Além disso, o uso de Modelos de Linguagem de Grande Porte (LLMs) sem mecanismos de fundamentação pode resultar em respostas incorretas ou informações sem respaldo documental.

O **Orienta-SAUDE RAG** propõe uma camada de acolhimento e orientação informativa. O sistema recebe queixas em linguagem natural, identifica termos clínicos relevantes, consulta documentos recuperados de uma base vetorial e gera respostas fundamentadas no contexto encontrado.

A proposta é auxiliar o usuário a compreender possíveis fluxos de atendimento, como Atenção Primária, avaliação especializada ou emergência, sem substituir a avaliação de profissionais de saúde.

A utilização da arquitetura RAG (*Retrieval-Augmented Generation*) permite combinar a capacidade de geração de linguagem da LLM com a recuperação de informações de documentos previamente indexados. A interface também apresenta os trechos recuperados e seus metadados, favorecendo a transparência e a inspeção dos resultados.

## Funcionalidades

- Interface web interativa desenvolvida com Streamlit.
- Chat para envio de dúvidas e relatos de saúde em linguagem natural.
- Expansão da consulta para identificar termos clínicos e gerar uma consulta otimizada para a busca vetorial.
- Recuperação semântica de trechos armazenados no ChromaDB.
- Geração de orientações por meio de um modelo de linguagem acessado pela API da Groq.
- Exibição das queixas principais, dos termos clínicos identificados, das hipóteses ou protocolos considerados e dos sinais de alerta sugeridos.
- Exibição dos documentos de origem, das páginas e dos scores de similaridade dos trechos recuperados.
- Controle da temperatura de geração da resposta final.
- Controle da quantidade de trechos recuperados por meio do parâmetro `k`.
- Exibição do consumo estimado de tokens do prompt, da resposta e do total.
- Medição da latência das solicitações.
- Histórico de mensagens durante a sessão.
- Área de transparência e auditoria com informações sobre a expansão da consulta, os trechos recuperados e as métricas.

## Conteúdos da unidade aplicados

O projeto implementa conceitos estudados na disciplina de TEIA, relacionando fundamentos teóricos a uma aplicação prática.

| Conceito                                           | Implementação no projeto                                                                                                                                                                       |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tokenização**                                    | Estimativa e exibição do consumo de tokens do prompt e da resposta, permitindo observar o custo computacional associado às solicitações.                                                       |
| **Embeddings**                                     | Conversão dos documentos e das consultas em representações vetoriais para permitir a recuperação semântica. O modelo utilizado na etapa de ingestão é `paraphrase-multilingual-MiniLM-L12-v2`. |
| **Modelos de Linguagem de Grande Porte (LLMs)**    | Utilização de um modelo de linguagem acessado pela API da Groq para expandir consultas e gerar orientações baseadas no contexto recuperado.                                                    |
| **Engenharia de Prompt**                           | Utilização de instruções estruturadas para extrair informações clínicas relevantes e orientar a geração de respostas com atenção à segurança e às fontes documentais.                          |
| **RAG (Retrieval-Augmented Generation)**           | Integração entre recuperação vetorial de documentos, construção de contexto e geração de respostas pela LLM.                                                                                   |
| **Busca semântica**                                | Recuperação dos trechos mais relevantes para a consulta com base na proximidade entre suas representações vetoriais.                                                                           |
| **Transparência e interpretabilidade operacional** | Exibição dos termos identificados, da consulta utilizada, dos trechos recuperados, dos documentos de origem e das métricas da execução.                                                        |

## Arquitetura do sistema

O processamento do Orienta-SAUDE RAG é organizado em etapas sequenciais.

### 1. Entrada do usuário

O usuário descreve uma dúvida ou queixa de saúde em linguagem natural por meio da interface desenvolvida com Streamlit.

### 2. Expansão da consulta

O sistema utiliza uma LLM para interpretar o relato e organizar informações relevantes para a recuperação documental.

Essa etapa pode identificar:

- Queixas principais;
- Termos clínicos relacionados aos sintomas;
- Hipóteses ou protocolos a serem considerados na busca;
- Sinais de alerta sugeridos;
- Consulta otimizada para a busca vetorial.

A expansão busca aproximar a linguagem cotidiana utilizada pelo usuário da terminologia presente nos documentos clínicos.

### 3. Recuperação vetorial

A consulta otimizada é convertida em uma representação vetorial por meio do modelo de embeddings utilizado pelo projeto.

O ChromaDB armazena os vetores e os metadados dos documentos indexados. A consulta é comparada com a base para recuperar os trechos mais relevantes.

A quantidade de trechos retornados pode ser controlada pelo parâmetro `k`.

### 4. Construção do contexto

Os trechos recuperados são organizados para compor o contexto enviado à LLM. Os metadados permitem identificar documentos e páginas de origem.

Essa etapa busca fornecer informações documentais relevantes para fundamentar a resposta, em vez de depender exclusivamente do conhecimento aprendido pelo modelo durante seu treinamento.

### 5. Geração da orientação

A LLM recebe a pergunta do usuário e o contexto recuperado. Com base nas instruções do sistema, gera uma resposta em linguagem acessível, considerando as informações disponíveis e a necessidade de orientar o usuário quanto à procura por atendimento.

A geração deve priorizar a segurança e evitar apresentar hipóteses como diagnósticos confirmados.

### 6. Apresentação dos resultados

A interface Streamlit apresenta a resposta e disponibiliza informações complementares para inspeção do funcionamento do sistema:

- **Expansão da query:** termos clínicos identificados e consulta utilizada na busca;
- **Chunks recuperados:** trechos documentais, páginas de origem e scores de similaridade;
- **Métricas:** consumo estimado de tokens e latência da solicitação.

### Fluxo resumido

```text
Relato do usuário
       |
       v
Expansão da consulta pela LLM
       |
       +--> Queixas principais
       +--> Termos clínicos
       +--> Sinais de alerta sugeridos
       +--> Consulta otimizada
                    |
                    v
          Modelo de embeddings
                    |
                    v
                ChromaDB
                    |
                    v
         Recuperação de trechos
                    |
                    v
          Construção do contexto
                    |
                    v
          Geração pela LLM
                    |
                    v
       Resposta, fontes e métricas
                    |
                    v
           Interface Streamlit
```

**Importante:** a recuperação de documentos e a apresentação dos scores de similaridade não garantem, por si só, a correção clínica da resposta. É necessário verificar se os trechos recuperados sustentam as orientações geradas.

## Tecnologias utilizadas

- **Python:** linguagem de programação principal.
- **Streamlit:** desenvolvimento da interface web.
- **Groq API:** acesso ao modelo de linguagem.
- **ChromaDB:** armazenamento e recuperação vetorial.
- **Sentence Transformers:** geração de embeddings.
- **paraphrase-multilingual-MiniLM-L12-v2:** modelo de embeddings utilizado no processamento dos documentos.
- **tiktoken:** estimativa de consumo de tokens.
- **python-dotenv:** leitura de variáveis de ambiente.

## Estrutura do projeto

A estrutura abaixo representa os principais componentes do projeto. A organização exata dos arquivos e diretórios pode variar conforme a configuração local.

```text
orienta-saude-rag/
├── src/
│   ├── app.py                 # Interface Streamlit
│   ├── rag_engine.py          # Motor de processamento RAG
│   ├── ingestion.py           # Ingestão e indexação dos documentos
│   └── test_end_to_end.py     # Teste ponta a ponta
├── chroma_db/                 # Base vetorial persistida
├── .env                       # Variáveis de ambiente e chave da API
├── .gitignore                 # Arquivos e diretórios ignorados pelo Git
├── requirements.txt           # Dependências do projeto
└── README.md                  # Documentação
```

A base vetorial é utilizada pelo motor RAG para recuperar os trechos relevantes. O processo de ingestão depende dos documentos PDF e dos caminhos configurados em `src/ingestion.py`.

## Como executar

### 1. Pré-requisitos

Antes de iniciar, é necessário ter:

- Python 3.10 ou superior;
- Git instalado;
- Uma chave de API da Groq;
- Os documentos PDF utilizados na base de conhecimento;
- As dependências do projeto instaladas.

A chave da API pode ser obtida no [console oficial da Groq](https://console.groq.com/keys).

### 2. Clonar o repositório

```bash
git clone https://github.com/mahsalves/orienta-saude-rag.git
cd orienta-saude-rag
```

### 3. Criar o ambiente virtual

No Windows, utilizando o PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

Caso o PowerShell bloqueie a ativação do ambiente, é possível utilizar diretamente o caminho do interpretador Python do ambiente escolhido.

### 4. Instalar as dependências

Com o ambiente ativado, execute:

```bash
python -m pip install -r requirements.txt
```

Verifique se o arquivo `requirements.txt` contém todas as bibliotecas utilizadas pelo projeto, incluindo Streamlit, OpenAI, ChromaDB, Sentence Transformers, `tiktoken` e `python-dotenv`, conforme os imports efetivamente presentes no código.

### 5. Configurar as variáveis de ambiente

Crie um arquivo chamado `.env` na raiz do projeto e adicione sua chave da Groq:

```dotenv
GROQ_API_KEY=gsk_sua_chave_aqui
```

Substitua `gsk_sua_chave_aqui` pela chave real da sua conta.

**Não compartilhe sua chave de API nem a envie para o GitHub.** Verifique se o arquivo `.env` está incluído no `.gitignore`.

### 6. Criar ou reconstruir a base vetorial

Se a base vetorial ainda não tiver sido criada, execute:

```bash
python src/ingestion.py
```

Esse processo lê os documentos PDF configurados no script, divide seus conteúdos em trechos e gera os embeddings necessários para a indexação no ChromaDB.

O primeiro processamento pode demorar devido ao carregamento ou download do modelo de embeddings.

Se a base já estiver construída e disponível, não é necessário executar a ingestão novamente a cada inicialização da interface.

### 7. Executar o teste ponta a ponta

Para verificar o funcionamento do pipeline antes de iniciar a interface, execute:

```bash
python src/test_end_to_end.py
```

O teste valida o fluxo de expansão da consulta, recuperação de trechos, geração de resposta e apresentação das métricas no terminal.

A execução depende da configuração correta da chave de API, das dependências e da disponibilidade da base vetorial.

### 8. Iniciar a interface Streamlit

Na raiz do projeto, execute:

```bash
python -m streamlit run src/app.py
```

Se houver problemas relacionados ao monitoramento automático de arquivos, é possível iniciar a aplicação desativando esse recurso:

```bash
python -m streamlit run src/app.py --server.fileWatcherType none
```

O Streamlit exibirá no terminal o endereço local da aplicação, normalmente:

```text
http://localhost:8501
```

## Como utilizar a interface

1. Inicie a aplicação Streamlit.
2. Digite uma pergunta ou um relato de saúde no campo de chat.
3. Ajuste a temperatura da geração final, se necessário.
4. Selecione a quantidade de trechos a recuperar por meio do controle `k`.
5. Leia a resposta gerada e observe as recomendações de segurança.
6. Acesse a aba **Expansão da query** para consultar os termos clínicos identificados e a consulta utilizada na busca vetorial.
7. Acesse **Chunks recuperados** para examinar os trechos, os documentos de origem, as páginas e os scores de similaridade.
8. Acesse **Métricas** para consultar o consumo estimado de tokens e a latência.
9. Utilize **Limpar conversa** para reiniciar o histórico e as métricas acumuladas da sessão.

## Testes e validação

A validação deve contemplar diferentes tipos de queixa, observando tanto a resposta gerada quanto a pertinência das fontes recuperadas.

| Categoria                           | Exemplos de cenário                                                                            | Critérios de avaliação                                                                                |
| ----------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Emergência**                      | Fraqueza súbita de um lado do corpo, assimetria facial ou dor torácica sugestiva de emergência | Verificar se a resposta reconhece a gravidade potencial e orienta a procura imediata por atendimento. |
| **Atenção primária**                | Acompanhamento de hipertensão ou cefaleia leve sem sinais de alerta relatados                  | Verificar se a orientação é proporcional ao relato e se indica avaliação na UBS quando apropriado.    |
| **Avaliação especializada**         | Perda auditiva progressiva ou suspeita de glaucoma                                             | Verificar se a resposta recomenda avaliação profissional adequada sem afirmar um diagnóstico.         |
| **Pergunta sem suporte documental** | Dúvida para a qual não há trechos pertinentes na base                                          | Verificar se o sistema reconhece a insuficiência de contexto e evita inventar fontes ou informações.  |

Para cada teste, recomenda-se registrar:

- Pergunta enviada;
- Resposta gerada;
- Documentos e páginas recuperados;
- Scores de similaridade;
- Termos identificados na expansão da consulta;
- Tokens estimados e latência;
- Problemas observados e ajustes necessários.

As capturas de tela da interface podem ser adicionadas a esta seção para documentar os resultados obtidos.

Os testes são exploratórios e não substituem uma avaliação clínica formal por profissionais qualificados.

## Segurança, privacidade e limitações

- O Orienta-SAUDE RAG é um protótipo acadêmico, não um serviço clínico nem um dispositivo médico.
- A aplicação não deve ser utilizada para confirmar diagnósticos ou definir tratamentos.
- As respostas geradas por LLM podem conter erros, omissões ou interpretações inadequadas.
- A base documental pode não conter informações suficientes para responder a todas as perguntas.
- Os scores de similaridade indicam proximidade na busca vetorial, não a veracidade ou a qualidade clínica de uma informação.
- A contagem de tokens exibida pela interface é uma estimativa e pode diferir do consumo oficial contabilizado pelo provedor.
- Não devem ser inseridos dados pessoais identificáveis ou informações reais de pacientes durante as demonstrações.
- Em caso de sinais de emergência, o usuário deve procurar atendimento imediatamente ou ligar para o SAMU (192).

## Possíveis melhorias futuras

- Ampliar e revisar a coleção de documentos oficiais.
- Desenvolver uma suíte de testes com perguntas e critérios de avaliação documentados.
- Avaliar a relevância dos trechos recuperados e a fidelidade das respostas às fontes.
- Melhorar o tratamento de perguntas sem contexto suficiente na base.
- Registrar sistematicamente os resultados dos cenários de teste.
- Adicionar capturas de tela da interface e exemplos de uso.
- Manter o arquivo `requirements.txt` atualizado com as dependências efetivamente utilizadas.
- Avaliar a aplicação com profissionais qualificados antes de qualquer uso além do contexto acadêmico.

## Licença

A licença do projeto deve ser definida pela equipe caso o repositório seja distribuído publicamente.
