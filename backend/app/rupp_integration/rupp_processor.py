"""
Fixed Enhanced RUPP Template-based SNL Generator
Clean version with proper actor identification
"""

import spacy
import re
import textacy
from typing import List, Dict, Any

class FixedRUPPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            # Fallback to basic processing if spaCy model not available
            self.nlp = None
        
        self.corrections = {
            'librarian': 'NOUN',
        }
        self.abbreviation_mapping = {
            'guest user': 'guest_user',
            'into': 'in to'
        }
        
    def split_into_sentences(self, paragraph: str) -> str:
        """Split the paragraph into sentences using regular expressions"""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+', paragraph)
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences, start=1):
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:
                formatted_sentences.append(f"{i}. {sentence}")
        
        return '\n'.join(formatted_sentences)
    
    def apply_preprocessing(self, text: str) -> str:
        """Apply complete preprocessing pipeline"""
        # Basic text cleaning
        text = text.lower()
        text = text.replace("&", "and")
        
        # Expand common contractions
        contractions = {
            "can't": "cannot", "won't": "will not", "don't": "do not",
            "isn't": "is not", "aren't": "are not", "wasn't": "was not",
            "weren't": "were not", "haven't": "have not", "hasn't": "has not",
            "wouldn't": "would not", "shouldn't": "should not", "couldn't": "could not"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        # Remove excessive punctuation but keep periods
        text = re.sub(r'[^\w\s\.,\-]', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def identify_actors_enhanced(self, description: str) -> List[str]:
        """Enhanced actor identification - ONLY valid human actors"""
        actors = set()
        
        # STRICT list of valid actors only
        valid_actors = {'system', 'user', 'administrator', 'librarian', 'member', 'guest'}
        
        # Extract words and check against valid actors only
        words = description.lower().split()
        for word in words:
            clean_word = re.sub(r'[^a-z]', '', word)
            if clean_word in valid_actors:
                actors.add(clean_word)
        
        # Direct keyword mapping
        text_lower = description.lower()
        if 'system' in text_lower:
            actors.add('system')
        if 'user' in text_lower:
            actors.add('user')
        if 'member' in text_lower:
            actors.add('member')
        if 'librarian' in text_lower:
            actors.add('librarian')
        if 'administrator' in text_lower or 'admin' in text_lower:
            actors.add('administrator')
        if 'guest' in text_lower:
            actors.add('guest')
            
        return sorted(list(actors))

    def extract_sentences_comprehensive(self, text: str) -> List[str]:
        """Extract all meaningful sentences from text with maximum coverage"""
        sentences = []
        
        # Primary split by periods, exclamation marks, and question marks
        period_splits = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+', text)
        
        for sentence in period_splits:
            sentence = sentence.strip()
            if len(sentence) > 3:  # Very low threshold for maximum coverage
                sentences.append(sentence)
        
        # Enhanced processing for additional sentence extraction
        enhanced_sentences = []
        for sentence in sentences:
            enhanced_sentences.append(sentence)
            
            # Split by semicolons
            if ';' in sentence:
                semi_splits = [s.strip() for s in sentence.split(';') if s.strip() and len(s.strip()) > 3]
                enhanced_sentences.extend(semi_splits)
            
            # Aggressive compound sentence splitting with 'and'
            if ' and ' in sentence.lower():
                # Look for action verbs that indicate separate requirements
                action_verbs = ['clicks', 'enters', 'displays', 'shows', 'checks', 'validates', 
                               'asks', 'opens', 'closes', 'selects', 'returns', 'issues', 'reserves',
                               'adds', 'removes', 'updates', 'stores', 'retrieves', 'prompts']
                
                if any(verb in sentence.lower() for verb in action_verbs):
                    and_parts = sentence.split(' and ')
                    current_subject = None
                    
                    # Extract subject from first part
                    first_part = and_parts[0].lower()
                    if 'system' in first_part:
                        current_subject = 'The system'
                    elif 'member' in first_part:
                        current_subject = 'The member'
                    elif 'user' in first_part:
                        current_subject = 'The user'
                    elif 'librarian' in first_part:
                        current_subject = 'The librarian'
                    elif 'administrator' in first_part:
                        current_subject = 'The administrator'
                    elif 'guest' in first_part:
                        current_subject = 'The guest'
                    
                    for i, part in enumerate(and_parts):
                        part = part.strip()
                        if len(part) > 3:
                            if i == 0:
                                enhanced_sentences.append(part)
                            elif current_subject and not part.lower().startswith(('the ', 'a ', 'an ')):
                                enhanced_sentences.append(f"{current_subject} {part}")
                            else:
                                enhanced_sentences.append(part)
            
            # Split complex sentences with multiple clauses
            if ' then ' in sentence.lower():
                then_parts = sentence.split(' then ')
                for part in then_parts:
                    part = part.strip()
                    if len(part) > 3:
                        enhanced_sentences.append(part)
        
        # Remove duplicates while preserving order
        unique_sentences = list(dict.fromkeys(enhanced_sentences))
        
        # Final filtering with very permissive criteria
        final_sentences = []
        for sentence in unique_sentences:
            sentence = sentence.strip()
            if (len(sentence) > 3 and  # Minimum viable length
                not sentence.isdigit() and 
                any(char.isalpha() for char in sentence) and
                # More comprehensive filtering
                not any(skip_phrase in sentence.lower() for skip_phrase in [
                    'the details include', 'details include', 'include the total',
                    'total number of', 'date of issue', 'return date', 'fine to be paid'
                ])):
                final_sentences.append(sentence)
        
        return final_sentences

    def apply_rupp_templates_enhanced(self, sentence: str, actors: List[str]) -> List[str]:
        """Apply enhanced RUPP templates to generate multiple requirements"""
        requirements = []
        sentence = sentence.strip()
        sentence_lower = sentence.lower()
        
        # Template 1: Conditional statements (If-then)
        if 'if' in sentence_lower and ('then' in sentence_lower or ',' in sentence):
            req = self.process_conditional_template(sentence)
            if req:
                requirements.append(req)
        
        # Template 2: When statements
        elif sentence_lower.startswith('when '):
            req = self.process_when_template(sentence)
            if req:
                requirements.append(req)
        
        # Template 3: System capabilities (more aggressive detection)
        elif any(verb in sentence_lower for verb in ['display', 'show', 'validate', 'process', 'store', 'retrieve', 
                                                    'calculate', 'generate', 'check', 'ask', 'prompt', 'open', 
                                                    'close', 'update', 'enter', 'select']):
            req = self.process_system_capability_template(sentence)
            if req:
                requirements.append(req)
        
        # Template 4: User actions (more comprehensive)
        elif (any(actor in sentence_lower for actor in actors if actor != 'system') or
              any(action in sentence_lower for action in ['click', 'enter', 'select', 'view', 'browse', 'search'])):
            req = self.process_user_action_template(sentence, actors)
            if req:
                requirements.append(req)
        
        # Template 5: Modal statements
        elif any(modal in sentence_lower for modal in ['should', 'must', 'can', 'will', 'shall', 'may']):
            req = self.process_modal_template(sentence)
            if req:
                requirements.append(req)
        
        # Template 6: Feature statements
        elif any(feature in sentence_lower for feature in ['feature', 'function', 'capability', 'service']):
            req = self.process_feature_template(sentence)
            if req:
                requirements.append(req)
        
        # Template 7: State/condition statements
        elif any(state in sentence_lower for state in ['available', 'ready', 'logged in', 'valid', 'correct']):
            req = self.process_state_template(sentence)
            if req:
                requirements.append(req)
        
        # Template 8: Data validation statements
        elif any(validation in sentence_lower for validation in ['validate', 'check', 'verify', 'confirm']):
            req = self.process_validation_template(sentence)
            if req:
                requirements.append(req)
        
        # Default template if no specific template matches
        else:
            req = self.process_default_template(sentence, actors)
            if req:
                requirements.append(req)
        
        return requirements

    def process_conditional_template(self, sentence: str) -> str:
        """Process conditional if-then statements"""
        try:
            sentence_lower = sentence.lower()
            if 'if' in sentence_lower and 'then' in sentence_lower:
                parts = sentence_lower.split(' then ')
                if_part = parts[0].replace('if', '').strip()
                then_part = parts[1].strip()
                
                # Clean up the then part
                then_part = re.sub(r'^(the )?system (shall|should|will|can)', '', then_part).strip()
                then_part = re.sub(r'(the )?system', '', then_part).strip()
                then_part = re.sub(r'^(asks?|shows?|displays?|checks?)', r'\1', then_part)
                
                if then_part:
                    return f"If {if_part}, then the system shall {then_part}."
                else:
                    return f"If {if_part}, then the system shall respond appropriately."
                    
            elif 'if' in sentence_lower and ',' in sentence:
                parts = sentence.split(',')
                if_part = parts[0].lower().replace('if', '').strip()
                then_part = ','.join(parts[1:]).strip()
                
                # Clean up similar to above
                then_part = re.sub(r'^(the )?system (shall|should|will|can)', '', then_part).strip()
                then_part = re.sub(r'(the )?system', '', then_part).strip()
                
                if then_part:
                    return f"If {if_part}, then the system shall {then_part}."
                else:
                    return f"If {if_part}, then the system shall respond appropriately."
        except:
            pass
        return f"The system shall handle the condition: {sentence}."
    
    def process_when_template(self, sentence: str) -> str:
        """Process when statements"""
        try:
            when_part = sentence[5:].strip()  # Remove 'when '
            return f"When {when_part}, the system shall be able to respond appropriately."
        except:
            return f"The system shall handle the scenario: {sentence}."
    
    def process_system_capability_template(self, sentence: str) -> str:
        """Process system capability statements with better text handling"""
        action_verbs = {
            'displays': 'display', 'display': 'display', 'shows': 'display', 'show': 'display',
            'validates': 'validate', 'validate': 'validate', 'checks': 'validate', 'check': 'validate',
            'processes': 'process', 'process': 'process', 'handles': 'process', 'handle': 'process',
            'stores': 'store', 'store': 'store', 'saves': 'store', 'save': 'store',
            'retrieves': 'retrieve', 'retrieve': 'retrieve', 'fetches': 'retrieve', 'fetch': 'retrieve',
            'asks': 'ask', 'ask': 'ask', 'prompts': 'prompt', 'prompt': 'prompt',
            'opens': 'open', 'open': 'open', 'closes': 'close', 'close': 'close',
            'updates': 'update', 'update': 'update', 'enters': 'accept', 'enter': 'accept'
        }
        
        sentence_lower = sentence.lower().strip()
        
        # Clean up the sentence first
        sentence_clean = re.sub(r'^the (system|member|user|librarian|administrator|guest)', '', sentence_lower).strip()
        
        for verb_variant, base_verb in action_verbs.items():
            if verb_variant in sentence_clean:
                try:
                    # Find the verb and extract the object/complement
                    verb_index = sentence_clean.find(verb_variant)
                    after_verb = sentence_clean[verb_index + len(verb_variant):].strip()
                    
                    # Clean up common artifacts
                    after_verb = re.sub(r'^(s\s|ing\s)', '', after_verb).strip()
                    after_verb = re.sub(r'^\s*the\s+', 'the ', after_verb)
                    
                    # Handle specific cases
                    if after_verb:
                        if base_verb == 'ask' or base_verb == 'prompt':
                            if 'to' not in after_verb:
                                after_verb = f"the user to {after_verb}"
                        elif base_verb == 'display':
                            if not after_verb.startswith('the '):
                                after_verb = f"the {after_verb}"
                        elif base_verb == 'validate':
                            if not after_verb.startswith('the ') and not after_verb.startswith('that '):
                                after_verb = f"the {after_verb}"
                        
                        return f"The system shall be able to {base_verb} {after_verb}."
                    else:
                        return f"The system shall be able to {base_verb} the required information."
                except:
                    return f"The system shall be able to {base_verb} appropriately."
        
        # If no specific verb found, generate a general capability requirement
        return f"The system shall be able to {sentence_clean}."
    
    def process_user_action_template(self, sentence: str, actors: List[str]) -> str:
        """Process user action statements with improved text handling"""
        sentence_lower = sentence.lower().strip()
        
        # Clean up the sentence
        sentence_clean = re.sub(r'^the\s+', '', sentence_lower)
        
        for actor in actors:
            if actor != 'system' and actor in sentence_clean:
                try:
                    # Find the actor and extract the action
                    actor_index = sentence_clean.find(actor)
                    after_actor = sentence_clean[actor_index + len(actor):].strip()
                    
                    # Clean up common connecting words and artifacts
                    after_actor = re.sub(r'^(can|will|should|must|may)\s+', '', after_actor)
                    after_actor = re.sub(r'^(clicks?|click)\s+', 'click ', after_actor)
                    after_actor = re.sub(r'^(enters?|enter)\s+', 'enter ', after_actor)
                    after_actor = re.sub(r'^(selects?|select)\s+', 'select ', after_actor)
                    after_actor = re.sub(r'^(types?|type)\s+', 'type ', after_actor)
                    after_actor = re.sub(r'^(views?|view)\s+', 'view ', after_actor)
                    after_actor = re.sub(r'^(browses?|browse)\s+', 'browse ', after_actor)
                    
                    # Handle specific action patterns
                    if after_actor:
                        # Fix common patterns
                        if after_actor.startswith('on '):
                            after_actor = after_actor[3:].strip()
                        
                        # Ensure proper article usage
                        if not after_actor.startswith(('the ', 'a ', 'an ', 'their ', 'his ', 'her ')):
                            if any(word in after_actor for word in ['button', 'page', 'details', 'information', 'books']):
                                after_actor = f"the {after_actor}"
                        
                        return f"The system shall provide {actor} with the ability to {after_actor}."
                    else:
                        return f"The system shall provide {actor} with the required functionality."
                except:
                    return f"The system shall provide {actor} with the ability to perform the action."
        
        # If no specific actor found, use generic user
        action = re.sub(r'^(the\s+)?(system\s+)?', '', sentence_clean).strip()
        if action:
            return f"The system shall provide users with the ability to {action}."
        else:
            return f"The system shall provide users with the required functionality."
    
    def process_modal_template(self, sentence: str) -> str:
        """Process modal verb statements"""
        modals = ['should', 'must', 'can', 'will', 'shall', 'may', 'could', 'would']
        sentence_lower = sentence.lower()
        
        for modal in modals:
            if modal in sentence_lower:
                try:
                    modal_index = sentence_lower.find(modal)
                    after_modal = sentence[modal_index + len(modal):].strip()
                    return f"The system shall {after_modal}."
                except:
                    pass
        
        return f"The system shall be able to {sentence.lower()}."
    
    def process_feature_template(self, sentence: str) -> str:
        """Process feature/function statements"""
        feature_words = ['feature', 'function', 'capability', 'service', 'interface', 'component']
        sentence_lower = sentence.lower()
        
        for feature_word in feature_words:
            if feature_word in sentence_lower:
                return f"The system shall provide the {feature_word} described as: {sentence}."
        
        return f"The system shall implement: {sentence}."
    
    def process_state_template(self, sentence: str) -> str:
        """Process state/condition statements"""
        state_words = ['available', 'ready', 'logged in', 'valid', 'correct', 'stored', 'retrieved']
        sentence_lower = sentence.lower()
        
        for state_word in state_words:
            if state_word in sentence_lower:
                return f"The system shall ensure that {sentence.lower()}."
        
        return f"The system shall maintain the state: {sentence}."
    
    def process_validation_template(self, sentence: str) -> str:
        """Process data validation statements"""
        validation_words = ['validate', 'check', 'verify', 'confirm', 'authenticate']
        sentence_lower = sentence.lower()
        
        for validation_word in validation_words:
            if validation_word in sentence_lower:
                return f"The system shall {validation_word} {sentence_lower.replace(validation_word, '').strip()}."
        
        return f"The system shall validate: {sentence}."
    
    def process_default_template(self, sentence: str, actors: List[str]) -> str:
        """Default template for unmatched sentences"""
        if any(actor in sentence.lower() for actor in actors if actor != 'system'):
            return f"The system shall support the requirement: {sentence}."
        else:
            return f"The system shall be able to {sentence.lower()}."

    def generate_snl_from_text(self, description: str) -> Dict[str, Any]:
        """
        Generate SNL from natural language description using enhanced RUPP methodology
        """
        try:
            # Step 1: Preprocess the text
            preprocessed_text = self.apply_preprocessing(description)
            
            # Step 2: Extract sentences with enhanced coverage
            sentences = self.extract_sentences_comprehensive(preprocessed_text)
            
            # Step 3: Identify actors
            actors = self.identify_actors_enhanced(description)
            
            # Step 4: Generate requirements using enhanced templates
            all_requirements = []
            
            for sentence in sentences:
                if len(sentence.strip()) > 3:  # Process meaningful sentences
                    sentence_requirements = self.apply_rupp_templates_enhanced(sentence, actors)
                    all_requirements.extend(sentence_requirements)
            
            # Step 5: Clean up and deduplicate requirements
            cleaned_requirements = []
            seen_requirements = set()
            
            for req in all_requirements:
                if req and req not in seen_requirements and len(req) > 20:
                    cleaned_requirements.append(req)
                    seen_requirements.add(req)
            
            # Step 6: Create final SNL text
            final_snl = '\n'.join(cleaned_requirements)
            
            return {
                'snl_text': final_snl,
                'actors': actors,
                'preprocessed_text': preprocessed_text,
                'sentences_count': len(cleaned_requirements),
                'formatted_sentences': self.split_into_sentences(final_snl),
                'requirements': cleaned_requirements,
                'original_sentences_processed': len(sentences),
                'processing_stats': {
                    'total_input_sentences': len(sentences),
                    'requirements_generated': len(all_requirements),
                    'unique_requirements': len(cleaned_requirements),
                    'actors_identified': len(actors)
                }
            }
            
        except Exception as e:
            return {
                'snl_text': f"Error processing requirements: {str(e)}",
                'actors': [],
                'preprocessed_text': description,
                'sentences_count': 0,
                'formatted_sentences': "",
                'requirements': [],
                'error': str(e)
            }
