import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.documents import Document # Import Document type for clarity with chunks
from src.config import get_project_config, get_model_config # get_model_config is needed to get embedding model name
import logging # Import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

def get_vectorstore(text_chunks: List[Document]):
    """
    Create a FAISS vector store from text chunks using Vertex AI embeddings.
    
    Args:
        text_chunks: List of text chunks (LangChain Document objects).
        
    Returns:
        FAISS vector store.
        
    Raises:
        ValueError: If no text chunks are provided or if embedding model fails to initialize.
        Exception: For any other errors during vector store creation.
    """
    if not text_chunks:
        logger.warning("No text chunks provided to get_vectorstore. Cannot create vector store.")
        raise ValueError("No text chunks available to create a vector store.")

    # Get project and model configuration
    try:
        project_id, location = get_project_config()
        model_config = get_model_config()
        embedding_model_name = model_config["embedding_model"]
    except Exception as e:
        logger.critical(f"Failed to get project or model configuration for embeddings: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load configuration for embedding model: {e}")

    logger.info(f"Attempting to initialize Vertex AI embeddings with model: '{embedding_model_name}'")
    
    try:
        # Initialize Vertex AI embeddings
        vertex_embeddings = VertexAIEmbeddings(
            model_name=embedding_model_name,
            project=project_id,
            location=location
        )
        
        # A quick test to ensure the embedding model is callable
        _ = vertex_embeddings.embed_query("test embedding functionality")
        logger.info(f"Successfully initialized and tested Vertex AI embedding model: '{embedding_model_name}'.")
        
    except Exception as e:
        logger.critical(f"Failed to initialize or test Vertex AI embedding model '{embedding_model_name}': {e}", exc_info=True)
        # It's crucial for the app's core functionality to have Vertex AI embeddings working.
        # So, we raise an error rather than falling back to a different provider.
        raise RuntimeError(f"Failed to initialize Vertex AI embedding model. Please check your configuration, credentials, and API access. Error: {e}")
    
    logger.info(f"Creating FAISS vector store from {len(text_chunks)} text chunks.")
    try:
        # Create the vector store
        vectorstore = FAISS.from_documents(text_chunks, vertex_embeddings)
        logger.info("FAISS vector store created successfully.")
        return vectorstore
    except Exception as e:
        logger.critical(f"An error occurred while creating the FAISS vector store: {e}", exc_info=True)
        raise RuntimeError(f"Failed to create vector store from text chunks: {e}")