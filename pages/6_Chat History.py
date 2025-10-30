import streamlit as st
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("database/chathistory.db")

# --- PAGE CONFIG ---
st.set_page_config(page_title="💬 Saved Conversations", page_icon="💾", layout="centered")

# --- LOGIN PROTECTION ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please log in or create an account to access this page.")
    st.stop()

user = st.session_state["user"]
user_email = user["email"]

st.title("💬 Saved Conversations")
st.caption("Browse your previous AI-assisted trip planning chats — or delete old ones.")

# --- DATABASE SETUP ---
DB_PATH = Path("database/chathistory.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_chat_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            name TEXT,
            chat_history TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user_conversations(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, chat_history FROM conversations WHERE user_email=? ORDER BY id DESC", (email,))
    data = c.fetchall()
    conn.close()
    return data

def delete_conversation(convo_id, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE id=? AND user_email=?", (convo_id, email))
    conn.commit()
    conn.close()

# --- INIT DATABASE ---
init_chat_db()

# --- DISPLAY USER CONVERSATIONS ---
convos = get_user_conversations(user_email)

if not convos:
    st.info("💡 No saved conversations yet. Try chatting with the AI first.")
else:
    for convo_id, name, chat_json in convos:
        col1, col2 = st.columns([8, 1])
        with col1:
            expander = st.expander(f"🗓️ {name}", expanded=False)
        with col2:
            if st.button("🗑️", key=f"del_{convo_id}", help="Delete this conversation"):
                delete_conversation(convo_id, user_email)
                st.success(f"✅ Deleted: {name}")
                st.rerun()

        # Inside expander: display chat messages
        with expander:
            chat = json.loads(chat_json)
            for msg in chat:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}**")
                else:
                    st.markdown(f"**🤖 AI:** {msg['content']}**")

# --- SIDEBAR (Logout) ---
st.sidebar.markdown(f"👋 **{user['firstname']} {user['lastname']}**")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user"] = {}
    st.experimental_rerun()
