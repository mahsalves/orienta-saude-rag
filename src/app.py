import time
import sqlite3
from pathlib import Path
import sys

import streamlit as st

# Permite importar rag_engine.py quando o Streamlit é iniciado pela raiz do projeto.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rag_engine import gerar_orientacao_clinica


HISTORY_DB = ROOT_DIR / "data" / "history.sqlite3"


def inicializar_historico():
    HISTORY_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(HISTORY_DB) as conexao:
        conexao.execute(
            """CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                criada_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )


def listar_historico():
    with sqlite3.connect(HISTORY_DB) as conexao:
        return conexao.execute(
            "SELECT id, pergunta, resposta, criada_em FROM conversas ORDER BY id DESC"
        ).fetchall()


def salvar_conversa(pergunta, resposta):
    with sqlite3.connect(HISTORY_DB) as conexao:
        conexao.execute(
            "INSERT INTO conversas (pergunta, resposta) VALUES (?, ?)",
            (pergunta, resposta),
        )


inicializar_historico()


st.set_page_config(
    page_title="Orienta-SAUDE | RAG",
    page_icon="🩺",
    layout="wide",
)

st.title("🩺 Orienta-SAUDE")
st.caption(
    "Protótipo de acolhimento e orientação em saúde fundamentado em documentos "
    "recuperados pela base vetorial."
)
st.warning(
    "Protótipo acadêmico: não substitui avaliação de profissionais de saúde. "
    "Em uma emergência, procure atendimento imediatamente ou ligue para o SAMU (192)."
)

with st.sidebar:
    st.header("Histórico de perguntas")
    historico = listar_historico()
    if historico:
        opcoes_historico = {
            f"#{id_conversa} · {pergunta[:70]}{'…' if len(pergunta) > 70 else ''} · {criada_em}": (pergunta, resposta)
            for id_conversa, pergunta, resposta, criada_em in historico
        }
        selecionada = st.selectbox("Perguntas anteriores", ["Selecione uma pergunta"] + list(opcoes_historico))
        if selecionada != "Selecione uma pergunta":
            pergunta_antiga, resposta_antiga = opcoes_historico[selecionada]
            st.markdown("**Pergunta**")
            st.write(pergunta_antiga)
            st.markdown("**Resposta**")
            st.write(resposta_antiga)
    else:
        st.caption("As perguntas respondidas aparecerão aqui.")

    st.header("Configurações")
    temperatura = st.slider(
        "Temperatura da LLM",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Valores menores tendem a gerar respostas mais determinísticas.",
    )
    k = st.slider(
        "Chunks recuperados (k)",
        min_value=1,
        max_value=10,
        value=4,
        step=1,
        help="Quantidade de trechos da base vetorial enviados como contexto.",
    )
    st.divider()
    st.subheader("Consumo da sessão")
    metricas_sessao = st.session_state.get(
        "metricas_sessao",
        {"tokens_prompt": 0, "tokens_resposta": 0, "tokens_total": 0},
    )
    c1, c2 = st.columns(2)
    c1.metric("Tokens prompt", metricas_sessao["tokens_prompt"])
    c2.metric("Tokens resposta", metricas_sessao["tokens_resposta"])
    st.metric("Tokens totais", metricas_sessao["tokens_total"])
    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.metricas_sessao = {
            "tokens_prompt": 0,
            "tokens_resposta": 0,
            "tokens_total": 0,
        }
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "metricas_sessao" not in st.session_state:
    st.session_state.metricas_sessao = {
        "tokens_prompt": 0,
        "tokens_resposta": 0,
        "tokens_total": 0,
    }

# Reexibe o histórico sem chamar novamente a LLM.
for mensagem in st.session_state.messages:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])
        if mensagem["role"] == "assistant" and mensagem.get("resultado"):
            resultado = mensagem["resultado"]
            with st.expander("Transparência e auditoria desta resposta"):
                tab_query, tab_chunks, tab_tokens = st.tabs(
                    ["Expansão da query", "Chunks recuperados", "Métricas"]
                )
                with tab_query:
                    analise = resultado.get("analise_clinica", {})
                    st.markdown("**Query usada na busca vetorial**")
                    st.code(
                        resultado.get("metricas", {}).get("query_enriquecida", ""),
                        language=None,
                    )
                    for rotulo, chave in [
                        ("Queixas principais", "queixas_principais"),
                        ("Termos clínicos", "sintomas_tecnicos"),
                        ("Hipóteses/protocolos identificados", "hipoteses_protocolos"),
                        ("Sinais de alerta sugeridos", "sinais_alerta_sugeridos"),
                    ]:
                        valores = analise.get(chave, [])
                        st.markdown(f"**{rotulo}:**")
                        if valores:
                            st.write(", ".join(map(str, valores)))
                        else:
                            st.write("Nenhum termo retornado.")

                with tab_chunks:
                    chunks = resultado.get("chunks", [])
                    if not chunks:
                        st.info("Nenhum trecho foi recuperado.")
                    for i, chunk in enumerate(chunks, start=1):
                        st.markdown(
                            f"**Trecho {i} — {chunk.get('fonte', 'Fonte não informada')} "
                            f"(página {chunk.get('pagina', '—')})**"
                        )
                        st.caption(
                            f"Score de similaridade retornado: {chunk.get('similaridade', '—')}"
                        )
                        st.write(chunk.get("texto", ""))
                        if i < len(chunks):
                            st.divider()

                with tab_tokens:
                    metricas = resultado.get("metricas", {})
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Tokens do prompt", metricas.get("tokens_prompt", 0))
                    m2.metric("Tokens da resposta", metricas.get("tokens_resposta", 0))
                    m3.metric("Tokens totais", metricas.get("tokens_total", 0))
                    st.metric("Latência desta resposta", f"{resultado.get('latencia_segundos', 0):.2f} s")

pergunta = st.chat_input("Descreva sua dúvida ou queixa de saúde...")
if pergunta:
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Analisando a queixa e consultando os documentos..."):
            try:
                inicio = time.perf_counter()
                resultado = gerar_orientacao_clinica(
                    pergunta,
                    temperatura=temperatura,
                    k=k,
                )
                latencia = time.perf_counter() - inicio
                resultado["latencia_segundos"] = latencia
                resposta = resultado.get("resposta") or (
                    "Não foi possível gerar uma resposta para esta solicitação."
                )
                st.markdown(resposta)

                metricas = resultado.get("metricas", {})
                for chave in ("tokens_prompt", "tokens_resposta", "tokens_total"):
                    st.session_state.metricas_sessao[chave] += int(metricas.get(chave, 0))

                with st.expander("Transparência e auditoria desta resposta", expanded=True):
                    tab_query, tab_chunks, tab_tokens = st.tabs(
                        ["Expansão da query", "Chunks recuperados", "Métricas"]
                    )
                    with tab_query:
                        analise = resultado.get("analise_clinica", {})
                        st.markdown("**Query usada na busca vetorial**")
                        st.code(
                            metricas.get("query_enriquecida", ""),
                            language=None,
                        )
                        for rotulo, chave in [
                            ("Queixas principais", "queixas_principais"),
                            ("Termos clínicos", "sintomas_tecnicos"),
                            ("Hipóteses/protocolos identificados", "hipoteses_protocolos"),
                            ("Sinais de alerta sugeridos", "sinais_alerta_sugeridos"),
                        ]:
                            valores = analise.get(chave, [])
                            st.markdown(f"**{rotulo}:**")
                            st.write(", ".join(map(str, valores)) if valores else "Nenhum termo retornado.")

                    with tab_chunks:
                        chunks = resultado.get("chunks", [])
                        if not chunks:
                            st.info("Nenhum trecho foi recuperado.")
                        for i, chunk in enumerate(chunks, start=1):
                            st.markdown(
                                f"**Trecho {i} — {chunk.get('fonte', 'Fonte não informada')} "
                                f"(página {chunk.get('pagina', '—')})**"
                            )
                            st.caption(
                                f"Score de similaridade retornado: {chunk.get('similaridade', '—')}"
                            )
                            st.write(chunk.get("texto", ""))
                            if i < len(chunks):
                                st.divider()

                    with tab_tokens:
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Tokens do prompt", metricas.get("tokens_prompt", 0))
                        m2.metric("Tokens da resposta", metricas.get("tokens_resposta", 0))
                        m3.metric("Tokens totais", metricas.get("tokens_total", 0))
                        st.metric("Latência desta resposta", f"{latencia:.2f} s")

                st.session_state.messages.append(
                    {"role": "assistant", "content": resposta, "resultado": resultado}
                )
                salvar_conversa(pergunta, resposta)
                st.rerun()
            except Exception as erro:
                mensagem_erro = (
                    "Não foi possível processar a solicitação. Verifique a configuração "
                    "da chave GROQ_API_KEY, a base ChromaDB e as dependências do projeto."
                )
                st.error(mensagem_erro)
                st.exception(erro)
