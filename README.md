# PDF RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot application that processes PDF documents and provides intelligent question-answering capabilities using Google Vertex AI.

## Setup Instructions

### 1. Virtual Environment Setup

The project uses a Python virtual environment located in `.venv/`. To activate it:

```bash
source .venv/bin/activate
```

### 2. Dependencies

All required dependencies are already installed in the virtual environment. If you need to reinstall:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your Google Cloud credentials:
   - Set `GOOGLE_CLOUD_PROJECT` to your Google Cloud project ID
   - Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account key file
   - Optionally adjust `VERTEX_AI_LOCATION` if needed

### 4. Running the Application

Use the provided run script:

```bash
./run.sh
```

Or manually:

```bash
source .venv/bin/activate
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
├── .venv/                  # Python virtual environment
├── src/                    # Source code modules
│   ├── __init__.py
│   ├── document_processor.py
│   ├── embedding_manager.py
│   ├── vector_store.py
│   └── chat_engine.py
├── app.py                  # Main Streamlit application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── run.sh                 # Application startup script
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Features

- PDF document upload and processing
- Text extraction and chunking
- Vector embeddings using Vertex AI
- Semantic search and retrieval
- Conversational chat interface
- Source citation and references