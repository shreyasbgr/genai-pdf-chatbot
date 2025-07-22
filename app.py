import streamlit as st
import os
from dotenv import load_dotenv
from src.pdf_processor import process_pdf
from src.vector_store import get_vectorstore
from src.chatbot import get_conversation_chain
from src.config import initialize_vertex_ai
import logging
from src.logger_config import setup_logging # Import the new logging setup function

# Load environment variables
load_dotenv()

# --- Initialize Logging ---
setup_logging() # Call the setup function
logger = logging.getLogger(__name__) # Get logger for app.py

st.set_page_config(page_title="PDF Chatbot with Vertex AI", page_icon="📚", layout="wide")

# Clean CSS for better chat styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        max-height: none !important;
        height: auto !important;
    }
    
    .stChatInputContainer {
        border-top: 1px solid #e0e0e0;
        padding-top: 1rem;
    }
    
    .pdf-info {
        background-color: #f0f8ff;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 4px solid #1f77b4;
    }
    
    /* Ensure chat messages can expand to full content */
    .stChatMessage .stMarkdown {
        max-height: none !important;
        height: auto !important;
        overflow: visible !important;
    }
    
    .stChatMessage .stMarkdown p {
        opacity: 1 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        max-height: none !important;
        height: auto !important;
    }
    
    /* Ensure text content is fully visible */
    .stChatMessage [data-testid="stMarkdownContainer"] {
        max-height: none !important;
        height: auto !important;
        overflow: visible !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.header("Chat with your PDF using Vertex AI 📚")
    logger.info("Application started.")
    
    # Sidebar with information and controls
    with st.sidebar:
        st.header("📋 Information")
        
        if st.session_state.get("pdf_processed", False):
            st.success("✅ PDF Ready")
            st.write(f"**File:** {st.session_state.get('current_pdf_name', 'Unknown')}")
            st.write(f"**Text Chunks:** {st.session_state.get('text_chunks_count', 0)}")
            st.write(f"**Messages:** {len(st.session_state.get('messages', []))}")
            
            # Model information
            st.subheader("🤖 Models Used")
            model_name = os.getenv("MODEL_NAME", "gemini-pro")
            embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
            st.write(f"**Language:** {model_name}")
            st.write(f"**Embeddings:** {embedding_model}")
            
            # Clear history button
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_chain = None # Reset conversation chain to re-init if PDF is same
                st.session_state.pdf_processed = False # Force reprocessing of PDF for clarity
                st.session_state.current_pdf_name = None
                st.session_state.text_chunks_count = 0
                logger.info("Chat history cleared.")
                st.rerun()
        else:
            st.info("📄 No PDF uploaded yet")
        
        st.divider()
        st.subheader("💡 Tips")
        st.write("• Upload a PDF to start chatting")
        st.write("• Ask specific questions about the content")
        st.write("• Use clear, concise language")
        st.write("• Try asking for summaries or explanations")
    
    # Initialize Vertex AI (only once)
    if "vertex_ai_initialized" not in st.session_state:
        try:
            logger.info("Initializing Vertex AI...")
            initialize_vertex_ai()
            st.session_state.vertex_ai_initialized = True
            logger.info("Vertex AI successfully initialized.")
        except ValueError as e:
            logger.error(f"Configuration Error during Vertex AI initialization: {e}", exc_info=True)
            st.error(f"Configuration Error: {e}")
            st.info("Please set up your Google Cloud project configuration in the .env file.")
            return
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}", exc_info=True)
            st.error(f"Failed to initialize Vertex AI: {e}")
            st.info("Please check your Google Cloud credentials and project configuration.")
            return
    
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
        logger.info("Initialized 'messages' in session state.")
    if "conversation_chain" not in st.session_state:
        st.session_state.conversation_chain = None
        logger.info("Initialized 'conversation_chain' in session state.")
    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False
        logger.info("Initialized 'pdf_processed' in session state.")
    if "current_pdf_name" not in st.session_state:
        st.session_state.current_pdf_name = None
        logger.info("Initialized 'current_pdf_name' in session state.")
    if "text_chunks_count" not in st.session_state:
        st.session_state.text_chunks_count = 0
        logger.info("Initialized 'text_chunks_count' in session state.")
    if "generating_response" not in st.session_state:
        st.session_state.generating_response = False
        logger.info("Initialized 'generating_response' in session state.")


    # File upload
    pdf_file = st.file_uploader("Upload your PDF", type=["pdf"])
    
    # Check if a new PDF is uploaded
    if pdf_file:
        pdf_name = pdf_file.name
        
        # Only process if it's a new PDF or first time
        if not st.session_state.pdf_processed or st.session_state.current_pdf_name != pdf_name:
            logger.info(f"New PDF uploaded or different PDF detected: {pdf_name}. Starting processing...")
            try:
                # Clear previous chat history for new PDF
                if st.session_state.current_pdf_name != pdf_name:
                    st.session_state.messages = []
                    st.session_state.conversation_chain = None # Reset chain for new PDF
                    logger.info("Cleared chat history for new PDF.")
                
                # Process PDF and create vector store
                with st.spinner(f"Processing PDF '{pdf_name}'..."):
                    text_chunks = process_pdf(pdf_file)
                    st.session_state.text_chunks_count = len(text_chunks)
                    logger.info(f"PDF '{pdf_name}' processed into {len(text_chunks)} chunks.")
                
                with st.spinner("Creating embeddings..."):
                    vectorstore = get_vectorstore(text_chunks)
                    logger.info(f"Embeddings created for '{pdf_name}'.")
                
                # Create conversation chain and store in session state
                st.session_state.conversation_chain = get_conversation_chain(vectorstore)
                st.session_state.pdf_processed = True
                st.session_state.current_pdf_name = pdf_name
                
                st.success(f"PDF '{pdf_name}' processed successfully! You can now ask questions.")
                logger.info(f"PDF '{pdf_name}' successfully processed and conversation chain created.")
                st.rerun() 
            except Exception as e:
                logger.error(f"Error processing PDF '{pdf_name}': {e}", exc_info=True)
                st.error(f"Error processing PDF: {e}")
                st.session_state.pdf_processed = False
                return
    
    # Only show chat interface if PDF is processed
    if st.session_state.pdf_processed and st.session_state.conversation_chain:
        st.markdown(f"""
        <div class="pdf-info">
            📄 Currently chatting with: <strong>{st.session_state.current_pdf_name}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask a question about your PDF:"):
            logger.info(f"User query received: '{prompt}'")
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun() 
            
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            if not st.session_state.get("generating_response", False):
                st.session_state.generating_response = True
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            logger.info(f"Invoking conversation chain for query: '{st.session_state.messages[-1]['content']}'")
                            response = st.session_state.conversation_chain.invoke({"question": st.session_state.messages[-1]["content"]})
                            
                            if response and "answer" in response and response["answer"].strip():
                                answer = response["answer"].strip()
                                st.session_state.messages.append({"role": "assistant", "content": answer})
                                logger.info("Assistant response successfully generated.")
                            else:
                                error_msg = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                logger.warning("Assistant generated an empty or invalid response.")
                                
                        except Exception as e:
                            logger.error(f"Error during conversation chain invocation: {e}", exc_info=True)
                            error_msg = f"I encountered an error while processing your question: {str(e)}"
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        finally:
                            st.session_state.generating_response = False
                            st.rerun()
    
    elif pdf_file is None:
        st.info("👆 Please upload a PDF file to start chatting!")
        logger.info("Awaiting PDF upload.")

if __name__ == "__main__":
    main()