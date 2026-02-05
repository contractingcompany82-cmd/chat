import streamlit as st
from google.cloud import firestore
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Config aur Auto-refresh (Sabse upar)
st.set_page_config(page_title="Real-time Chat", page_icon="💬")
st.title("💬 My Global Chat")
st_autorefresh(interval=3000, key="datarefresh")

# 2. Firebase Connection
db = firestore.Client.from_service_account_info(st.secrets["firebase"])

# 3. Sidebar mein User Settings aur Clear Chat
with st.sidebar:
    st.header("Settings")
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    new_user = st.text_input("Apna Naam:", value=st.session_state.username)
    if new_user:
        st.session_state.username = new_user

    st.divider()
    
    # Clear Chat Button
    if st.button("🗑️ Clear All Messages"):
        docs = db.collection("messages").get()
        for doc in docs:
            doc.reference.delete()
        st.success("Chat saaf ho gayi!")
        st.rerun()

# 4. Username check (Agar naam nahi dala toh aage nahi badhega)
if not st.session_state.username:
    st.warning("Pehle Sidebar mein apna naam likhein!")
    st.stop()

# 5. Message Input (Message bhejne ke liye)
chat_input = st.chat_input("Message likhein...")
if chat_input:
    doc_ref = db.collection("messages").document()
    doc_ref.set({
        "name": st.session_state.username,
        "text": chat_input,
        "timestamp": datetime.now()
    })

# 6. Messages Display (Messages dikhane ke liye)
# Messages ko purane se naye ki taraf dikhane ke liye (Oldest at top, Newest at bottom)
messages_ref = db.collection("messages").order_by("timestamp", direction=firestore.Query.ASCENDING)
messages = messages_ref.stream()

for msg in messages:
    m = msg.to_dict()
    role = "user" if m["name"] == st.session_state.username else "assistant"
    with st.chat_message(role):
        st.write(f"**{m['name']}**: {m['text']}")
