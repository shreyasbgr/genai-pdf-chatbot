import io
import os # Import os for file path management
import tempfile # Import tempfile for secure temporary file handling
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import logging # Import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

def process_pdf(pdf_file) -> List[str]:
    """
    Process a PDF file and split it into chunks.
    
    Args:
        pdf_file: The uploaded PDF file (Streamlit UploadedFile object or file path).
        
    Returns:
        List of text chunks (documents).
        
    Raises:
        ValueError: If the input pdf_file is invalid.
        FileNotFoundError: If a file path is provided but the file does not exist.
        Exception: For any other errors during PDF loading or splitting.
    """
    if pdf_file is None:
        logger.error("No PDF file provided to process_pdf function.")
        raise ValueError("PDF file cannot be None.")

    temp_file_path = None
    loader = None
    
    try:
        if hasattr(pdf_file, "read"): # Check if it's a file-like object (e.g., Streamlit UploadedFile)
            # Create a temporary file to save the uploaded PDF content
            # 'delete=False' allows us to get the path before it's deleted
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_file.read())
                temp_file_path = temp_file.name
            logger.info(f"Uploaded PDF temporarily saved to: {temp_file_path}")
            loader = PyPDFLoader(temp_file_path)
        elif isinstance(pdf_file, str): # Assume it's a file path string
            if not os.path.exists(pdf_file):
                logger.error(f"PDF file not found at path: {pdf_file}")
                raise FileNotFoundError(f"PDF file not found at: {pdf_file}")
            temp_file_path = pdf_file # In this case, it's not a temp file created by us
            loader = PyPDFLoader(pdf_file)
        else:
            logger.error(f"Invalid pdf_file type provided: {type(pdf_file)}")
            raise ValueError("Invalid PDF file input. Expected a file-like object or a path string.")

        logger.info(f"Loading documents from PDF: {temp_file_path or pdf_file.name}")
        documents = loader.load()
        if not documents:
            logger.warning(f"No documents loaded from PDF: {temp_file_path or pdf_file.name}. It might be empty or unreadable.")
            # Depending on desired behavior, you might want to raise an error here
            # For now, we'll let it proceed, and it will result in 0 chunks
        logger.info(f"Loaded {len(documents)} pages/documents from PDF.")
        
        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        logger.info(f"Splitting documents into chunks (size: 1000, overlap: 200).")
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            logger.warning("No text chunks generated from the PDF. Document might be empty or contain only images.")
        else:
            logger.info(f"Successfully generated {len(chunks)} text chunks.")
            
        return chunks
    
    except Exception as e:
        logger.critical(f"An unexpected error occurred during PDF processing: {e}", exc_info=True)
        # Re-raise the exception to be caught by the calling function (e.g., in app.py)
        raise
    finally:
        # Clean up the temporary file if it was created
        if temp_file_path and hasattr(pdf_file, "read") and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Temporary PDF file removed: {temp_file_path}")
            except OSError as e:
                logger.warning(f"Could not remove temporary PDF file {temp_file_path}: {e}")