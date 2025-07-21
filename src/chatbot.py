import os
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
from src.config import get_project_config, get_model_config

# Load environment variables
load_dotenv()

def get_conversation_chain(vectorstore):
    """
    Create a conversation chain for the chatbot.
    
    Args:
        vectorstore: Vector store containing document embeddings
        
    Returns:
        Conversation chain
    """
    # Get configuration from .env file
    project_id, location = get_project_config()
    model_config = get_model_config()
    
    print(f"Using language model from .env: {model_config['language_model']}")
    
    # Initialize the language model with Vertex AI
    llm = VertexAI(
        model_name=model_config['language_model'],
        temperature=model_config['temperature'],
        project=project_id,
        location=location,
        max_output_tokens=model_config['max_output_tokens']
    )
    
    # Create memory for conversation
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
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
    
    # Create the conversation chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}), # k=5 is a good starting point for large docs
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT}
    )
    
    return conversation_chain