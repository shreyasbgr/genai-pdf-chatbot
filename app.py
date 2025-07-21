import streamlit as st
import os
from dotenv import load_dotenv
from src.pdf_processor import process_pdf
from src.vector_store import get_vectorstore
from src.chatbot import get_conversation_chain
from src.config import initialize_vertex_ai

# Load environment variables
load_dotenv()

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
            initialize_vertex_ai()
            st.session_state.vertex_ai_initialized = True
        except ValueError as e:
            st.error(f"Configuration Error: {e}")
            st.info("Please set up your Google Cloud project configuration in the .env file")
            return
        except Exception as e:
            st.error(f"Failed to initialize Vertex AI: {e}")
            st.info("Please check your Google Cloud credentials and project configuration")
            return
    
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_chain" not in st.session_state:
        st.session_state.conversation_chain = None
    if "pdf_processed" not in st.session_state:
        st.session_state.pdf_processed = False
    if "current_pdf_name" not in st.session_state:
        st.session_state.current_pdf_name = None
    if "text_chunks_count" not in st.session_state:
        st.session_state.text_chunks_count = 0
    # Removed "processing_question" and "last_question" as they are not needed with the new flow

    
    # File upload
    pdf_file = st.file_uploader("Upload your PDF", type=["pdf"])
    
    # Check if a new PDF is uploaded
    if pdf_file:
        pdf_name = pdf_file.name
        
        # Only process if it's a new PDF or first time
        if not st.session_state.pdf_processed or st.session_state.current_pdf_name != pdf_name:
            try:
                # Clear previous chat history for new PDF
                if st.session_state.current_pdf_name != pdf_name:
                    st.session_state.messages = []
                
                # Process PDF and create vector store
                with st.spinner("Processing PDF..."):
                    text_chunks = process_pdf(pdf_file)
                    st.session_state.text_chunks_count = len(text_chunks)
                
                with st.spinner("Creating embeddings..."):
                    vectorstore = get_vectorstore(text_chunks)
                
                # Create conversation chain and store in session state
                st.session_state.conversation_chain = get_conversation_chain(vectorstore)
                st.session_state.pdf_processed = True
                st.session_state.current_pdf_name = pdf_name
                
                st.success("PDF processed successfully! You can now ask questions.")
                # Rerun to clear the file uploader and show the chat input cleanly
                st.rerun() 
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
                st.session_state.pdf_processed = False
                return
    
    # Only show chat interface if PDF is processed
    if st.session_state.pdf_processed and st.session_state.conversation_chain:
        # Display current PDF name with custom styling
        st.markdown(f"""
        <div class="pdf-info">
            📄 Currently chatting with: <strong>{st.session_state.current_pdf_name}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chat messages using Streamlit's built-in components
        # This loop now just displays what's in st.session_state.messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Handle new user input
        if prompt := st.chat_input("Ask a question about your PDF:"):
            # 1. Immediately add user message to chat history and display it
            st.session_state.messages.append({"role": "user", "content": prompt})
            # This rerun makes the user's message appear instantly
            st.rerun() 
            
        # This block executes AFTER the prompt is added and the rerun happened above
        # It's separated so the assistant's response is generated in the *next* script run
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            # Check if the last message is from the user and we haven't processed it yet
            if not st.session_state.get("generating_response", False):
                st.session_state.generating_response = True # Flag to prevent re-triggering generation
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = st.session_state.conversation_chain.invoke({"question": st.session_state.messages[-1]["content"]})
                            
                            if response and "answer" in response and response["answer"].strip():
                                answer = response["answer"].strip()
                                st.session_state.messages.append({"role": "assistant", "content": answer})
                            else:
                                error_msg = "I apologize, but I couldn't generate a response. Please try rephrasing your question."
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                
                        except Exception as e:
                            error_msg = f"I encountered an error while processing your question: {str(e)}"
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        finally:
                            st.session_state.generating_response = False # Reset flag
                            st.rerun() # Rerun to display the assistant's response
    
    elif pdf_file is None:
        st.info("👆 Please upload a PDF file to start chatting!")

if __name__ == "__main__":
    main()