"""
AI Medical Assistant - Streamlit Application
=============================================
Main user interface for the RAG system with full persistent chat history.
Supports both Light and Dark themes seamlessly.
"""

import streamlit as st
import json
import os
from datetime import datetime
from src.rag import RAGOrchestrator
from src.config import DEVICE

# Path to store chat history persistently
HISTORY_FILE = "data/chat_history.json"


# =========================
# Page Configuration
# =========================

st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================
# Theme Detection (FIXED)
# =========================
try:
    _configured_theme = st.get_option("theme.base")
except:
    _configured_theme = None

if _configured_theme:
    st.markdown(
        f'<style>html {{ color-scheme: {_configured_theme} !important; }}</style>',
        unsafe_allow_html=True
    )


# =========================
# Custom CSS (FIXED: Light & Dark Themes)
# =========================

st.markdown(
    """
    <style>
        
    /* --- Main Background --- */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    /* --- Title Styling --- */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 5px;
    }
    
    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #64748b;
        margin-bottom: 30px;
    }
    
    /* --- Chat Container --- */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
    }
    
    /* --- Input Styling --- */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 12px 20px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c3aed;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
    }
    
    /* --- Sidebar Title (FIXED: now visible in both themes) --- */
    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 20px;
        padding: 12px 14px;
        background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
        border-radius: 10px;
        border-left: 4px solid #7c3aed;
    }
    
    /* --- Info Card --- */
    .info-card {
        background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    
    /* --- Status Badge --- */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .status-ready {
        background: #dcfce7;
        color: #166534;
    }
    
    /* --- Footer --- */
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        margin-top: 30px;
    }
    
    /* --- Disclaimer Banner --- */
    .disclaimer-banner {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        background: #fff7ed;
        border: 1px solid #fdba74;
        border-left: 5px solid #ea580c;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }
    .disclaimer-icon {
        font-size: 20px;
        line-height: 1.4;
    }
    .disclaimer-text {
        font-size: 13.5px;
        color: #7c2d12;
        line-height: 1.5;
    }
    .disclaimer-text strong {
        color: #9a3412;
    }
    
    /* ===== Chat History Styling ===== */
    .chat-history-container {
        max-height: 450px;
        overflow-y: auto;
        padding-right: 2px;
        margin-bottom: 10px;
    }
    .chat-history-container::-webkit-scrollbar {
        width: 5px;
    }
    .chat-history-container::-webkit-scrollbar-track {
        background: transparent;
    }
    .chat-history-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    .chat-item {
        position: relative;
        padding: 10px 35px 10px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s ease;
        margin-bottom: 4px;
        border: 1px solid transparent;
        min-height: 48px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .chat-item:hover {
        background: #f1f5f9;
    }
    .chat-item.active {
        background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
        border-color: #818cf8;
        box-shadow: 0 1px 3px rgba(99, 102, 241, 0.1);
    }
    .chat-item-title {
        font-size: 13px;
        color: #1e293b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 500;
        line-height: 1.4;
    }
    .chat-item.active .chat-item-title {
        color: #4338ca;
        font-weight: 600;
    }
    .chat-item-meta {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 2px;
    }
    .chat-item-delete {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0;
        transition: opacity 0.15s;
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px 6px;
        border-radius: 4px;
        font-size: 12px;
        color: #64748b;
        line-height: 1;
    }
    .chat-item:hover .chat-item-delete {
        opacity: 1;
    }
    .chat-item-delete:hover {
        background: #fee2e2;
        color: #dc2626;
    }
    .empty-history {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        padding: 30px 15px;
        line-height: 1.6;
    }
    .empty-history-icon {
        font-size: 32px;
        margin-bottom: 8px;
        opacity: 0.5;
    }
    
    /* --- Session Header in Sidebar --- */
    .session-header {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 10px;
        background: #f8fafc;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 12px;
        color: #64748b;
        border: 1px solid #e2e8f0;
    }
    .session-header-id {
        font-family: monospace;
        font-weight: 600;
        color: #475569;
    }
    
    /* --- New Chat Button --- */
    .new-chat-btn > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    .new-chat-btn > button:hover {
        opacity: 0.9 !important;
    }
    
    /* ====================================================
       DARK MODE OVERRIDES (FIXED)
       ==================================================== */
    
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }
        .main-title {
            background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            color: #94a3b8;
        }
        .stTextInput > div > div > input {
            border-color: #334155;
            background-color: #1e293b;
            color: #e2e8f0;
        }
        .stTextInput > div > div > input:focus {
            border-color: #818cf8;
            box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2);
        }
        .sidebar-title {
            color: #f1f5f9 !important;
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            border-left: 4px solid #818cf8;
        }
        .info-card {
            background: linear-gradient(135deg, #1e293b 0%, #1e1b4b 100%);
            border: 1px solid #334155;
            color: #cbd5e1;
        }
        .status-ready {
            background: #14532d;
            color: #86efac;
        }
        .disclaimer-banner {
            background: #431407;
            border: 1px solid #9a3412;
            border-left: 5px solid #ea580c;
        }
        .disclaimer-text {
            color: #fed7aa;
        }
        .disclaimer-text strong {
            color: #fdba74;
        }
        .chat-history-container::-webkit-scrollbar-thumb {
            background: #475569;
        }
        .chat-item:hover {
            background: #1e293b;
        }
        .chat-item.active {
            background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
            border-color: #6366f1;
        }
        .chat-item-title {
            color: #e2e8f0;
        }
        .chat-item.active .chat-item-title {
            color: #a5b4fc;
        }
        .chat-item-delete:hover {
            background: #7f1d1d;
            color: #fca5a5;
        }
        .empty-history {
            color: #64748b;
        }
        .session-header {
            background: #0f172a;
            border: 1px solid #334155;
            color: #94a3b8;
        }
        .session-header-id {
            color: #cbd5e1;
        }
    } /* end @media dark */
    
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# JSON Persistence Helpers
# =========================

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def load_history_from_file():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for session_id, chats in data.items():
                for chat_id, chat_data in chats.items():
                    if "created_at" in chat_data and isinstance(chat_data["created_at"], str):
                        chat_data["created_at"] = datetime.fromisoformat(chat_data["created_at"])
                    if "updated_at" in chat_data and isinstance(chat_data["updated_at"], str):
                        chat_data["updated_at"] = datetime.fromisoformat(chat_data["updated_at"])
            return data
        except Exception as e:
            print(f"Error loading chat history from file: {e}")
            return {}
    return {}

def persist_history():
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.all_chats_history, f, cls=DateTimeEncoder, indent=2)
    except Exception as e:
        print(f"Error saving chat history to file: {e}")


# =========================
# Helper Functions
# =========================

def generate_chat_id():
    import uuid
    return f"chat_{uuid.uuid4().hex[:8]}"

def set_current_chat(chat_id):
    """Switch the active chat and clear the sidebar radio's cached
    selection ("chat_selector") so it doesn't snap back to whatever
    chat was previously selected on the next rerun."""
    st.session_state.current_chat_id = chat_id
    st.session_state.pop("chat_selector", None)

def get_chat_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            title = msg["content"].strip()
            for prefix in ["what are", "what is", "how to", "can you", "tell me", "show me"]:
                if title.lower().startswith(prefix):
                    title = title[len(prefix):].strip()
                    if title:
                        title = title[0].upper() + title[1:]
                    break
            if len(title) > 45:
                title = title[:42] + "..."
            return title if title else "New Chat"
    return "New Chat"

def format_time(timestamp):
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except:
            return ""
    now = datetime.now()
    diff = now - timestamp
    if diff.days == 0:
        return timestamp.strftime("%I:%M %p")
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return timestamp.strftime("%A")
    else:
        return timestamp.strftime("%b %d")

def get_message_count_text(messages):
    count = len(messages)
    if count == 0:
        return "Empty"
    user_msgs = sum(1 for m in messages if m["role"] == "user")
    return f"{user_msgs} message{'s' if user_msgs != 1 else ''}"


# =========================
# Session State Initialization
# =========================

if "all_chats_history" not in st.session_state:
    st.session_state.all_chats_history = load_history_from_file()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = generate_chat_id()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "user_session_1"


# =========================
# Chat History Management
# =========================

def get_current_session_history():
    session_id = st.session_state.session_id
    if session_id not in st.session_state.all_chats_history:
        st.session_state.all_chats_history[session_id] = {}
    return st.session_state.all_chats_history[session_id]

def save_current_chat():
    session_id = st.session_state.session_id
    chat_id = st.session_state.current_chat_id
    messages = st.session_state.messages
    
    if session_id not in st.session_state.all_chats_history:
        st.session_state.all_chats_history[session_id] = {}
    
    if not messages:
        if chat_id in st.session_state.all_chats_history[session_id]:
            del st.session_state.all_chats_history[session_id][chat_id]
        persist_history()
        return
    
    now = datetime.now()
    st.session_state.all_chats_history[session_id][chat_id] = {
        "title": get_chat_title(messages),
        "messages": messages.copy(),
        "created_at": now,
        "updated_at": now
    }
    persist_history()

def load_chat(chat_id):
    session_id = st.session_state.session_id
    if session_id not in st.session_state.all_chats_history:
        return False
    if chat_id not in st.session_state.all_chats_history[session_id]:
        return False
    
    chat_data = st.session_state.all_chats_history[session_id][chat_id]
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = chat_data["messages"].copy()
    
    if rag_system:
        restore_rag_memory(chat_data["messages"])
    return True

def restore_rag_memory(messages):
    if not rag_system or not messages:
        return
    try:
        rag_system.clear_session(st.session_state.session_id)
        for i in range(len(messages)):
            msg = messages[i]
            if msg["role"] in ["human", "user"]:
                ai_response = ""
                if i + 1 < len(messages) and messages[i + 1]["role"] == "assistant":
                    ai_response = messages[i + 1]["content"]
                if hasattr(rag_system, 'memory') and rag_system.memory:
                    rag_system.memory.save_context({"input": msg["content"]}, {"output": ai_response})
                elif hasattr(rag_system, 'chain') and hasattr(rag_system.chain, 'memory'):
                    rag_system.chain.memory.save_context({"input": msg["content"]}, {"output": ai_response})
    except Exception as e:
        print(f"Warning: Could not fully restore RAG memory: {e}")

def delete_chat(chat_id):
    session_id = st.session_state.session_id
    if session_id in st.session_state.all_chats_history:
        if chat_id in st.session_state.all_chats_history[session_id]:
            del st.session_state.all_chats_history[session_id][chat_id]
            if st.session_state.current_chat_id == chat_id:
                set_current_chat(generate_chat_id())
                st.session_state.messages = []
                if rag_system:
                    rag_system.clear_session(st.session_state.session_id)
            persist_history()

def start_new_chat():
    save_current_chat()
    set_current_chat(generate_chat_id())
    st.session_state.messages = []
    if rag_system:
        rag_system.clear_session(st.session_state.session_id)

def switch_session(new_session_id):
    old_session_id = st.session_state.session_id
    save_current_chat()
    if rag_system and old_session_id != new_session_id:
        try:
            rag_system.clear_session(old_session_id)
        except:
            pass
    st.session_state.session_id = new_session_id
    set_current_chat(generate_chat_id())
    st.session_state.messages = []


# =========================
# Header & Disclaimer
# =========================

st.markdown(
    """
    <div class="main-title">🩺 AI Medical Assistant</div>
    <div class="subtitle">Ask medical questions and get AI-powered answers based on trusted medical documents.</div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="disclaimer-banner">
        <div class="disclaimer-icon">⚠️</div>
        <div class="disclaimer-text">
            <strong>Not a substitute for professional medical advice.</strong>
            This assistant provides information generated from a limited set of reference
            documents and may be incomplete, outdated, or inaccurate. Always consult a licensed physician.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# Initialize RAG System
# =========================

@st.cache_resource
def load_rag_system() -> RAGOrchestrator:
    with st.spinner("Initializing AI Medical Assistant..."):
        rag = RAGOrchestrator.from_data_directory()
    return rag

rag_system = None
load_error = None

try:
    rag_system = load_rag_system()
except Exception as e:
    load_error = str(e)

if load_error:
    st.error(f"❌ Error loading RAG system:\n\n{load_error}")
    st.info("Please check your data directory and try again.")
    st.stop()

if rag_system:
    st.markdown('<span class="status-badge status-ready">🟢 System Ready</span>', unsafe_allow_html=True)


# =========================
# Display Chat Messages
# =========================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =========================
# Unified User Input & Example Questions (FIXED)
# =========================

user_question = st.chat_input(placeholder="Type your question here... (e.g., What are the symptoms of COVID-19?)")
st.caption("⚠️ AI-generated answers may be incomplete or inaccurate — not a substitute for professional medical advice.")

# Intercept question if clicked from the sidebar examples
if "example_question" in st.session_state:
    user_question = st.session_state.pop("example_question")

# Unified processing whether from chat_input or sidebar button
if user_question and rag_system:
    if not user_question.strip():
        st.warning("Please enter a valid question.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_question})

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("🧠 Analyzing medical information..."):
                try:
                    response = rag_system.run(
                        question=user_question,
                        session_id=st.session_state.session_id,
                    )
                except Exception as e:
                    response = f"❌ Error while generating answer:\n\n```\n{str(e)}\n```"
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_current_chat()


# =========================
# Sidebar
# =========================

with st.sidebar:
    
    st.markdown('<div class="sidebar-title">🩺 Medical AI</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()
    
    st.markdown(
        f'''
        <div class="session-header">
            👤 <span class="session-header-id">{st.session_state.session_id}</span>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    st.markdown("### 💬 Chats")
    current_session_chats = get_current_session_history()

    sorted_chats = sorted(
        current_session_chats.items(),
        key=lambda x: x[1].get("updated_at", datetime.now()),
        reverse=True
    )

    chat_ids_list = []
    chat_labels_list = []

    # If the active chat hasn't been saved yet (e.g. right after hitting
    # "New Chat"), give it its own entry so the selector always has a
    # valid, matching option instead of falling back to a different,
    # older chat.
    if st.session_state.current_chat_id not in current_session_chats:
        chat_ids_list.append(st.session_state.current_chat_id)
        chat_labels_list.append("📝 New chat\nUnsaved")

    for chat_id, chat_data in sorted_chats:
        is_active = chat_id == st.session_state.current_chat_id
        icon = "💬" if is_active else "○"
        title = chat_data['title']
        time_str = format_time(chat_data["updated_at"])
        msg_count = get_message_count_text(chat_data["messages"])

        label = f"{icon} {title}\n📝 {time_str} · {msg_count}"
        chat_ids_list.append(chat_id)
        chat_labels_list.append(label)

    if chat_ids_list:
        # Options are the actual chat IDs (not positions), so the selection
        # stays correct even when the list gets re-sorted, e.g. as soon as
        # you send a new message in a re-opened chat and it jumps to the top.
        chat_label_map = dict(zip(chat_ids_list, chat_labels_list))

        selected_chat_id = st.radio(
            "Select chat",
            options=chat_ids_list,
            format_func=lambda cid: chat_label_map[cid],
            index=chat_ids_list.index(st.session_state.current_chat_id),
            label_visibility="collapsed",
            key="chat_selector"
        )

        if selected_chat_id != st.session_state.current_chat_id:
            load_chat(selected_chat_id)
            st.rerun()

        st.caption(f"📝 {len(current_session_chats)} chat(s) saved")

        st.divider()
        if st.button("🗑️ Delete Selected Chat", use_container_width=True, type="secondary"):
            if selected_chat_id in current_session_chats:
                delete_chat(selected_chat_id)
                st.rerun()
            else:
                st.info("This chat hasn't been saved yet — nothing to delete.")
    else:
        st.markdown(
            '''
            <div class="empty-history">
                <div class="empty-history-icon">💬</div>
                No conversations yet.<br>
                Start by asking a question!
            </div>
            ''',
            unsafe_allow_html=True
        )
    
    st.divider()
    
    with st.expander("🔑 Change Session", expanded=False):
        st.caption("Changing session switches to a different user context")
        new_session = st.text_input("Session ID:", value=st.session_state.session_id, key="session_input", label_visibility="collapsed")
        if new_session and new_session != st.session_state.session_id:
            switch_session(new_session)
            st.success(f"Switched to: {new_session}")
            st.rerun()
        if st.button("🎲 Random New Session", use_container_width=True):
            import uuid
            switch_session(f"session_{uuid.uuid4().hex[:8]}")
            st.rerun()
    
    st.divider()
    
    with st.expander("⚠️ Danger Zone", expanded=False):
        if st.button("🗑️ Clear Current Chat (Don't Save)", use_container_width=True):
            delete_chat(st.session_state.current_chat_id)
            st.rerun()
        if st.button("🧹 Delete ALL Chats in Session", use_container_width=True):
            if st.session_state.session_id in st.session_state.all_chats_history:
                st.session_state.all_chats_history[st.session_state.session_id] = {}
            set_current_chat(generate_chat_id())
            st.session_state.messages = []
            if rag_system:
                rag_system.clear_session(st.session_state.session_id)
            persist_history()
            st.rerun()
        if st.button("♻️ Rebuild Knowledge Base", use_container_width=True):
            with st.spinner("Rebuilding..."):
                from src.retriever import RetrieverManager
                RetrieverManager().clear(delete_cache=True)
                load_rag_system.clear()
            st.success("Done! Reloading...")
            st.rerun()
    
    st.divider()
    
    # --- Example Questions ---
    with st.expander("💡 Example Questions", expanded=False):
        example_questions = [
            "Show me patient records with diabetes",
            "What are the symptoms of COVID-19?",
            "What medications are used for hypertension?",
            "What is the treatment for severe COVID-19?",
            "What are the risk factors for heart disease?",
            "Show me patients with cancer admitted urgently",
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}"):
                st.session_state.example_question = question
                st.rerun()
    
    with st.expander("ℹ️ System Info", expanded=False):
        st.markdown(
            f"""
            <div class="info-card">
                <strong>🔍 Components:</strong><br><br>
                ✔ RAG System<br>
                ✔ Medical Knowledge Base<br>
                ✔ Groq LLM API<br>
                ✔ FAISS Vector Search<br>
                ✔ Conversation Memory<br>
                ✔ Persistent Chat History (JSON)<br>
                <br>
                <strong>💻 Device:</strong> {DEVICE.upper()}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown(
        """
        ---
        <div class="footer">
            AI Medical Assistant v1.1<br>
            Built with RAG, LangChain & Groq
        </div>
        """,
        unsafe_allow_html=True
    )