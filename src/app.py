"""
Chat web con Streamlit para el agente de Mercado Central 24h,
con una interfaz estilizada al estilo iOS (Mensajes).
Ejecutar con: streamlit run src/app.py
"""
import html
import streamlit as st
from agent import MercadoCentralAgent

st.set_page_config(
    page_title="Mercado Central 24h · Asistente IA",
    page_icon="🛒",
    layout="centered",
)

# ---------------------------------------------------------------------------
# ESTILOS — estética iOS (Mensajes / Ajustes): tipografía de sistema, azul
# #007AFF, fondo gris de sistema, burbujas asimétricas, input tipo "pill".
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --ios-blue: #007AFF;
        --ios-blue-dark: #0A63C9;
        --ios-bg: #F2F2F7;
        --ios-card: #FFFFFF;
        --ios-bubble-assistant: #E9E9EB;
        --ios-text: #1C1C1E;
        --ios-text-secondary: #8E8E93;
        --ios-separator: #E5E5EA;
        --ios-green: #34C759;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
            "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    .stApp {
        background: var(--ios-bg) !important;
    }

    /* Oculta el header/menu por defecto de Streamlit para que se sienta
       como una app nativa, sin "chrome" de navegador */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    #MainMenu, footer {visibility: hidden;}

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
        max-width: 640px;
    }

    /* ---------- Encabezado tipo "contacto" de Mensajes ---------- */
    .ios-header {
        display: flex;
        align-items: center;
        gap: 12px;
        background: var(--ios-card);
        border-radius: 20px;
        padding: 14px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .ios-avatar {
        width: 46px;
        height: 46px;
        border-radius: 50%;
        background: linear-gradient(180deg, var(--ios-blue) 0%, var(--ios-blue-dark) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .ios-header-text h1 {
        font-size: 17px;
        font-weight: 600;
        color: var(--ios-text);
        margin: 0;
        line-height: 1.2;
    }
    .ios-header-text p {
        font-size: 13px;
        color: var(--ios-text-secondary);
        margin: 2px 0 0 0;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .ios-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--ios-green);
        display: inline-block;
    }

    /* ---------- Banner informativo tipo "mensaje del sistema" ---------- */
    .ios-system-banner {
        text-align: center;
        color: var(--ios-text-secondary);
        font-size: 12px;
        background: rgba(142,142,147,0.12);
        border-radius: 14px;
        padding: 8px 14px;
        margin: 10px auto 18px auto;
        max-width: 90%;
        line-height: 1.4;
    }

    /* ---------- Burbujas de chat ---------- */
    .ios-row {
        display: flex;
        margin: 6px 0;
        width: 100%;
    }
    .ios-row.user { justify-content: flex-end; }
    .ios-row.assistant { justify-content: flex-start; }

    .ios-bubble {
        max-width: 78%;
        padding: 10px 14px;
        font-size: 15.5px;
        line-height: 1.42;
        word-wrap: break-word;
        box-shadow: 0 1px 1px rgba(0,0,0,0.03);
    }
    .ios-bubble.user {
        background: var(--ios-blue);
        color: #FFFFFF;
        border-radius: 18px 18px 4px 18px;
    }
    .ios-bubble.assistant {
        background: var(--ios-bubble-assistant);
        color: var(--ios-text);
        border-radius: 18px 18px 18px 4px;
    }
    .ios-bubble a { color: inherit; text-decoration: underline; }

    /* ---------- Fuentes (expander) con look de lista iOS ---------- */
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
        max-width: 78%;
        margin: 2px 0 10px auto;
        background: transparent !important;
    }
    div[data-testid="stExpander"] details {
        background: var(--ios-card);
        border-radius: 14px;
        border: 1px solid var(--ios-separator);
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-size: 12.5px !important;
        color: var(--ios-blue) !important;
        font-weight: 500;
        padding: 8px 12px !important;
    }
    .ios-source-item {
        font-size: 12.5px;
        color: var(--ios-text-secondary);
        padding: 6px 12px;
        border-top: 1px solid var(--ios-separator);
    }
    .ios-source-item b { color: var(--ios-text); font-weight: 500; }

    /* ---------- Input inferior tipo "pill" ---------- */
    [data-testid="stChatInput"] {
        background: var(--ios-bg) !important;
        border-top: none !important;
    }
    [data-testid="stChatInput"] > div {
        background: var(--ios-card) !important;
        border-radius: 22px !important;
        border: 1px solid var(--ios-separator) !important;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.03);
    }
    [data-testid="stChatInputSubmitButton"] button {
        background: var(--ios-blue) !important;
        border-radius: 50% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_bubble(role: str, text: str):
    """Renderiza un mensaje como burbuja estilo iOS (texto ya escapado)."""
    safe_text = html.escape(text).replace("\n", "<br>")
    st.markdown(
        f'<div class="ios-row {role}"><div class="ios-bubble {role}">{safe_text}</div></div>',
        unsafe_allow_html=True,
    )


def render_sources(sources: list):
    if not sources:
        return
    with st.expander("📄 Fuentes utilizadas"):
        for s in sources:
            st.markdown(
                f'<div class="ios-source-item"><b>{html.escape(s["file"])}</b> '
                f'— pág/fila {s["location"]} · score {s["score"]}</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="ios-header">
        <div class="ios-avatar">🛒</div>
        <div class="ios-header-text">
            <h1>Mercado Central 24h</h1>
            <p><span class="ios-dot"></span> Asistente IA · En línea</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ios-system-banner">
        🤖 Estás hablando con un agente de inteligencia artificial, no con
        una persona. Las respuestas se generan a partir de documentos
        oficiales de Mercado Central 24h.
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_agent():
    return MercadoCentralAgent()


agent = load_agent()

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------------------------------------------------
# HISTORIAL DE CONVERSACIÓN
# ---------------------------------------------------------------------------
for turn in st.session_state.history:
    render_bubble("user", turn["question"])
    render_bubble("assistant", turn["answer"])
    render_sources(turn["sources"])

# ---------------------------------------------------------------------------
# ENTRADA DE CHAT
# ---------------------------------------------------------------------------
question = st.chat_input("Escribe tu pregunta sobre productos, horarios o políticas...")

if question:
    render_bubble("user", question)
    with st.spinner("Respondiendo..."):
        result = agent.ask(question)
    render_bubble("assistant", result["answer"])
    render_sources(result["sources"])

    st.session_state.history.append({
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
    })
