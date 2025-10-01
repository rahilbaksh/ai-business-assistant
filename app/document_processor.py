import PyPDF2
import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from utils import setup_logging

class DocumentProcessor:
    def __init__(self):
        self.logger = setup_logging()
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,  # Increased for better context
            chunk_overlap=200,  # Increased overlap
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]  # Better separators
        )
        
    def read_pdf(self, file_path):
        """Read text from PDF file with better parsing"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker for context
                        text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
            
            self.logger.info(f"Read PDF with {len(pdf_reader.pages)} pages")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error reading PDF: {e}")
            return ""
    
    def read_text_file(self, file_path):
        """Read text from .txt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.logger.info(f"Read text file: {file_path}")
            return content
        except Exception as e:
            self.logger.error(f"Error reading text file: {e}")
            return ""
    
    def process_business_document(self, file_path):
        """Specialized processor for business reports with better chunking"""
        content = self.process_file(file_path)
        if not content:
            return None
        
        # Use smarter chunking for business documents
        chunks = self.text_splitter.split_text(content)
        
        # Enhance chunks with metadata about their content type
        enhanced_chunks = []
        for chunk in chunks:
            chunk_lower = chunk.lower()
            chunk_type = "general"
            
            if any(word in chunk_lower for word in ['lawsuit', 'litigation', 'talc', 'opioid', 'legal']):
                chunk_type = "legal"
            elif any(word in chunk_lower for word in ['sales', 'revenue', 'growth', 'billion', 'million']):
                chunk_type = "financial"
            elif any(word in chunk_lower for word in ['risk', 'competition', 'patent']):
                chunk_type = "risk"
            elif any(word in chunk_lower for word in ['research', 'development', 'r&d', 'pipeline']):
                chunk_type = "innovation"
                
            enhanced_chunk = f"[{chunk_type.upper()} SECTION] {chunk}"
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def process_file(self, file_path):
        """Process any supported file type"""
        file_type = file_path.lower().split('.')[-1]
        
        if file_type == 'pdf':
            content = self.read_pdf(file_path)
        elif file_type == 'txt':
            content = self.read_text_file(file_path)
        else:
            self.logger.warning(f"Unsupported file type: {file_type}")
            return None
            
        return content