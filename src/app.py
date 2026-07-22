"""
Chat web con Streamlit para el agente de Mercado Central 24h,
con una estética estilo WhatsApp (header verde, burbujas de mensaje,
fondo tipo "wallpaper", hora y check de leído) aplicada sobre los
componentes nativos de Streamlit (st.chat_message / st.chat_input),
para no entrar en conflicto con su layout, scroll ni funcionalidad.
Ejecutar con: streamlit run src/app.py
"""
import html
from datetime import datetime
import streamlit as st
from agent import MercadoCentralAgent

st.set_page_config(
    page_title="Mercado Central 24h · Asistente IA",
    page_icon="🛒",
    layout="centered",
)

# ---------------------------------------------------------------------------
# ESTILOS — estética WhatsApp aplicada SOLO por encima de los componentes
# nativos de Streamlit (st.chat_message, st.chat_input), usando los
# atributos data-testid oficiales. No se oculta el menú nativo de
# Streamlit ni se reemplaza su estructura de layout.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --wa-green-dark: #075E54;
        --wa-green: #008069;
        --wa-green-light: #25D366;
        --wa-bubble-out: #D9FDD3;
        --wa-bubble-in: #FFFFFF;
        --wa-bg: #E5DDD5;
        --wa-text: #111B21;
        --wa-text-secondary: #667781;
        --wa-check-blue: #53BDEB;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
            Arial, sans-serif !important;
    }

    /* Fondo tipo "wallpaper" del chat: patrón sutil de rombos sobre beige,
       como el fondo clásico de WhatsApp */
    .stApp {
        background-color: var(--wa-bg) !important;
        background-image:
            linear-gradient(45deg, rgba(0,0,0,0.025) 25%, transparent 25%),
            linear-gradient(-45deg, rgba(0,0,0,0.025) 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, rgba(0,0,0,0.025) 75%),
            linear-gradient(-45deg, transparent 75%, rgba(0,0,0,0.025) 75%);
        background-size: 24px 24px;
        background-position: 0 0, 0 12px, 12px -12px, -12px 0px;
    }

    /* Solo oculta el watermark "Made with Streamlit"; el menú (⋮) con
       "Clear cache" / "Reboot" del propio Streamlit queda intacto */
    footer {visibility: hidden;}

    .block-container {
        padding-top: 0 !important;
        max-width: 640px;
    }

    /* ---------- Header verde estilo WhatsApp ---------- */
    .wa-header {
        display: flex;
        align-items: center;
        gap: 12px;
        background: var(--wa-green-dark);
        padding: 14px 16px;
        margin: 0 -1rem 12px -1rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .wa-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }
    .wa-header-text { flex-grow: 1; }
    .wa-header-text h1 {
        font-size: 16.5px;
        font-weight: 600;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.25;
    }
    .wa-header-text p {
        font-size: 12.5px;
        color: rgba(255,255,255,0.85);
        margin: 0;
    }
    .wa-header-icons {
        display: flex;
        gap: 18px;
        font-size: 18px;
        color: #FFFFFF;
        opacity: 0.9;
    }

    /* ---------- Aviso tipo mensaje de sistema (cifrado, en WhatsApp) ---------- */
    .wa-system-banner {
        text-align: center;
        color: #5B6B73;
        font-size: 12px;
        background: #FFF3C4;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px auto 16px auto;
        max-width: 92%;
        line-height: 1.4;
    }

    /* ---------- Burbujas: se reskinnea st.chat_message sin tocar su
       estructura ni su posicionamiento ---------- */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 2px 0 !important;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    [data-testid="stChatMessageContent"] {
        background: var(--wa-bubble-in);
        border-radius: 8px;
        padding: 7px 9px 6px 9px !important;
        font-size: 14.5px;
        color: var(--wa-text);
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
        max-width: 82%;
        margin-left: 0;
    }
    /* Mensajes del usuario (identificados por su avatar nativo) van en
       verde y alineados a la derecha, como los mensajes salientes */
    div:has(> [data-testid="stChatMessageAvatarUser"]) {
        display: flex;
        justify-content: flex-end;
    }
    div:has(> [data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--wa-bubble-out);
        margin-left: auto;
        margin-right: 0;
    }

    .wa-meta {
        display: block;
        text-align: right;
        font-size: 11px;
        color: var(--wa-text-secondary);
        margin-top: 2px;
        white-space: nowrap;
    }
    .wa-check { color: var(--wa-check-blue); font-weight: bold; }

    /* ---------- Input de chat: solo redondeo, sin tocar su estructura ---------- */
    [data-testid="stChatInput"] textarea {
        border-radius: 20px !important;
        background: #FFFFFF !important;
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
    <div class="wa-header">
        <div class="wa-avatar">🛒</div>
        <div class="wa-header-text">
            <h1>Mercado Central 24h</h1>
            <p>en línea</p>
        </div>
        <div class="wa-header-icons">
            <span>📹</span><span>📞</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="wa-system-banner">
        🔒 Estás hablando con un agente de inteligencia artificial, no con
        una persona. Las respuestas se generan a partir de documentos
        oficiales de Mercado Central 24h.
    </div>
    """,
    unsafe_allow_html=True,
)


def render_message_html(text: str, time_str: str, outgoing: bool) -> str:
    """Construye el HTML interno de una burbuja: texto + hora (+ check si
    es un mensaje del usuario), imitando el pie de los mensajes de WhatsApp."""
    safe_text = html.escape(text).replace("\n", "<br>")
    check = '<span class="wa-check">✓✓</span> ' if outgoing else ""
    return f'{safe_text}<span class="wa-meta">{check}{time_str}</span>'


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
        st.markdown(
            render_message_html(turn["question"], turn["time"], outgoing=True),
            unsafe_allow_html=True,
        )
    with st.chat_message("assistant"):
        st.markdown(
            render_message_html(turn["answer"], turn["time"], outgoing=False),
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# ENTRADA DE CHAT
# ---------------------------------------------------------------------------
question = st.chat_input("Escribe un mensaje...")

if question:
    now = datetime.now().strftime("%H:%M")

    with st.chat_message("user"):
        st.markdown(render_message_html(question, now, outgoing=True), unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Escribiendo..."):
            result = agent.ask(question)
        st.markdown(render_message_html(result["answer"], now, outgoing=False), unsafe_allow_html=True)

    st.session_state.history.append({
        "question": question,
        "answer": result["answer"],
        "time": now,
    })
