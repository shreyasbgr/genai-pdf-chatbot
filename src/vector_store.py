import os
from typing import List
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings # Keep this import for type hinting if needed elsewhere, though not directly used for the main embedding
from src.config import get_project_config
from langchain.docstore.document import Document # Import Document class

# Load environment variables
load_dotenv()

# --- REMOVED BatchSizeOneEmbeddings CLASS ---
# VertexAIEmbeddings handles internal batching for models that support it,
# like text-embedding-004.

def get_vectorstore(text_chunks: List[Document]):
    """
    Create a vector store from text chunks using Vertex AI embeddings from .env configuration.
    
    Args:
        text_chunks: List of text chunks (LangChain Document objects)
        
    Returns:
        Vector store (FAISS)
    """
    # Get project configuration
    project_id, location = get_project_config()
    
    # Get embedding model from environment variable
    # Ensure no trailing spaces for the model name
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-004").strip() 
    
    try:
        print(f"Using embedding model from .env: {embedding_model}")
        
        # Initialize Vertex AI embeddings directly.
        # Langchain's VertexAIEmbeddings will handle batching internally
        # for models like text-embedding-004 which support it.
        embeddings = VertexAIEmbeddings(
            model_name=embedding_model,
            project=project_id,
            location=location
        )
        
        # Test the embeddings with a simple text to ensure initialization
        embeddings.embed_query("test query for embedding model")
        print(f"Successfully initialized embedding model: {embedding_model}")
        
    except Exception as e:
        print(f"Failed to initialize Vertex AI embedding model {embedding_model}: {e}")
        print("Falling back to HuggingFace embeddings...")
        
        # Fall back to HuggingFace embeddings if Vertex AI fails
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    
    # Create the vector store from documents and embeddings
    vectorstore = FAISS.from_documents(text_chunks, embeddings)
    
    return vectorstore