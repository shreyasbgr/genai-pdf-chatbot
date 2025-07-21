"""Configuration settings for the PDF RAG Chatbot application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

# Application Configuration
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")

# Document Processing Configuration
MAX_CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_FILE_SIZE_MB = 50

# Vector Store Configuration
VECTOR_STORE_INDEX_NAME = "pdf_documents"
SIMILARITY_SEARCH_K = 5

# LLM Configuration
MODEL_NAME = "gemini-1.5-pro"
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.1