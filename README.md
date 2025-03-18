# TalWiz - A Talkative Wizard Chatbot

## Description
TalWiz is a chatbot application that allows users to ask questions about the Harry Potter universe. Built using Streamlit, it leverages various libraries from Langchain for document retrieval and vector storage (FAISS) to provide accurate and engaging responses.

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory and add the following:
     ```
     BASE_DIR=<path-to-your-base-directory>
     GROQ_API_KEY=<your-groq-api-key>
     ```

## Usage
To run the application, execute the following command:
```bash
streamlit run app/main.py
```
Once the application is running, you can interact with the chatbot through the web interface.

## Dependencies
- Streamlit
- Langchain
- FAISS
- dotenv

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.