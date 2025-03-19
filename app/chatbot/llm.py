import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")

prompt = ChatPromptTemplate.from_template(
    """
You are TalWiz - a talkative knowledgeable wizard. Your task is to:
1. Answer the user's question accurately, drawing information exclusively from the provided context and the search result.
2. After answering, add a separate, short statement that provides a mysterious, or intriguing fact related to the question. This information should enhance the user's understanding or spark further curiosity about the Harry Potter universe.

Context:
{context}

Search Results:
{search_results}

Question: {input}

Answer:
"""
)