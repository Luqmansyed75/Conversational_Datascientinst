import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataBot | AI Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS — Matches Stitch Design Exactly ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

/* ── Global Styles ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0a0a0a !important;
    color: #e5e2e1 !important;
}

#MainMenu, header, footer { visibility: hidden; }
.block-container { 
    padding-top: 1rem !important; 
    padding-bottom: 0 !important; 
    max-width: 100% !important; 
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1c1b1b !important;
    border-right: 1px solid #59413d !important;
}
[data-testid="stSidebar"] section { 
    padding: 1.5rem 0.75rem !important; 
}

/* ── New Chat Button ── */
div[data-testid="stButton"] button {
    background: linear-gradient(to right, #c0392b, #7b0000) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}
div[data-testid="stButton"] button:hover {
    box-shadow: 0 0 15px rgba(192, 57, 43, 0.45) !important;
    transform: scale(0.98) !important;
}

/* ── Sidebar History Items ── */
.thread-btn button {
    background: transparent !important;
    color: #c8c6c5 !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    padding: 10px 12px !important;
    margin-bottom: 4px !important;
}
.thread-btn button:hover {
    background-color: #2a2a2a !important;
    color: #e5e2e1 !important;
}
.thread-btn-active button {
    background: #201f1f !important;
    color: #e5e2e1 !important;
    border-left: 3px solid #c0392b !important;
    border-radius: 0 8px 8px 0 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 12px !important;
    margin-bottom: 4px !important;
}

/* ── Main Canvas Background ── */
.main { background-color: #0e0e0e !important; }
section.main > div { background-color: #0e0e0e !important; }

/* ── Chat Messages Styling ── */
[data-testid="stChatMessage"] {
    border-radius: 18px !important;
    padding: 6px !important;
    margin-bottom: 12px !important;
    background: transparent !important;
}

/* User Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stChatMessageContent {
    background-color: #c0392b !important;
    border-radius: 18px 18px 4px 18px !important;
    color: #ffffff !important;
    padding: 14px 18px !important;
    max-width: 80% !important;
    margin-left: auto !important;
    box-shadow: 0 4px 12px rgba(192, 57, 43, 0.2) !important;
}

/* Assistant Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stChatMessageContent {
    background-color: #201f1f !important;
    border: 1px solid #353534 !important;
    border-radius: 18px 18px 18px 4px !important;
    color: #e5e2e1 !important;
    padding: 14px 18px !important;
    max-width: 85% !important;
}

/* ── Bottom Chat Input Styling ── */
[data-testid="stChatInput"] textarea {
    background-color: #1a1a1a !important;
    border: 1px solid #59413d !important;
    border-radius: 9999px !important;
    color: #e5e2e1 !important;
    font-family: 'Inter', sans-serif !important;
    padding-left: 20px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #c0392b !important;
    box-shadow: 0 0 15px rgba(192, 57, 43, 0.3) !important;
}
[data-testid="stChatInput"] {
    background-color: #0e0e0e !important;
    border-top: 1px solid #1c1b1b !important;
    padding: 16px 24px !important;
}

/* ── Custom Dark Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background-color: #333; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background-color: #c0392b; }

/* ── Welcome Screen ── */
.welcome-screen {
    display: flex; 
    flex-direction: column;
    align-items: center; 
    justify-content: center;
    height: 65vh; 
    gap: 16px; 
    text-align: center;
}
.welcome-title {
    font-size: 40px; 
    font-weight: 800;
    color: #ffb4a9; 
    letter-spacing: -0.02em;
    font-family: 'Inter', sans-serif;
}
.welcome-sub {
    font-size: 16px; 
    color: #a88a85;
    font-family: 'Inter', sans-serif;
    max-width: 480px;
    line-height: 1.5;
}

/* ── Typing Indicator ── */
.typing-indicator {
    display: flex; 
    align-items: center; 
    gap: 6px;
    padding: 14px 18px; 
    background-color: #201f1f;
    border: 1px solid #353534;
    border-radius: 18px 18px 18px 4px; 
    width: fit-content;
}
.dot {
    width: 8px; 
    height: 8px; 
    background-color: #ffb4a9;
    border-radius: 50%;
    animation: pulse 1.4s infinite ease-in-out both;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
.dot:nth-child(3) { animation-delay: 0s; }

@keyframes pulse {
    0%, 80%, 100% { transform: scale(0.3); opacity: 0.3; }
    40%           { transform: scale(1);   opacity: 1;   }
}
.typing-text {
    font-size: 13px; 
    color: #a88a85;
    font-style: italic; 
    margin-left: 6px;
    font-family: 'Inter', sans-serif;
}

/* ── Chat Header ── */
.chat-header {
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.chat-title {
    color: #ffb4a9; 
    font-family: 'Inter', sans-serif;
    font-weight: 700; 
    font-size: 22px; 
    margin: 0;
}

/* ── History Header ── */
.history-label {
    font-size: 11px; 
    color: #a88a85;
    letter-spacing: 0.12em; 
    text-transform: uppercase;
    padding: 12px 4px 6px; 
    opacity: 0.7;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────
if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "active_thread" not in st.session_state:
    st.session_state.active_thread = None


# ─── API Helpers ──────────────────────────────────────────────────────────────
def api_create_thread() -> str | None:
    try:
        resp = requests.post(f"{API_BASE}/chat/new-thread", timeout=10)
        resp.raise_for_status()
        return resp.json()["thread_id"]
    except Exception as e:
        st.error(f"Could not connect to backend server: {e}")
        return None


def api_ask(question: str, thread_id: str) -> dict:
    try:
        resp = requests.post(
            f"{API_BASE}/chat/ask",
            json={"question": question, "thread_id": thread_id},
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"answer": f"⚠️ Connection error with backend: {e}", "needs_chart": False, "has_chart": False}


# ─── Actions ─────────────────────────────────────────────────────────────────
def start_new_chat():
    thread_id = api_create_thread()
    if thread_id:
        st.session_state.conversations.append({
            "thread_id": thread_id,
            "title":     "New Conversation",
            "messages":  [],
        })
        st.session_state.active_thread = thread_id


def get_active_conv() -> dict | None:
    for conv in st.session_state.conversations:
        if conv["thread_id"] == st.session_state.active_thread:
            return conv
    return None


# ─── Sidebar UI ───────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:2px;">
            <div style="width:36px;height:36px;background:linear-gradient(135deg, #c0392b, #7b0000);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">🤖</div>
            <div>
                <div style="font-size:22px;font-weight:800;color:#ffb4a9;font-family:Inter,sans-serif;line-height:1.1;">DataBot</div>
                <div style="font-size:11px;color:#a88a85;letter-spacing:0.06em;font-family:Inter,sans-serif;margin-top:2px;">AI Engine</div>
            </div>
        </div>
        <div style="height:16px;"></div>
    """, unsafe_allow_html=True)

    # New Chat Button
    if st.button("＋  New Chat", use_container_width=True, key="btn_new_chat"):
        start_new_chat()
        st.rerun()

    st.markdown('<div class="history-label">History</div>', unsafe_allow_html=True)

    # Conversation History List
    for conv in reversed(st.session_state.conversations):
        is_active = conv["thread_id"] == st.session_state.active_thread
        title     = conv["title"]
        label     = (title[:26] + "…") if len(title) > 26 else title
        css_class = "thread-btn-active" if is_active else "thread-btn"

        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(f"💬  {label}", key=f"t_{conv['thread_id']}", use_container_width=True):
            st.session_state.active_thread = conv["thread_id"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ─── Main Area UI ─────────────────────────────────────────────────────────────
active_conv = get_active_conv()

if active_conv is None:
    # Welcome Screen
    st.markdown("""
        <div class="welcome-screen">
            <div style="width:80px;height:80px;background:linear-gradient(135deg, #c0392b, #7b0000);border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:44px;box-shadow:0 0 30px rgba(192, 57, 43, 0.3);">🤖</div>
            <div class="welcome-title">DataBot AI</div>
            <div class="welcome-sub">Your conversational data analyst. Ask questions, analyze sales, or query internal documents.<br/><br/>Click <b>＋ New Chat</b> in the sidebar to start!</div>
        </div>
    """, unsafe_allow_html=True)

else:
    # Chat Header
    st.markdown(f"""
        <div class="chat-header">
            <h1 class="chat-title">{active_conv['title']}</h1>
        </div>
    """, unsafe_allow_html=True)

    # Render Conversation Messages
    if not active_conv["messages"]:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("Hello! I am **DataBot**. How can I assist you with your data today?")

    for msg in active_conv["messages"]:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat Input Box
    if prompt := st.chat_input("Ask me anything about your data..."):

        # Render User Message Immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        active_conv["messages"].append({"role": "user", "content": prompt})

        # Update Conversation Title from First User Message
        if active_conv["title"] == "New Conversation" or len(active_conv["messages"]) == 1:
            active_conv["title"] = prompt[:35]

        # Assistant Thinking / Typing State
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            placeholder.markdown("""
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <span class="typing-text">Processing your request…</span>
                </div>
            """, unsafe_allow_html=True)

            # Call FastAPI Backend Endpoint
            result = api_ask(prompt, active_conv["thread_id"])
            answer = result.get("answer") or "⚠️ No response received from server."

            # Update with Assistant Answer
            placeholder.markdown(answer)

        active_conv["messages"].append({"role": "assistant", "content": answer})
        st.rerun()
