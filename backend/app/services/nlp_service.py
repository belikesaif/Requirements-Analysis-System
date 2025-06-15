"""
NLP Service for processing natural language requirements
"""

from typing import Dict, Any, List
import docx2txt
import aiofiles
from fastapi import UploadFile
import tempfile
import os

from app.rupp_integration.rupp_processor import RUPPProcessor

class NLPService:
    def __init__(self):
        self.rupp_processor = RUPPProcessor()
    
    def generate_rupp_snl(self, requirements_text: str) -> Dict[str, Any]:
        """
        Generate SNL using RUPP's template methodology
        """
        try:
            result = self.rupp_processor.generate_snl(requirements_text)
            return result
        except Exception as e:
            raise Exception(f"RUPP SNL generation failed: {str(e)}")
    
    def extract_actors(self, text: str) -> List[str]:
        """
        Extract actors from requirements text
        """
        try:
            return self.rupp_processor.identify_actors_with_actions(text)
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
            doc = self.rupp_processor.nlp(text)
            
            # Basic statistics
            sentences = list(doc.sents)
            tokens = list(doc)
            
            # POS tag distribution
            pos_counts = {}
            for token in tokens:
                pos = token.pos_
                pos_counts[pos] = pos_counts.get(pos, 0) + 1
            
            # Entity recognition
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            return {
                'sentence_count': len(sentences),
                'token_count': len(tokens),
                'average_sentence_length': len(tokens) / len(sentences) if sentences else 0,
                'pos_distribution': pos_counts,
                'entities': entities,
                'complexity_score': self._calculate_complexity_score(doc)
            }
        
        except Exception as e:
            raise Exception(f"Text analysis failed: {str(e)}")
    
    def _calculate_complexity_score(self, doc) -> float:
        """
        Calculate a simple complexity score based on sentence structure
        """
        try:
            total_score = 0
            sentence_count = 0
            
            for sent in doc.sents:
                sentence_count += 1
                
                # Factors that increase complexity
                verb_count = sum(1 for token in sent if token.pos_ == "VERB")
                noun_count = sum(1 for token in sent if token.pos_ == "NOUN")
                adj_count = sum(1 for token in sent if token.pos_ == "ADJ")
                
                # Dependency complexity
                dep_complexity = len(set(token.dep_ for token in sent))
                
                sentence_score = (verb_count + noun_count + adj_count + dep_complexity) / len(sent)
                total_score += sentence_score
            
            return total_score / sentence_count if sentence_count > 0 else 0
        
        except Exception as e:
            return 0.0
