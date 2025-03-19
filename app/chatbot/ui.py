import streamlit as st
from chatbot.llm import llm, prompt
from chatbot.retriever import load_vector_db
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from agents.duckduckgo_search_agent import retrieve_search_results

def chatbot_ui():
    st.title("Hi, I'm TalWiz - a Talkative Wizard!")
    st.markdown("#### Ask me anything about the Harry Potter universe!")

    vectors = load_vector_db()

    if vectors:
        st.write("Good to go!")
    else:
        st.write("Vector DB not found!")
        return

    user_prompt = st.text_input("Let your curious mind ask TalWiz about the wizarding world...")
    
    if user_prompt:
        document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        duckduckgo_search_results = retrieve_search_results(user_prompt)
        retriever = vectors.as_retriever(search_kwargs={'k': 3})
        retriever_chain = create_retrieval_chain(retriever, document_chain)

        # Combine the user prompt and search results
        combined_input = {
            "input": user_prompt,
            "search_results": duckduckgo_search_results,
        }

        response = retriever_chain.invoke(combined_input)
        st.write(response["answer"])

        with st.expander("Document Similarity Search"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("--------------------")

        with st.expander("DuckDuckGo Search Results"):
            st.write(duckduckgo_search_results)