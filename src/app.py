"""
Chat web simple con Streamlit para el agente de Mercado Central 24h.
Ejecutar con: streamlit run src/app.py
"""
import streamlit as st
from agent import MercadoCentralAgent

st.set_page_config(page_title="Mercado Central 24h · Asistente IA", page_icon="🛒")

st.title("🛒 Asistente Virtual — Mercado Central 24h")
st.caption(
    "Agente de IA (RAG) que responde preguntas sobre horarios, devoluciones, "
    "productos y políticas del supermercado. Modelo: Cohere (command-a-03-2025)."
)
st.info(
    "🤖 Estás hablando con un agente de inteligencia artificial, no con una "
    "persona. Las respuestas se generan a partir de documentos oficiales.",
    icon="ℹ️",
)


@st.cache_resource
def load_agent():
    return MercadoCentralAgent()


agent = load_agent()

if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        if turn["sources"]:
            with st.expander("📄 Fuentes utilizadas"):
                for s in turn["sources"]:
                    st.markdown(f"- **{s['file']}** (pág/fila {s['location']}, score {s['score']})")

question = st.chat_input("Escribe tu pregunta sobre productos, horarios o políticas...")

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            result = agent.ask(question)
        st.write(result["answer"])
        if result["sources"]:
            with st.expander("📄 Fuentes utilizadas"):
                for s in result["sources"]:
                    st.markdown(f"- **{s['file']}** (pág/fila {s['location']}, score {s['score']})")

    st.session_state.history.append({
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
    })
