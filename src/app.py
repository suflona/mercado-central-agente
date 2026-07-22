"""
Chat web con Streamlit para el agente de Mercado Central 24h,
con una estética estilo iOS aplicada sobre los componentes nativos de
Streamlit (st.chat_message / st.chat_input), para no entrar en
conflicto con su layout, scroll ni funcionalidad.
Ejecutar con: streamlit run src/app.py
"""
import streamlit as st
from agent import MercadoCentralAgent

st.set_page_config(
    page_title="Mercado Central 24h · Asistente IA",
    page_icon="🛒",
    layout="centered",
)

# ---------------------------------------------------------------------------
# ESTILOS — estética iOS aplicada SOLO por encima de los componentes nativos
# de Streamlit (st.chat_message, st.chat_input), usando los atributos
# data-testid oficiales. No se oculta el menú nativo de Streamlit ni se
# reemplaza su estructura de layout, para evitar conflictos.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --ios-blue: #007AFF;
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

    /* Solo oculta el watermark "Made with Streamlit"; el menú (⋮) con
       "Clear cache" / "Reboot" queda intacto y accesible */
    footer {visibility: hidden;}

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
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--ios-blue);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
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
        margin: 10px 0 18px 0;
        line-height: 1.4;
    }

    /* ---------- Burbujas: se reskinnea st.chat_message, sin tocar
       su estructura ni su posicionamiento ---------- */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 4px 0 !important;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        background: var(--ios-blue) !important;
    }
    [data-testid="stChatMessageContent"] {
        background: var(--ios-bubble-assistant);
        border-radius: 16px;
        padding: 10px 14px !important;
        font-size: 15.5px;
    }
    /* El mensaje del usuario es el segundo bloque en cada intercambio
       (chat_message se pinta en orden de llamada); usamos su avatar para
       diferenciar el color con :has() (Chrome/Edge/Safari recientes) */
    div:has(> [data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--ios-blue);
        color: #FFFFFF;
    }
    div:has(> [data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] p {
        color: #FFFFFF;
    }

    /* ---------- Input de chat: solo redondeo, sin tocar su estructura ---------- */
    [data-testid="stChatInput"] textarea {
        border-radius: 20px !important;
    }
    </style>
    """,
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
# HISTORIAL DE CONVERSACIÓN (usando st.chat_message nativo)
# ---------------------------------------------------------------------------
for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])

# ---------------------------------------------------------------------------
# ENTRADA DE CHAT
# ---------------------------------------------------------------------------
question = st.chat_input("Escribe tu pregunta sobre productos, horarios o políticas...")

if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Respondiendo..."):
            result = agent.ask(question)
        st.write(result["answer"])

    st.session_state.history.append({
        "question": question,
        "answer": result["answer"],
    })
