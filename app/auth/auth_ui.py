import streamlit as st
from db.user_db import register_user, login_user, get_chat_history

def auth_ui():
    st.title("Welcome to TalWiz - A Talkative Wizard Chatbot!")
    st.markdown("Please login or register to continue.")
    
    auth_mode = st.radio("Choose an option", ["Login", "Register"])
    
    if auth_mode == "Register":
        with st.form("register_form", clear_on_submit=True):
            st.markdown("<div class='auth-title'>Register</div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="reg_username")
            password = st.text_input("Password", type="password", key="reg_password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                # Input validations
                if not username:
                    st.error("Username cannot be empty.")
                elif not password:
                    st.error("Password cannot be empty.")
                else:
                    success, message = register_user(username, password)
                    if success:
                        st.success(message)
                        st.session_state.user = username  # Set logged in user
                        st.session_state.current_user = username  # Track the chat owner
                        # Load chat history for the new user
                        st.session_state.chat_history = get_chat_history(username)
                    else:
                        st.error(message)
                        
    else:  # Login mode
        with st.form("login_form", clear_on_submit=True):
            st.markdown("<div class='auth-title'>Login</div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Input validations
                if not username:
                    st.error("Username cannot be empty.")
                elif not password:
                    st.error("Password cannot be empty.")
                else:
                    success, result = login_user(username, password)
                    if success:
                        st.success("Login successful!")
                        st.session_state.user = username  # Set logged in user
                        st.session_state.current_user = username  # Track the chat owner
                        # Load chat hist
