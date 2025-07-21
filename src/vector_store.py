import os
from typing import List
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from src.config import get_project_config

# Load environment variables
load_dotenv()

class BatchSizeOneEmbeddings(Embeddings):
    """
    Wrapper for VertexAI embeddings that processes documents one at a time
    to handle batch size limitations.
    """
    
    def __init__(self, vertex_embeddings: VertexAIEmbeddings):
        self.vertex_embeddings = vertex_embeddings
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents by processing them one at a time."""
        embeddings = []
        total = len(texts)
        print(f"Processing {total} text chunks for embeddings...")
        
        for i, text in enumerate(texts, 1):
            if i % 10 == 0 or i == total:  # Show progress every 10 chunks
                print(f"Processing chunk {i}/{total}...")
            embedding = self.vertex_embeddings.embed_query(text)
            embeddings.append(embedding)
        
        print(f"✅ Successfully created embeddings for {total} chunks")
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        return self.vertex_embeddings.embed_query(text)

def get_vectorstore(text_chunks):
    """
    Create a vector store from text chunks using Vertex AI embeddings from .env configuration.
    
    Args:
        text_chunks: List of text chunks
        
    Returns:
        Vector store
    """
    # Get project configuration
    project_id, location = get_project_config()
    
    # Get embedding model from environment variable
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
    
    try:
        print(f"Using embedding model from .env: {embedding_model}")
        
        # Initialize Vertex AI embeddings
        vertex_embeddings = VertexAIEmbeddings(
            model_name=embedding_model,
            project=project_id,
            location=location
        )
        
        # Test the embeddings with a simple text
        vertex_embeddings.embed_query("test")
        print(f"Successfully initialized embedding model: {embedding_model}")
        
        # Wrap with batch size one handler
        embeddings = BatchSizeOneEmbeddings(vertex_embeddings)
        
    except Exception as e:
        print(f"Failed to initialize Vertex AI embedding model {embedding_model}: {e}")
        print("Falling back to HuggingFace embeddings...")
        
        # Fall back to HuggingFace embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    
    # Create the vector store
    vectorstore = FAISS.from_documents(text_chunks, embeddings)
    
    return vectorstore