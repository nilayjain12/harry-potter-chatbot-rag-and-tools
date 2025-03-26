import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

import requests

def validate_api_key(api_key):
    """
    Validates the provided GroqCloud API key by making a minimal request to the chat completion endpoint.
    Returns True if the key is valid, False otherwise.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant",  # Use an available model
        "messages": [{"role": "system", "content": "ping"}],  # Minimal payload
        "max_tokens": 1
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

def get_chat_groq_instance(current_groq_api_key):
    if not current_groq_api_key:
        raise ValueError("No GroqCloud API key provided. Please enter your API key in the settings.")

    try:
        llm = ChatGroq(api_key=current_groq_api_key, model="llama-3.1-8b-instant")
        
        # Optional: Perform a lightweight validation call (depends on API behavior)
        # response = llm.invoke("ping")  # Uncomment if the API supports a quick validation query

        return llm
    except Exception as e:
        raise ValueError(f"Invalid GroqCloud API Key! Please Enter Correct Key.")

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
