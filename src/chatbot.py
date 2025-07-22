import os
from dotenv import load_dotenv # Although loaded in app.py, good practice to have it if run standalone
import logging # Import logging

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory # Reverted import as per previous fix
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
from src.config import get_project_config, get_model_config

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Load environment variables (only if this module might be run standalone for testing)
# load_dotenv() 

def get_conversation_chain(vectorstore):
    """
    Create a conversation chain for the chatbot.
    
    Args:
        vectorstore: Vector store containing document embeddings
        
    Returns:
        Conversation chain
        
    Raises:
        RuntimeError: If configuration cannot be loaded or LLM fails to initialize.
        Exception: For any other unexpected errors during chain creation.
    """
    if vectorstore is None:
        logger.error("Vectorstore provided to get_conversation_chain is None.")
        raise ValueError("Cannot create conversation chain with a None vectorstore.")

    # Get configuration from .env file
    try:
        project_id, location = get_project_config()
        model_config = get_model_config()
        language_model_name = model_config['language_model']
        temperature = model_config['temperature']
        max_output_tokens = model_config['max_output_tokens']
        logger.info(f"Retrieved project and model configuration for LLM: "
                    f"Project ID='{project_id}', Location='{location}', "
                    f"Model='{language_model_name}', Temp='{temperature}', Max Tokens='{max_output_tokens}'")
    except Exception as e:
        logger.critical(f"Failed to load project or model configuration for LLM: {e}", exc_info=True)
        raise RuntimeError(f"Failed to load configuration for language model: {e}")
    
    logger.info(f"Attempting to initialize Vertex AI language model: '{language_model_name}'")
    
    try:
        # Initialize the language model with Vertex AI
        llm = VertexAI(
            model_name=language_model_name,
            temperature=temperature,
            project=project_id,
            location=location,
            max_output_tokens=max_output_tokens
        )
        # Optional: A quick test to ensure the LLM is callable (can add a simple generate call if needed, but often initialization is enough)
        # llm.invoke("Hello world")
        logger.info(f"Successfully initialized Vertex AI language model: '{language_model_name}'.")
        
    except Exception as e:
        logger.critical(f"Failed to initialize Vertex AI language model '{language_model_name}': {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize Vertex AI language model. Check your configuration, credentials, and API access. Error: {e}")
    
    logger.info("Creating ConversationBufferMemory for chat history.")
    try:
        # Create memory for conversation
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        logger.info("ConversationBufferMemory created successfully.")
    except Exception as e:
        logger.error(f"Failed to create ConversationBufferMemory: {e}", exc_info=True)
        raise RuntimeError(f"Failed to set up conversation memory: {e}")
    
    # Create custom prompt with better instructions
    template = """You are a helpful assistant that answers questions based on the provided PDF document context.

Instructions:
- Use ONLY the information from the provided context to answer questions. Do not make up information.
- If the context doesn't contain enough information to answer the question, clearly state: "I don't have enough information in the document to answer that question based on the provided context."
- If asked for an opinion, personal information, or anything not present in the document, politely state that you can only answer questions based on the document's content.
- Provide clear, concise, and helpful answers.
- If asked to summarize, provide a structured and comprehensive summary based on the available context, covering key points.
- Always provide a complete response, never leave answers empty.
- Maintain a professional and informative tone.

Context from the PDF:
{context}

Question: {question}

Answer:"""
    
    QA_PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    logger.info("PromptTemplate for QA defined.")
    
    logger.info("Creating ConversationalRetrievalChain.")
    try:
        # Create the conversation chain
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}), # k=5 is a good starting point for large docs
            memory=memory,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT}
        )
        logger.info("ConversationalRetrievalChain created successfully.")
        return conversation_chain
    except Exception as e:
        logger.critical(f"Failed to create ConversationalRetrievalChain: {e}", exc_info=True)
        raise RuntimeError(f"Failed to set up conversational chain: {e}")