"""
NLP Service for processing natural language requirements
"""

from typing import Dict, Any, List
import docx2txt
import aiofiles
from fastapi import UploadFile
import tempfile
import os

from app.rupp_integration.rupp_processor import FixedRUPPProcessor

class NLPService:
    def __init__(self):
        self.rupp_processor = FixedRUPPProcessor()
    
    def generate_rupp_snl(self, requirements_text: str) -> Dict[str, Any]:
        """
        Generate SNL using RUPP's template methodology
        """
        try:
            result = self.rupp_processor.generate_snl_from_text(requirements_text)
            return result
        except Exception as e:
            raise Exception(f"RUPP SNL generation failed: {str(e)}")
    
    def extract_actors(self, text: str) -> List[str]:
        """
        Extract actors from requirements text
        """
        try:
            return self.rupp_processor.identify_actors_enhanced(text)
        except Exception as e:
            raise Exception(f"Actor extraction failed: {str(e)}")
    
    def preprocess_text(self, text: str) -> str:
        """
        Apply NLP preprocessing to text
        """
        try:
            return self.rupp_processor.apply_preprocessing(text)
        except Exception as e:
            raise Exception(f"Text preprocessing failed: {str(e)}")
    
    def split_into_sentences(self, text: str) -> str:
        """
        Split text into numbered sentences
        """
        try:
            return self.rupp_processor.split_into_sentences(text)
        except Exception as e:
            raise Exception(f"Sentence splitting failed: {str(e)}")
    
    async def extract_text_from_file(self, file: UploadFile) -> str:
        """
        Extract text from uploaded document files
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process based on file type
                if file.filename.endswith(('.doc', '.docx')):
                    # Extract from Word document
                    extracted_text = docx2txt.process(temp_file_path)
                elif file.filename.endswith('.txt'):
                    # Read text file
                    with open(temp_file_path, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()
                else:
                    # Try to read as text
                    with open(temp_file_path, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()
                
                return extracted_text
            
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        except Exception as e:
            raise Exception(f"File text extraction failed: {str(e)}")
    
    def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """
        Analyze the complexity and structure of input text
        """
        try:
            # Basic statistics without spaCy dependency issues
            sentences = text.split('.')
            words = text.split()
            
            return {
                'character_count': len(text),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                'avg_chars_per_word': len(text) / len(words) if words else 0
            }
        
        except Exception as e:
            raise Exception(f"Text complexity analysis failed: {str(e)}")
