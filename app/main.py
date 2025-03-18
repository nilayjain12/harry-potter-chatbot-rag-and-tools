# streamlit for end-to-end chatbot
import streamlit as st
# os for file operations
import os
# Groq for open-source models with fast inference
from langchain_groq import ChatGroq
# loading the Ollama embeddings
from langchain_ollama import OllamaEmbeddings
# loading huggingface embeddings for open-source
from langchain.embeddings import HuggingFaceEmbeddings
# for combining documents using chains
from langchain.chains.combine_documents import create_stuff_documents_chain
# importing the chatprompt template
from langchain_core.prompts import ChatPromptTemplate
# for retrieval chains
from langchain.chains import create_retrieval_chain
# vector database
from langchain_community.vectorstores import FAISS
# loading environment variables
from dotenv import load_dotenv
load_dotenv()
# import path library
from pathlib import Path

# Get the absolute path of the current script (main.py)
BASE_DIR = Path(__file__).resolve().parent.parent  # Goes up one level to 'harry-potter-chatbot'
VECTOR_DB_PATH = BASE_DIR / "data" / "database" / "faiss_index"

# load the groq api key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# initializing the title
st.title("Hi, I'm TalWiz - a Talkative Wizard!")
st.markdown("#### You can ask me anything about the world of Harry Potter, and I'll do my best to answer your questions.")

# Load the FAISS vector database
if "vectors" not in st.session_state:
    if os.path.exists(VECTOR_DB_PATH):
        st.session_state.vectors = FAISS.load_local(VECTOR_DB_PATH, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"), allow_dangerous_deserialization=True)
        st.write("Vector DB Loaded from Disk!")
    else:
        st.write("Vector DB not found! Please run precompute_embeddings.py first.")

# initializing the chatbot llm model
llm = ChatGroq(api_key=GROQ_API_KEY,
               model="llama-3.1-8b-instant")

# initializing the promp using chatprompt template
prompt = ChatPromptTemplate.from_template(
    """
You are an AI model simulating a knowledgeable wizard who has read all the Harry Potter books. Your task is to:
1.  Answer the user's question accurately, drawing information exclusively from the provided context.
2.  After answering, add a separate, short statement that provides an additional, mysterious, or intriguing piece of information related to the question. This information should enhance the user's understanding or spark further curiosity about the Harry Potter universe.
Context:
{context}
Question: {input}
"""
)

# creating the streamlit input box for the user to ask question
user_prompt = st.text_input("Let your curious mind begin to ask the TalWiz about the Harry Potter universe...")

# Process user input
if user_prompt:
    # Ensure vector DB is loaded
    if "vectors" in st.session_state:
        document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        retriever = st.session_state.vectors.as_retriever()
        retriever_chain = create_retrieval_chain(retriever, document_chain)

        response = retriever_chain.invoke({"input": user_prompt})
        st.write(response["answer"])

        # Show related documents in an expander
        with st.expander("Document Similarity Search"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)
                st.write("--------------------")
    else:
        st.write("Vector DB is not loaded. Please run precompute_embeddings.py first.")