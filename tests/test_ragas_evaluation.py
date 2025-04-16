import unittest
from unittest.mock import patch, MagicMock
from app.chatbot.retriever import load_vector_db
from app.chatbot.llm import get_chat_groq_instance, prompt
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import os
# import api key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class TestRAGASEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load vector DB once for all tests
        cls.vectors = load_vector_db()
        if cls.vectors is None:
            raise RuntimeError("Vector DB not found. Please ensure the FAISS index is built.")
        # Mock API key for LLM instantiation
        cls.mock_api_key = GROQ_API_KEY
        cls.llm = get_chat_groq_instance(cls.mock_api_key)
        cls.document_chain = create_stuff_documents_chain(llm=cls.llm, prompt=prompt)
        cls.retriever = cls.vectors.as_retriever(search_kwargs={'k': 3, 'score_threshold': 0.9})
        cls.retriever_chain = create_retrieval_chain(cls.retriever, cls.document_chain)

    @patch('app.agents.duckduckgo_search_agent.retrieve_search_results')
    def test_ragas_evaluation_on_sample_query(self, mock_search):
        # Mock DuckDuckGo search results
        mock_search.return_value = "Mocked search result about Harry Potter."

        sample_query = "Who is Harry Potter's godfather?"
        chat_history = ""

        combined_input = {
            "chat_history": chat_history,
            "input": sample_query,
            "search_results": mock_search.return_value
        }

        response_data = self.retriever_chain.invoke(combined_input)
        answer = response_data.get("answer", "")
        context_docs = response_data.get("context", [])

        # Basic assertions for RAG output
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer) > 0, "Answer should not be empty.")
        self.assertIsInstance(context_docs, list)
        self.assertTrue(len(context_docs) > 0, "Context documents should be retrieved.")

        # Additional RAGAS evaluation metrics can be added here
        # For example, relevance, accuracy, fluency, etc.
        # This is a placeholder for RAGAS metric evaluation

    @patch('app.agents.duckduckgo_search_agent.retrieve_search_results')
    def test_ragas_evaluation_with_chat_history(self, mock_search):
        mock_search.return_value = "Mocked search result about Hogwarts."

        sample_query = "Tell me about Hogwarts."
        chat_history = "You: Who is Harry Potter?\nTalWiz: Harry Potter is the boy who lived."

        combined_input = {
            "chat_history": chat_history,
            "input": sample_query,
            "search_results": mock_search.return_value
        }

        response_data = self.retriever_chain.invoke(combined_input)
        answer = response_data.get("answer", "")
        context_docs = response_data.get("context", [])

        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer) > 0)
        self.assertIsInstance(context_docs, list)
        self.assertTrue(len(context_docs) > 0)

if __name__ == "__main__":
    unittest.main()
