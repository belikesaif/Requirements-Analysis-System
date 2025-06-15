"""
Simplified RUPP processor without external dependencies
"""

import re
from typing import List, Dict, Any

class SimpleRUPPProcessor:
    def __init__(self):
        self.corrections = {
            'librarian': 'NOUN',
        }
        self.abbreviation_mapping = {
            'guest user': 'guest_user',
            'into': 'in to'
        }
        
    def split_into_sentences(self, paragraph: str) -> str:
        """Split the paragraph into sentences using regular expressions"""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', paragraph)
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences, start=1):
            if sentence.strip():
                formatted_sentences.append(f"{i}. {sentence}")
        
        return '\n'.join(formatted_sentences)
    
    def split_and_add_full_stop(self, sentence: str) -> str:
        """Split sentence on 'and' and add full stop"""
        if " and " in sentence:
            before_and, after_and = sentence.split("and", 1)
            before_and = before_and.strip() + '. '
            after_and = after_and.strip()
            return before_and + after_and
        else:
            return sentence + '. ' if not sentence.endswith('.') else sentence + ' '
    
    def replace_and(self, input_string: str) -> str:
        """Replace & with 'and'"""
        words = input_string.split()
        replaced_words = [word.replace("&", "and") for word in words]
        return ' '.join(replaced_words)
    
    def add_space_after_period(self, sentence: str) -> str:
        """Add space after periods"""
        result = ''
        for char in sentence:
            result += char
            if char == '.':
                result += ' '
        return result
    
    def join_abbreviation(self, text: str, abbreviation_mapping: Dict[str, str]) -> str:
        """Replace abbreviations with mapped values"""
        for word, replacement in abbreviation_mapping.items():
            if word in text:
                text = text.replace(word, replacement)
        return text
    
    def apply_preprocessing(self, text: str) -> str:
        """Apply complete preprocessing pipeline"""
        # Apply text lowercasing
        lowercased_paragraph = text.lower()
        and_replace = self.replace_and(lowercased_paragraph)
          # Expand contractions manually for common cases
        expanded_paragraph = and_replace.replace("can't", "cannot").replace("won't", "will not").replace("don't", "do not").replace("isn't", "is not").replace("aren't", "are not").replace("wasn't", "was not").replace("weren't", "were not")
          # Remove punctuation and special characters (except full stop)
        remove_punctuation = re.sub(r'[^a-zA-Z0-9\s\.,]', '', expanded_paragraph)
        
        # Remove extra whitespace
        remove_extra_whitespace = re.sub(r'\s+', ' ', remove_punctuation).strip()
        
        normalized_text = self.join_abbreviation(remove_extra_whitespace, self.abbreviation_mapping)
        
        split_and_sentences = self.split_and_add_full_stop(normalized_text)
        
        full_stop_space = self.add_space_after_period(split_and_sentences)
        
        return full_stop_space
    
    def identify_actors_simple(self, description: str) -> List[str]:
        """Simple actor identification using keywords"""
        common_actors = ['member', 'user', 'librarian', 'admin', 'administrator', 'customer', 'guest', 'system']
        actors = set()
        
        words = description.lower().split()
        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if clean_word in common_actors:
                actors.add(clean_word)
        
        return list(actors)
    
    def generate_snl(self, requirements_text: str) -> Dict[str, Any]:
        """Generate SNL using simplified RUPP's template methodology"""
        try:
            # Apply preprocessing
            preprocessed_text = self.apply_preprocessing(requirements_text)
            
            # Identify actors
            actors = self.identify_actors_simple(requirements_text)
            
            # Split into sentences
            sentences = [s.strip() for s in preprocessed_text.split('.') if s.strip()]
            
            # Generate RUPP-style requirements
            rupp_requirements = []
            
            for sentence in sentences:
                if not sentence:
                    continue
                    
                # Check for different patterns and apply templates
                rupp_req = self.apply_rupp_templates(sentence, actors)
                if rupp_req:
                    rupp_requirements.append(rupp_req)
            
            # Format results
            formatted_sentences = self.split_into_sentences('\n'.join(rupp_requirements))
            
            return {
                'snl_text': '\n'.join(rupp_requirements),
                'actors': actors,
                'preprocessed_text': preprocessed_text,
                'sentences_count': len(rupp_requirements),
                'formatted_sentences': formatted_sentences
            }
        
        except Exception as e:
            return {
                'snl_text': f"Error processing requirements: {str(e)}",
                'actors': [],
                'preprocessed_text': requirements_text,
                'sentences_count': 0,
                'formatted_sentences': ""
            }
    
    def apply_rupp_templates(self, sentence: str, actors: List[str]) -> str:
        """Apply RUPP templates to sentence"""
        sentence = sentence.strip().lower()
        
        # Template 1: If-then statements
        if "if" in sentence and "then" in sentence:
            return self.process_if_then_template(sentence)
        
        # Template 2: When statements
        if sentence.startswith("when"):
            return self.process_when_template(sentence)
        
        # Template 3: System actions
        if "system" in sentence and any(verb in sentence for verb in ["displays", "shows", "validates", "processes"]):
            return self.process_system_action_template(sentence)
        
        # Template 4: User actions
        for actor in actors:
            if actor in sentence and actor != "system":
                return self.process_user_action_template(sentence, actor)
        
        # Default template
        return f"The system shall be able to {sentence}."
    
    def process_if_then_template(self, sentence: str) -> str:
        """Process if-then conditional statements"""
        try:
            if_part = sentence.split("if")[1].split("then")[0].strip()
            then_part = sentence.split("then")[1].strip()
            return f"If {if_part}, then the system shall be able to {then_part}."
        except:
            return f"The system shall handle conditional logic for {sentence}."
    
    def process_when_template(self, sentence: str) -> str:
        """Process when statements"""
        try:
            when_part = sentence.replace("when", "").strip()
            return f"When {when_part}, the system shall be able to respond appropriately."
        except:
            return f"The system shall handle the scenario: {sentence}."
    
    def process_system_action_template(self, sentence: str) -> str:
        """Process system action statements"""
        # Extract the action verb
        action_verbs = ["displays", "shows", "validates", "processes", "stores", "retrieves"]
        for verb in action_verbs:
            if verb in sentence:
                action = sentence.split(verb)[1].strip() if verb in sentence else "perform the required action"
                return f"The system shall be able to {verb} {action}."
        
        return f"The system shall be able to {sentence}."
    
    def process_user_action_template(self, sentence: str, actor: str) -> str:
        """Process user action statements"""
        # Extract action after the actor
        try:
            actor_index = sentence.find(actor)
            if actor_index >= 0:
                action_part = sentence[actor_index + len(actor):].strip()
                # Remove common connecting words
                action_part = re.sub(r'^(clicks|enters|types|selects|chooses)', r'\1', action_part)
                return f"The system shall provide {actor} with the ability to {action_part}."
        except:
            pass
        
        return f"The system shall provide {actor} with the ability to {sentence}."
