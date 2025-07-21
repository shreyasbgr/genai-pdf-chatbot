import io
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

def process_pdf(pdf_file) -> List[str]:
    """
    Process a PDF file and split it into chunks.
    
    Args:
        pdf_file: The uploaded PDF file
        
    Returns:
        List of text chunks
    """
    # Save the uploaded file temporarily
    if hasattr(pdf_file, "name"):
        # Create a temporary file
        with open("temp_pdf.pdf", "wb") as f:
            f.write(pdf_file.getvalue())
        
        # Load the PDF
        loader = PyPDFLoader("temp_pdf.pdf")
    else:
        # If it's a file path
        loader = PyPDFLoader(pdf_file)
    
    # Load the documents
    documents = loader.load()
    
    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    
    return chunks