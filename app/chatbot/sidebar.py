import streamlit as st
from db.user_db import clear_chat_history
from db.mongo_connector import get_db
from chatbot.llm import validate_api_key

def sidebar_pannel(user_id):
    """Load sidebar components"""
    st.sidebar.title(f"⚡🧹⚯ - {user_id}")
    
    if st.sidebar.button("↻ Logout"):
        del st.session_state["user"]
        st.rerun()
    
    if st.sidebar.button("🗑️ Delete Current Chat"):
        clear_chat_history(user_id)
        st.session_state.chat_history = []
        st.session_state.retrieved_docs = []
        st.rerun()
    
    db = get_db()
    user_doc = db["users"].find_one({"username": user_id})
    current_groq_api_key = user_doc.get("groqcloud_api_key", "") if user_doc else ""
    
    with st.sidebar.form("groq_api_key_form"):
        new_api_key = st.text_input(
            "Enter your GroqCloud API Key:",
            value=current_groq_api_key,
            type="password",
            help="Provide your GroqCloud API key. If you already entered one before, it is loaded below. You can update it if needed."
        )
        submitted = st.form_submit_button("⎙ Save API Key")
        if submitted:
            if validate_api_key(new_api_key):
                db["users"].update_one({"username": user_id}, {"$set": {"groqcloud_api_key": new_api_key}}, upsert=True)
                st.session_state.groqcloud_api_key = new_api_key
                st.success("GroqCloud API key saved!")
                st.rerun()
            else:
                st.error("Invalid GroqCloud API Key! Please enter a correct key.")
                st.stop()
    
    st.sidebar.markdown("🔗 [Get your GroqCloud API Key](https://console.groq.com/keys)")
    
    if not current_groq_api_key:
        st.error("Error: No GroqCloud API key provided. Please enter your API key above to proceed.")
        st.stop()
    
    if not validate_api_key(current_groq_api_key):
        st.error("Invalid or missing GroqCloud API Key. Please enter a valid key.")
        st.stop()
    
    return current_groq_api_key