"""
Vector Store Module

This module handles vector storage and retrieval using FAISS
for the PDF RAG Chatbot application.
"""

import os
import numpy as np
from typing import List, Dict, Any
import faiss
import pickle
import config


class VectorStore:
    """Manages vector storage and retrieval using FAISS."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.index = None
        self.documents = []
        self.index_name = config.VECTOR_STORE_INDEX_NAME
        self.dimension = 768  # Default embedding dimension
    
    def initialize_store(self, dimension: int = 768):
        """
        Initialize the FAISS index.
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []
    
    def store_embeddings(self, embeddings_with_metadata: List[Dict[str, Any]]):
        """
        Store embeddings in the FAISS index.
        
        Args:
            embeddings_with_metadata: List of dictionaries containing embeddings and metadata
        """
        if self.index is None:
            self.initialize_store()
        
        # Extract embeddings and documents
        embeddings = [item["embedding"] for item in embeddings_with_metadata]
        
        # Store documents for retrieval
        self.documents.extend(embeddings_with_metadata)
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add embeddings to the index
        self.index.add(embeddings_array)
    
    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search using the query embedding.
        
        Args:
            query_embedding: The query embedding vector
            k: Number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of similar documents with metadata
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Convert query embedding to numpy array
        query_array = np.array([query_embedding]).astype('float32')
        
        # Perform search
        distances, indices = self.index.search(query_array, min(k, len(self.documents)))
        
        # Get the documents for the indices
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents) and idx >= 0:
                result = self.documents[idx].copy()
                result["distance"] = float(distances[0][i])
                results.append(result)
        
        return results
    
    def save_index(self, directory: str):
        """
        Save the FAISS index and documents to disk.
        
        Args:
            directory: Directory to save the index and documents
        """
        if self.index is None:
            return
        
        os.makedirs(directory, exist_ok=True)
        
        # Save the FAISS index
        index_path = os.path.join(directory, f"{self.index_name}.index")
        faiss.write_index(self.index, index_path)
        
        # Save the documents
        docs_path = os.path.join(directory, f"{self.index_name}.docs")
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load_index(self, directory: str) -> bool:
        """
        Load the FAISS index and documents from disk.
        
        Args:
            directory: Directory containing the index and documents
            
        Returns:
            bool: True if loading was successful, False otherwise
        """
        index_path = os.path.join(directory, f"{self.index_name}.index")
        docs_path = os.path.join(directory, f"{self.index_name}.docs")
        
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            return False
        
        try:
            # Load the FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load the documents
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False