import streamlit as st
from google.cloud import firestore
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="Messenger Lite", page_icon="💬")

# 2. Custom CSS (Visibility Fix)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f0f2f5;
    }
    /* Top Header */
    .chat-header {
        background-color: #1877f2;
        color: white !important;
        padding: 15px;
        border-radius: 0px 0px 15px 15px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-top: -60px;
        margin-bottom: 20px;
    }
    /* Message Text Color Fix */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important; /* Pure White background for bubbles */
        border: 1px solid #dddfe2;
        padding: 12px;
        border-radius: 18px;
    }
    /* Making name and text dark for readability */
    .msg-name {
        color: #1877f2; /* Blue name */
        font-weight: bold;
        margin-bottom: 2px;
    }
    .msg-text {
        color: #050505 !important; /* Jet Black text for message */
        font-size: 16px;
    }
    /* Sidebar text color */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        color: #000000;
    }
    </style>
    <div class="chat-header">Messenger Lite</div>
    """, unsafe_allow_html=True)

# 3. Auto Refresh
st_autorefresh(interval=3000, key="chat_refresh")

# 4. Firebase Setup
db = firestore.Client.from_service_account_info(st.secrets["firebase"])

# 5. Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: black;'>👤 Profile</h2>", unsafe_allow_html=True)
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    user_name = st.text_input("Apna Naam Likhein:", value=st.session_state.username)
    if user_name:
        st.session_state.username = user_name

# 6. Chat Logic
if not st.session_state.username:
    st.warning("👈 Sidebar mein apna naam likhein!")
    st.stop()

# Input
chat_input = st.chat_input("Message likhein...")
if chat_input:
    db.collection("messages").add({
        "name": st.session_state.username,
        "text": chat_input,
        "timestamp": datetime.now()
    })

# 7. Messages Display
messages = db.collection("messages").order_by("timestamp", direction=firestore.Query.ASCENDING).stream()

for msg in messages:
    m = msg.to_dict()
    is_me = m["name"] == st.session_state.username
    
    with st.chat_message("user" if is_me else "assistant"):
        # Custom HTML for dark text
        st.markdown(f"""
            <div class="msg-name">{m['name']}</div>
            <div class="msg-text">{m['text']}</div>
            """, unsafe_allow_html=True)
