"""
PDF RAG Chatbot - Main Streamlit Application

This is the main entry point for the PDF RAG Chatbot application.
It provides a user interface for uploading PDF documents and interacting
with them through a chat interface powered by Vertex AI.
"""

import os
import streamlit as st
from src.document_processor import DocumentProcessor
from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore
from src.chat_engine import ChatEngine
import config

# Page configuration
st.set_page_config(
    page_title="PDF RAG Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title
st.title("📚 PDF RAG Chatbot")
st.markdown("""
Upload a PDF document and ask questions about its content.
The chatbot uses Google Vertex AI to provide intelligent answers based on the document content.
""")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_processed" not in st.session_state:
    st.session_state.document_processed = False
if "current_document" not in st.session_state:
    st.session_state.current_document = None

# Sidebar for document upload
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")
    
    if uploaded_file is not None:
        st.info("Document uploaded. Click 'Process Document' to continue.")
        
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                # Here we would call the document processing pipeline
                # For now, we'll just set the document as processed
                st.session_state.document_processed = True
                st.session_state.current_document = uploaded_file.name
                st.success(f"Document '{uploaded_file.name}' processed successfully!")

# Main chat interface
if st.session_state.document_processed:
    st.header(f"Chat with document: {st.session_state.current_document}")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask a question about the document...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate response (placeholder)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Here we would call the chat engine to generate a response
                # For now, we'll just use a placeholder response
                response = f"This is a placeholder response to your question: '{user_input}'"
                st.write(response)
        
        # Add assistant message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
else:
    st.info("Please upload and process a document to start chatting.")