"""
Document processing utilities for InsightGPT
Handles PDF, DOCX, and text file uploads with text extraction and chunking
"""
import io
from typing import List, Tuple, Optional
import PyPDF2
from docx import Document
import streamlit as st
from config import Config


class DocumentProcessor:
    """Process various document formats and extract text"""
    
    def __init__(self):
        self.config = Config()
    
    def process_uploaded_file(self, uploaded_file) -> Tuple[str, bool]:
        """
        Process uploaded file and extract text
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (extracted_text, success_flag)
        """
        try:
            file_type = uploaded_file.name.split('.')[-1].lower()
            
            # Check file size
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > self.config.MAX_FILE_SIZE_MB:
                st.error(f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({self.config.MAX_FILE_SIZE_MB} MB)")
                return "", False
            
            if file_type == 'pdf':
                text = self._extract_from_pdf(uploaded_file)
            elif file_type in ['docx', 'doc']:
                text = self._extract_from_docx(uploaded_file)
            elif file_type == 'txt':
                text = self._extract_from_txt(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_type}")
                return "", False
            
            if not text.strip():
                st.error("No text could be extracted from the file.")
                return "", False
            
            return text, True
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return "", False
    
    def _extract_from_pdf(self, file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _extract_from_docx(self, file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file)
            text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def _extract_from_txt(self, file) -> str:
        """Extract text from TXT file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    file.seek(0)
                    text = file.read().decode(encoding)
                    return text.strip()
                except UnicodeDecodeError:
                    continue
            
            raise Exception("Could not decode text file with supported encodings")
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, 
                   overlap: Optional[int] = None) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.config.CHUNK_SIZE
        overlap = overlap or self.config.CHUNK_OVERLAP
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence ending punctuation
                for punct in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    last_punct = text[start:end].rfind(punct)
                    if last_punct > chunk_size * 0.5:  # At least 50% of chunk size
                        end = start + last_punct + len(punct)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def get_text_stats(self, text: str) -> dict:
        """
        Get statistics about the text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        words = text.split()
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return {
            'characters': len(text),
            'words': len(words),
            'sentences': len(sentences),
            'paragraphs': len([p for p in text.split('\n\n') if p.strip()])
        }


def validate_text_input(text: str) -> Tuple[bool, str]:
    """
    Validate text input
    
    Args:
        text: Input text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Text is empty"
    
    if len(text.strip()) < 50:
        return False, "Text is too short (minimum 50 characters)"
    
    return True, ""
