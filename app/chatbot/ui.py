import streamlit as st
from chatbot.llm import llm, prompt
from chatbot.retriever import load_vector_db
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from agents.duckduckgo_search_agent import retrieve_search_results
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSS_DARK_PATH = BASE_DIR / "app" / "frontend" / "css" / "style_dark.css"
CSS_LIGHT_PATH = BASE_DIR / "app" / "frontend" / "css" / "style_light.css"

def load_css(theme):
    css_path = CSS_DARK_PATH if theme == "Dark" else CSS_LIGHT_PATH
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def chatbot_ui():
    # Theme selection
    theme = st.radio("Select Theme:", ["Dark", "Light"], horizontal=True)
    
    # Apply selected theme
    load_css(theme)

    st.title("🧙‍♂️ TalWiz - The Talkative Wizard!")
    st.markdown("### Ask me anything about the wizarding world! ⚡")
    
    vectors = load_vector_db()
    
    if vectors:
        st.success("✨ The magic is ready! Ask your questions below.")
    else:
        st.error("❌ Vector DB not found! The Ministry of Magic is investigating...")
        return
    
    user_prompt = st.text_input("Let your curious mind ask TalWiz... 🏰")
    
    if user_prompt:
        document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        duckduckgo_search_results = retrieve_search_results(user_prompt)
        retriever = vectors.as_retriever(search_kwargs={'k': 3})
        retriever_chain = create_retrieval_chain(retriever, document_chain)

        combined_input = {"input": user_prompt, "search_results": duckduckgo_search_results}
        response = retriever_chain.invoke(combined_input)
        
        st.markdown("#### 🔮 The Wizard's Answer:")
        st.write(response["answer"])
        
        with st.expander("📜 Document Similarity Search:"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("--------------------")
        
        with st.expander("🔍 DuckDuckGo Search Results:"):
            st.write(duckduckgo_search_results)
