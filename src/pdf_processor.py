import io
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document # Import Document class
import tempfile # Import tempfile for secure temporary file creation
import os # Import os for file operations

def process_pdf(pdf_file) -> List[Document]: # Change return type hint to List[Document]
    """
    Process a PDF file and split it into chunks.

    Args:
        pdf_file: The uploaded PDF file (st.UploadedFile object)

    Returns:
        List of text chunks (LangChain Document objects)
    """
    # Create a BytesIO object from the uploaded file
    pdf_bytes = io.BytesIO(pdf_file.getvalue())

    # Use tempfile to create a secure temporary file
    # This ensures a unique file name and proper cleanup,
    # which is crucial for multi-user environments like Streamlit Cloud.
    tmp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes.getvalue())
            tmp_file_path = tmp_file.name
        
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
    finally:
        # Ensure the temporary file is deleted even if an error occurs
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    
    return chunks