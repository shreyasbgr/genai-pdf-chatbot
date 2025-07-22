import os
import logging
from langchain.chains import ConversationalRetrievalChain
from langchain_google_vertexai import ChatVertexAI # Changed from VertexAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate # Ensure this is imported for custom templates
from src.config import get_model_config # Import get_model_config

logger = logging.getLogger(__name__)

def get_conversation_chain(vectorstore):
    """
    Initializes and returns a conversational retrieval chain using a ChatModel.

    Args:
        vectorstore: The FAISS vector store containing document embeddings.

    Returns:
        ConversationalRetrievalChain: The initialized LangChain conversational chain.
    """
    logger.info("Initializing conversation chain with ChatModel.")

    # Get model configuration from src/config.py
    model_config = get_model_config()

    # Instantiate the ChatModel (ChatVertexAI)
    # ChatModels are designed for multi-turn conversations and handle message roles (Human, AI)
    # more explicitly, often leading to better conversational flow.
    llm = ChatVertexAI(
        model_name=model_config["language_model"],
        temperature=model_config["temperature"],
        max_output_tokens=model_config["max_output_tokens"],
        # Add any other ChatVertexAI specific parameters if needed
    )
    logger.debug(f"ChatModel instantiated: {model_config['language_model']} with temp={model_config['temperature']}, max_tokens={model_config['max_output_tokens']}")

    # Setup memory for the conversation
    # This stores past messages to maintain context
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True, # Important for ChatModels, as they expect message objects
        output_key='answer' # Specify output_key for ConversationalRetrievalChain
    )
    logger.debug("ConversationBufferMemory initialized.")

    # Define a custom prompt for the conversational retrieval chain
    # This guides the LLM on how to answer based on context and chat history
    # Using a template for clarity and flexibility
    custom_template = """You are an AI assistant for answering questions about uploaded PDF documents.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer concise and to the point.

Chat History:
{chat_history}

Context:
{context}

Question: {question}
Answer:"""
    
    # Create a PromptTemplate from the custom template
    qa_prompt = PromptTemplate(
        template=custom_template,
        input_variables=["chat_history", "context", "question"]
    )
    logger.debug("Custom prompt template created.")

    # Initialize the ConversationalRetrievalChain
    # This chain combines a retriever (for document chunks) with an LLM (for generating answers)
    # and memory (for conversation history).
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": qa_prompt}, # Pass the custom prompt to the combine_docs_chain
        return_source_documents=True # Optional: return the source documents used for the answer
    )
    logger.info("ConversationalRetrievalChain initialized successfully.")

    return conversation_chain

