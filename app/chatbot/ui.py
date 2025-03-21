import streamlit as st
from pathlib import Path
from chatbot.llm import llm, prompt
from chatbot.retriever import load_vector_db
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from agents.duckduckgo_search_agent import retrieve_search_results
from db.user_db import get_chat_history, save_chat_message

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSS_DARK_PATH = BASE_DIR / "app" / "frontend" / "css" / "style_dark.css"
CSS_LIGHT_PATH = BASE_DIR / "app" / "frontend" / "css" / "style_light.css"
CSS_CHAT_PATH = BASE_DIR / "app" / "frontend" / "css" / "chat_style.css"

def load_css():
    css_path_light = CSS_LIGHT_PATH
    with open(css_path_light) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    css_path_chat = CSS_CHAT_PATH
    with open(css_path_chat) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def chatbot_ui():
    load_css()
    # Ensure the user is authenticated
    if "user" not in st.session_state:
        st.error("User not logged in. Please login or register.")
        return

    # Use authenticated username as user ID
    user_id = st.session_state.user

    # Logout button in the sidebar
    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.rerun()
    
    # New button: Delete Current Chat
    if st.sidebar.button("Delete Current Chat"):
        from db.user_db import clear_chat_history
        clear_chat_history(user_id)
        st.session_state.chat_history = []  # Clear the session chat history
        st.rerun()  # Restart the app to reflect changes

    st.title("🧙‍♂️ TalWiz - The Talkative Wizard!")
    st.markdown("#### Ask me anything about the wizarding world! ⚡")

    # Load vector database
    vectors = load_vector_db()
    if not vectors:
        st.error("❌ Vector DB not found! The Ministry of Magic is investigating...")
        return

    # Load chat history from MongoDB if not already in session_state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = get_chat_history(user_id)
    
        # Use a form to submit new questions so the input box clears automatically
    with st.form("chat_form", clear_on_submit=True):
        user_prompt = st.text_input("Your message", key="user_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_prompt:
            # Retrieve DuckDuckGo search results and context from vector DB
            document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
            duckduckgo_search_results = retrieve_search_results(user_prompt)
            retriever = vectors.as_retriever(search_kwargs={'k': 3})
            retriever_chain = create_retrieval_chain(retriever, document_chain)

            # Optionally pass recent chat history as context (e.g., last 5 messages)
            recent_history = "\n".join(
                [f"You: {m['user']}\nTalWiz: {m['bot']}" for m in st.session_state.chat_history[-5:]]
            )
            combined_input = {
                "chat_history": recent_history,
                "input": user_prompt,
                "search_results": duckduckgo_search_results
            }
            response_data = retriever_chain.invoke(combined_input)
            response = response_data.get("answer", "I am not sure, try again!")

            # Append new conversation to session_state and save it to MongoDB
            st.session_state.chat_history.append({"user": user_prompt, "bot": response})
            save_chat_message(user_id, user_prompt, response)

            # Refresh the app to display the updated conversation history
            st.rerun()

    # Display the conversation history in a scrollable container
    conversation_container = st.container()
    with conversation_container:
        chat_history_html = ""
        # Reverse the chat history to display the latest at the top
        reversed_chat_history = reversed(st.session_state.chat_history)
        for msg in reversed_chat_history:
            chat_history_html += f"<div class='message user-message'><strong>You:</strong> {msg['user']}</div>"
            chat_history_html += f"<div class='message bot-message'><strong>TalWiz:</strong> {msg['bot']}</div>"
            chat_history_html += "<hr style='margin: 5px 0;'>"
        st.markdown(f"<div class='conversation-container' id='conversation-container'>{chat_history_html}</div>", unsafe_allow_html=True)