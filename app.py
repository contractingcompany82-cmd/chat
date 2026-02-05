import streamlit as st
from google.cloud import firestore
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="Community Messenger", page_icon="💬", layout="centered")

# 2. Custom CSS (Modern Facebook Style UI)
st.markdown("""
    <style>
    /* Background and Font */
    .stApp {
        background-color: #f0f2f5;
    }
    /* Header Style */
    .chat-header {
        background-color: #1877f2;
        color: white;
        padding: 15px;
        border-radius: 0px 0px 15px 15px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        margin-top: -60px; /* Fixing Streamlit padding */
    }
    /* Message styling */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        margin-bottom: 8px;
        border: 1px solid #e4e6eb;
    }
    /* Hide Streamlit top bar decorations */
    header {visibility: hidden;}
    </style>
    <div class="chat-header">
        Messenger Lite
    </div>
    """, unsafe_allow_html=True)

# 3. Auto Refresh (Har 3 seconds mein)
st_autorefresh(interval=3000, key="chat_refresh")

# 4. Firebase Setup
db = firestore.Client.from_service_account_info(st.secrets["firebase"])

# 5. Sidebar (Profile Section)
with st.sidebar:
    st.title("👤 User Profile")
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    user_name = st.text_input("Apna Naam Likhein:", value=st.session_state.username)
    if user_name:
        st.session_state.username = user_name

    st.divider()
    if st.button("🗑️ Clear My Chat View"):
        st.rerun()

# 6. Chat Logic
if not st.session_state.username:
    st.info("👈 Please enter your name in the sidebar to start chatting.")
    st.stop()

# Input Box (Bottom fixed)
chat_input = st.chat_input("Aaapka message...")
if chat_input:
    db.collection("messages").add({
        "name": st.session_state.username,
        "text": chat_input,
        "timestamp": datetime.now()
    })

# 7. Messages Display (ASCENDING: Naya niche aayega)
messages = db.collection("messages").order_by("timestamp", direction=firestore.Query.ASCENDING).stream()

for msg in messages:
    m = msg.to_dict()
    # Identifiers
    is_me = m["name"] == st.session_state.username
    
    with st.chat_message("user" if is_me else "assistant"):
        st.markdown(f"**{m['name']}**")
        st.markdown(f"{m['text']}")
