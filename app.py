import streamlit as st
from google.cloud import firestore
from datetime import datetime
from streamlit_autorefresh import st_autorefresh # Ye naya hai

# Har 3 seconds (3000ms) mein app apne aap refresh hoga
st_autorefresh(interval=3000, key="datarefresh")

# ... baaki ka code wahi rahega ...

# Page Configuration
st.set_page_config(page_title="Real-time Chat", page_icon="💬")
st.title("💬 Community Chat")

# Firebase setup (Authentication using Streamlit Secrets)
# Note: Iske liye aapko Firebase console se JSON key leni hogi
db = firestore.Client.from_service_account_info(st.secrets["firebase"])

# User Name setup
if "username" not in st.session_state:
    st.session_state.username = st.text_input("Apna Naam Likhein:", placeholder="e.g. Rahul")
    if st.session_state.username:
        st.rerun()
    st.stop()

# Message bhejni ki logic
chat_input = st.chat_input("Message type karein...")
if chat_input:
    doc_ref = db.collection("messages").document()
    doc_ref.set({
        "name": st.session_state.username,
        "text": chat_input,
        "timestamp": datetime.now()
    })

# Messages dikhane ki logic (Sorted by time)
messages_ref = db.collection("messages").order_by("timestamp", direction=firestore.Query.ASCENDING)
messages = messages_ref.stream()

for msg in messages:
    m = msg.to_dict()
    with st.chat_message("user" if m["name"] == st.session_state.username else "assistant"):
        st.write(f"**{m['name']}**: {m['text']}")

# Auto-refresh har 5 seconds mein (optional)
# st.empty()
# time.sleep(5)
# st.rerun()
