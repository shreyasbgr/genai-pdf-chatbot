"""
Document Processing Module

This module handles PDF document processing, including text extraction,
validation, and chunking for the PDF RAG Chatbot application.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import PyPDF2
import config


@dataclass
class TextChunk:
    """Represents a chunk of text extracted from a document."""
    content: str
    page_number: int
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]


class DocumentProcessor:
    """Handles PDF document processing operations."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.chunk_size = config.MAX_CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def validate_pdf(self, file) -> bool:
        """
        Validate that the uploaded file is a valid PDF.
        
        Args:
            file: The uploaded file object
            
        Returns:
            bool: True if the file is a valid PDF, False otherwise
        """
        try:
            # Try to open the file with PyPDF2
            reader = PyPDF2.PdfReader(file)
            # Check if the file has at least one page
            if len(reader.pages) > 0:
                return True
            return False
        except Exception as e:
            print(f"PDF validation error: {e}")
            return False
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            str: Extracted text content
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: The text to chunk
            metadata: Metadata about the document
            
        Returns:
            List[TextChunk]: List of text chunks
        """
        chunks = []
        text_length = len(text)
        
        # If text is shorter than chunk size, return it as a single chunk
        if text_length <= self.chunk_size:
            chunks.append(TextChunk(
                content=text,
                page_number=metadata.get("page_number", 0),
                chunk_index=0,
                start_char=0,
                end_char=text_length,
                metadata=metadata
            ))
            return chunks
        
        # Split text into overlapping chunks
        start = 0
        chunk_index = 0
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # If not at the end of the text, try to find a good break point
            if end < text_length:
                # Try to find a period, question mark, or exclamation point followed by a space
                for i in range(end - 1, start + self.chunk_size // 2, -1):
                    if i < text_length and text[i] in ['.', '!', '?'] and (i + 1 >= text_length or text[i + 1].isspace()):
                        end = i + 1
                        break
            
            chunk_text = text[start:end]
            
            # Create a chunk with metadata
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = chunk_index
            
            chunks.append(TextChunk(
                content=chunk_text,
                page_number=metadata.get("page_number", 0),
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                metadata=chunk_metadata
            ))
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
            
            chunk_index += 1
        
        return chunks
    
    def process_document(self, file_path: str, document_name: str) -> List[TextChunk]:
        """
        Process a PDF document: extract text and split into chunks.
        
        Args:
            file_path: Path to the PDF file
            document_name: Name of the document
            
        Returns:
            List[TextChunk]: List of text chunks from the document
        """
        # Extract text from PDF
        text = self.extract_text_from_pdf(file_path)
        
        if not text:
            return []
        
        # Create document metadata
        metadata = {
            "source": document_name,
            "file_path": file_path,
        }
        
        # Chunk the text
        chunks = self.chunk_text(text, metadata)
        
        return chunks