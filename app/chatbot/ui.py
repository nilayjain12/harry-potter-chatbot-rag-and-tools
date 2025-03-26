import streamlit as st
from pathlib import Path
from chatbot.retriever import load_vector_db
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from agents.duckduckgo_search_agent import retrieve_search_results
from db.user_db import get_chat_history, save_chat_message
from db.mongo_connector import get_db  # Import to update user record
from chatbot.llm import get_chat_groq_instance, prompt, validate_api_key  # Notice we now import the function

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
    if "user" not in st.session_state:
        st.error("User not logged in. Please login or register.")
        return

    user_id = st.session_state.user

    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.rerun()

    if st.sidebar.button("Delete Current Chat"):
        from db.user_db import clear_chat_history
        clear_chat_history(user_id)
        st.session_state.chat_history = []
        st.session_state.retrieved_docs = []  # Clear retrieved documents as well
        st.rerun()

    st.title("🧙‍♂️ TalWiz - The Talkative Wizard!")
    st.markdown("#### Ask me anything about the wizarding world! ⚡")

    vectors = load_vector_db()
    if not vectors:
        st.error("❌ Vector DB not found! The Ministry of Magic is investigating...")
        return
    else:
        st.write(f"💡TalWiz is ready to chat!")

    # ----------------- GroqCloud API Key Input Section -----------------
    # GroqCloud API Key Input Section
    db = get_db()
    user_doc = db["users"].find_one({"username": user_id})
    current_groq_api_key = user_doc.get("groqcloud_api_key", "") if user_doc else ""

    # Validate the API key when the user submits their question



    with st.form("groq_api_key_form"):
        new_api_key = st.text_input(
            "Enter your GroqCloud API Key:",
            value=current_groq_api_key,
            type="password",
            help="Provide your GroqCloud API key. If you already entered one before, it is loaded below. You can update it if needed."
        )
        submitted = st.form_submit_button("Save API Key")
        if submitted:
            if validate_api_key(new_api_key):
                db["users"].update_one({"username": user_id}, {"$set": {"groqcloud_api_key": new_api_key}}, upsert=True)
                st.session_state.groqcloud_api_key = new_api_key
                st.success("GroqCloud API key saved!")
                st.rerun()
            else:
                st.error("Invalid GroqCloud API Key! Please enter a correct key.")
                st.stop()
    # --------------------------------------------------------------------

    # Validate the API key (do not fallback to .env key for logged-in users)
    if not current_groq_api_key:
        st.error("Error: No GroqCloud API key provided. Please enter your API key above to proceed.")
        st.stop()

    # Validate the API key when the user submits their question
    if not current_groq_api_key or not validate_api_key(current_groq_api_key):
        st.error("Invalid or missing GroqCloud API Key. Please enter a valid key.")
        st.stop()

    llm = get_chat_groq_instance(current_groq_api_key)  # Moved API key validation here


    if "chat_history" not in st.session_state:
        st.session_state.chat_history = get_chat_history(user_id)
    if "retrieved_docs" not in st.session_state:
        st.session_state.retrieved_docs = []

    with st.form("chat_form", clear_on_submit=True):
        user_prompt = st.text_input("Your message", key="user_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_prompt:
            document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
            duckduckgo_search_results = retrieve_search_results(user_prompt)
            retriever = vectors.as_retriever(search_kwargs={'k': 3})
            retriever_chain = create_retrieval_chain(retriever, document_chain)

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
            
            retrieved_documents = response_data.get("context", [])
            retrieved_texts = [doc.page_content for doc in retrieved_documents]
            
            st.session_state.retrieved_docs.append(retrieved_texts)
            st.session_state.duckduckgo_search_results = duckduckgo_search_results
            
            st.session_state.chat_history.append({
                "user": user_prompt,
                "bot": response,
                "retrieved_docs": retrieved_texts,
                "duckduckgo_search_results": duckduckgo_search_results
            })
            save_chat_message(user_id, user_prompt, response)
            st.rerun()

    conversation_container = st.container()
    with conversation_container:
        reversed_chat_history = reversed(st.session_state.chat_history)
        for idx, msg in enumerate(reversed_chat_history):
            st.markdown(f"<div class='message user-message'><strong>You:</strong> {msg['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='message bot-message'><strong>TalWiz:</strong> {msg['bot']}</div>", unsafe_allow_html=True)
            
            with st.expander(f"📜 Retrieved Document Context (Chat {len(st.session_state.chat_history) - idx})"):
                if msg.get("retrieved_docs"):
                    for doc in msg["retrieved_docs"]:
                        st.write(doc)
                        st.write("---")
                else:
                    st.write("No documents retrieved.")

            with st.expander(f"🔍 DuckDuckGo Search Results (Chat {len(st.session_state.chat_history) - idx})"):
                if msg.get("duckduckgo_search_results"):
                    st.write(msg["duckduckgo_search_results"])
                else:
                    st.write("No search results found.")
