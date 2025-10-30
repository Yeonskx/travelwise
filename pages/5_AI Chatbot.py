import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
import json
from datetime import date
from pathlib import Path

DB_PATH = Path("database/chathistory.db")

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Travel Chatbot 🌏", page_icon="🧳", layout="centered")

# --- LOGIN PROTECTION ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please log in or create an account to access this page.")
    st.stop()

user = st.session_state["user"]
user_email = user["email"]

# --- SETUP GEMINI ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# --- DATABASE SETUP ---
DB_PATH = Path("database/chathistory.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
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

def save_conversation(name, chat_history):
    """Save chat history tied to the logged-in user's email."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO conversations (user_email, name, chat_history) VALUES (?, ?, ?)",
        (user_email, name, json.dumps(chat_history))
    )
    conn.commit()
    conn.close()

init_db()

# --- UI HEADER ---
st.title("🧳 AI Travel Chatbot")
st.write("Chat with your AI travel planner to plan your next adventure — powered by Gemini ✈️")

# --- TRIP INPUTS ---
destination = st.text_input("Destination Country", placeholder="e.g., Japan, France, Canada")
trip_date = st.date_input("Trip Date", date.today())

# --- AI CONTEXT ---
system_instruction = """
You are TravelWise — a travel assistant AI.
Only discuss travel-related topics:
- Trip planning, itineraries, and destinations
- Budgeting and expenses
- Flights, transportation, and accommodations
- Food, culture, and local activities
If asked something unrelated to travel, politely refuse.
"""

# --- CHAT INITIALIZATION (user-specific) ---
if f"chat_history_{user_email}" not in st.session_state:
    st.session_state[f"chat_history_{user_email}"] = []
if f"chat_session_{user_email}" not in st.session_state:
    st.session_state[f"chat_session_{user_email}"] = model.start_chat(
        history=[{"role": "user", "parts": [system_instruction]}]
    )

chat_history = st.session_state[f"chat_history_{user_email}"]
chat_session = st.session_state[f"chat_session_{user_email}"]

# --- DISPLAY HISTORY ---
for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- HELPER: Context Filter ---
def is_travel_related(prompt_text):
    check_prompt = f"""
    Determine if this message is travel-related. Respond only with "yes" or "no".
    Message: "{prompt_text}"
    """
    try:
        result = model.generate_content(check_prompt)
        return "yes" in result.text.strip().lower()
    except Exception as e:
        st.error(f"Error checking context: {e}")
        return False

# --- CHAT INPUT ---
user_input = st.chat_input("Ask about your travel plans...")

if user_input:
    # Show user message
    st.chat_message("user").markdown(user_input)
    chat_history.append({"role": "user", "content": user_input})

    # Validate topic
    if is_travel_related(user_input):
        with st.chat_message("assistant"):
            with st.spinner("Thinking... ✈️"):
                try:
                    response = chat_session.send_message(user_input)
                    bot_reply = response.text
                    st.markdown(bot_reply)
                    chat_history.append({"role": "assistant", "content": bot_reply})
                except Exception as e:
                    st.error(f"Error: {e}")

        # Save unique conversation per user
        chat_name = f"{destination.strip() or 'Trip'} — {trip_date.strftime('%Y-%m-%d')}"
        save_conversation(chat_name, chat_history)

    else:
        bot_reply = (
            "🌍 I’m your **AI Travel Assistant**, so I can only help with travel-related topics — "
            "like trip planning, destinations, budgeting, and experiences. Try asking me about your next adventure! ✈️"
        )
        st.chat_message("assistant").markdown(bot_reply)
        chat_history.append({"role": "assistant", "content": bot_reply})

# --- SIDEBAR ---
st.sidebar.markdown(f"👋 **{user['firstname']} {user['lastname']}**")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user"] = {}
    st.experimental_rerun()
