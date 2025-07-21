# PDF Chatbot with Vertex AI

A streamlined application that allows users to chat with their PDF documents using natural language. This application uses LangChain, Google Vertex AI, Streamlit, and vector databases to provide accurate responses based on the content of uploaded PDFs.

## Features

- Upload and process large PDF documents (up to 200+ pages)
- Ask questions about the PDF content in natural language
- Get contextually relevant answers from the document
- Conversation memory to maintain context across multiple questions
- Powered by Google Vertex AI for embeddings and language model

## Project Structure

```
pdf-chatbot/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables for Google Cloud
├── src/
│   ├── pdf_processor.py    # PDF processing module
│   ├── vector_store.py     # Vector database module with Vertex AI embeddings
│   ├── config.py           # Google Cloud configuration
│   └── chatbot.py          # LangChain conversation module with Vertex AI
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google Cloud credentials:
   - Create a service account with access to Vertex AI
   - Download the service account key JSON file
   - Update the `.env` file with your Google Cloud project details:
     ```
     GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
     PROJECT_ID=your-google-cloud-project-id
     LOCATION=us-central1
     MODEL_NAME=gemini-2.5-pro
     EMBEDDING_MODEL=text-embedding-004
     TEMPERATURE=0
     MAX_OUTPUT_TOKENS=1024
     ```
4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Upload a PDF document using the file uploader
2. Wait for the document to be processed
3. Ask questions about the document in the chat input
4. Receive contextually relevant answers based on the document content

## Technologies Used

- **Streamlit**: For the web interface
- **LangChain**: For document processing and conversation chains
- **Google Vertex AI**: For embeddings and language model capabilities
- **FAISS**: For efficient vector storage and similarity search
- **Google Cloud Platform**: For infrastructure and API access