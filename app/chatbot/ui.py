import streamlit as st
from pathlib import Path
from chatbot.retriever import load_vector_db
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from agents.duckduckgo_search_agent import retrieve_search_results
from db.user_db import get_chat_history, save_chat_message
from chatbot.llm import get_chat_groq_instance, prompt
from frontend.css_loader import load_css
from chatbot.sidebar import sidebar_pannel

def chatbot_ui():
    load_css()
    if "user" not in st.session_state:
        st.error("User not logged in. Please login or register.")
        return

    user_id = st.session_state.user
    current_groq_api_key = sidebar_pannel(user_id)
    
    st.title("🧙‍♂️ TalWiz - The Talkative Wizard!")
    st.markdown("#### Ask me anything about the wizarding world! ⚡")
    
    vectors = load_vector_db()
    if not vectors:
        st.error("❌ Vector DB not found! The Ministry of Magic is investigating...")
        return
    else:
        st.write("💡TalWiz is ready to chat!")
    
    llm = get_chat_groq_instance(current_groq_api_key)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = get_chat_history(user_id)
    if "retrieved_docs" not in st.session_state:
        st.session_state.retrieved_docs = []
    
    with st.form("chat_form", clear_on_submit=True):
        user_prompt = st.text_input("Your message", key="user_input")
        submitted = st.form_submit_button("ᯓ➤ Send")
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
            st.markdown(f"<div class='message user-message'>🫵🏻 <strong>You:</strong> {msg['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='message bot-message'>🦉 <strong>TalWiz:</strong> {msg['bot']}</div>", unsafe_allow_html=True)
            
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
            
            st.write("---")