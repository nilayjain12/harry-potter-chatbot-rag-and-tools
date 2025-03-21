import streamlit as st
from chatbot.ui import chatbot_ui
from auth.auth_ui import auth_ui

if __name__ == "__main__":
    if "user" not in st.session_state:
        auth_ui()
    else:
        chatbot_ui()
