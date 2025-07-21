"""
Chat Engine Module

This module handles query processing and response generation
for the PDF RAG Chatbot application.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import config
from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[str]] = None


class ChatEngine:
    """Handles query processing and response generation."""
    
    def __init__(self, embedding_manager: EmbeddingManager, vector_store: VectorStore):
        """
        Initialize the chat engine.
        
        Args:
            embedding_manager: The embedding manager for generating query embeddings
            vector_store: The vector store for retrieving relevant documents
        """
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store
        self.k = config.SIMILARITY_SEARCH_K
    
    def retrieve_relevant_chunks(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: The user query
            
        Returns:
            List[Dict[str, Any]]: List of relevant document chunks
        """
        # Generate embedding for the query
        query_embedding = self.embedding_manager.generate_query_embedding(query)
        
        if not query_embedding:
            return []
        
        # Retrieve similar documents
        results = self.vector_store.similarity_search(query_embedding, k=self.k)
        
        return results
    
    def generate_response(self, query: str, context: List[Dict[str, Any]], chat_history: List[ChatMessage] = None) -> ChatMessage:
        """
        Generate a response using the query and retrieved context.
        
        Args:
            query: The user query
            context: The retrieved document chunks
            chat_history: Previous chat messages for context
            
        Returns:
            ChatMessage: The generated response
        """
        if not context:
            # No relevant context found
            return ChatMessage(
                role="assistant",
                content="I couldn't find any relevant information in the document to answer your question.",
                timestamp=datetime.now(),
                sources=[]
            )
        
        # Extract text from context
        context_texts = [item["text"] for item in context]
        
        # Extract sources for citation
        sources = []
        for item in context:
            if "metadata" in item and "source" in item["metadata"]:
                source = item["metadata"]["source"]
                if source not in sources:
                    sources.append(source)
        
        # In a real implementation, we would use Vertex AI to generate a response
        # For now, we'll just create a placeholder response
        response_text = f"This is a placeholder response to your question: '{query}'\n\n"
        response_text += "I found the following relevant information:\n\n"
        
        for i, text in enumerate(context_texts[:2]):  # Limit to first 2 chunks for brevity
            response_text += f"Excerpt {i+1}: {text[:100]}...\n\n"
        
        return ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.now(),
            sources=sources
        )
    
    def process_query(self, query: str, chat_history: List[ChatMessage] = None) -> ChatMessage:
        """
        Process a user query and generate a response.
        
        Args:
            query: The user query
            chat_history: Previous chat messages for context
            
        Returns:
            ChatMessage: The generated response
        """
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(query)
        
        # Generate response
        response = self.generate_response(query, relevant_chunks, chat_history)
        
        return response