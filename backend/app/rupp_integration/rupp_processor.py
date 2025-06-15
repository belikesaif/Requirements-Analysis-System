"""
RUPP Template-based SNL Generator
Extracted and adapted from the existing notebook implementation
"""

import spacy
import re
# import contractions  # Removed to avoid dependency issues
import textacy
from typing import List, Dict, Any

class RUPPProcessor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.corrections = {
            'librarian': 'NOUN',  # Correct Librarian to be a noun
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
            formatted_sentences.append(f"{i}. {sentence}")
        
        return '\n'.join(formatted_sentences)
    
    def split_and_add_full_stop(self, sentence: str) -> tuple:
        """Split sentence on 'and' and add full stop"""
        if " and " in sentence:
            before_and, after_and = sentence.split("and", 1)
            before_and = before_and.strip() + '. '
            after_and = after_and.strip()
            return before_and, after_and
        else:
            return sentence + '. '
    
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
        
        # Expand contractions can't to cannot
        # Basic contraction expansion (simplified without contractions library)
        and_replace = and_replace.replace("'t", " not")
        and_replace = and_replace.replace("'re", " are")
        and_replace = and_replace.replace("'ll", " will")
        and_replace = and_replace.replace("'ve", " have")
        and_replace = and_replace.replace("'m", " am")
        and_replace = and_replace.replace("'d", " would")
        expanded_paragraph = and_replace
          # Remove punctuation and special characters (except full stop)
        remove_punctuation = re.sub(r'[^a-zA-Z0-9\s\.,]', '', expanded_paragraph)
        
        # Remove extra whitespace
        remove_extra_whitespace = re.sub(r'\s+', ' ', remove_punctuation).strip()
        
        normalized_text = self.join_abbreviation(remove_extra_whitespace, self.abbreviation_mapping)
        
        split_and_sentences = self.split_and_add_full_stop(normalized_text)
        
        full_stop_space = self.add_space_after_period(split_and_sentences)
        
        return full_stop_space
    
    def identify_actors_with_actions(self, description: str) -> List[str]:
        """Identify actors from text using spaCy and textacy - filtered for meaningful actors"""
        doc = self.nlp(description)
        actors_with_actions = set()
        
        # Define common system-related entities that should be included
        valid_actors = {'system', 'user', 'admin', 'administrator', 'librarian', 'manager', 'guest', 'member', 'customer', 'client', 'operator'}
        
        # Words to exclude (common nouns that are not actors)
        exclude_words = {
            'information', 'book', 'category', 'details', 'data', 'page', 'button', 'form', 'field', 
            'database', 'table', 'record', 'file', 'document', 'report', 'view', 'display', 'screen',
            'id', 'number', 'date', 'time', 'message', 'error', 'warning', 'notification', 'alert',
            'option', 'choice', 'selection', 'item', 'element', 'component', 'feature', 'function',
            'process', 'procedure', 'method', 'step', 'action', 'operation', 'task', 'activity'
        }
        
        # Extract from subject-verb-object triples with strict filtering
        for sent in doc.sents:
            try:
                SBOV_ext = textacy.extract.subject_verb_object_triples(sent)
                SBOV = list(SBOV_ext)
                
                for triple in SBOV:
                    subject, verb, _ = triple
                    for token in subject:
                        actor_text = token.text.lower().strip()
                        
                        # Include only if it's in valid_actors or is a proper noun person/organization
                        if (actor_text in valid_actors or
                            (token.pos_ == "PROPN" and token.ent_type_ in ["PERSON", "ORG"]) or
                            (token.pos_ == "NOUN" and actor_text in valid_actors)) and \
                           actor_text not in exclude_words and \
                           len(actor_text) > 2 and \
                           not actor_text.endswith('.'):  # Exclude things like "id."
                            actors_with_actions.add(actor_text)
            except Exception:
                continue
        
        # Always include core actors if they appear in text
        text_lower = description.lower()
        for actor in ['system', 'user', 'administrator', 'librarian', 'member', 'guest']:
            if actor in text_lower:
                actors_with_actions.add(actor)
        
        # Filter out any remaining problematic entries
        final_actors = []
        for actor in actors_with_actions:
            if (len(actor) > 2 and 
                not actor.isdigit() and 
                actor not in exclude_words and
                not any(char.isdigit() for char in actor) and  # No numbers in actor names
                actor.isalpha()):  # Only alphabetic characters
                final_actors.append(actor)
                
        return sorted(list(set(final_actors)))  # Remove duplicates and sort
    
    def identify_nsubj(self, sent) -> str:
        """Identify nominal subject in sentence"""
        for token in sent:
            if token.dep_ == "nsubj":
                return token.text.lower()
        return ""
    
    def rupp_template_1(self, sent, rupp_template_2: List[str], actor: List[str]) -> str:
        """If-then template processing"""
        if "if" in sent.text.lower() and "then" in sent.text.lower():
            temp = list(rupp_template_2)
            
            then_idx = sent.text.find("then")
            then_next = then_idx + 5
            
            if then_idx == -1:
                then_idx = sent.text.find(",")
                then_next = then_idx + 1
            
            if sent.text.startswith("If"):
                temp[1] = sent.text[3:then_idx]
            else:
                temp[1] = sent.text[:then_idx]
            
            if temp[1].lower().startswith("if "):
                temp[1] = " " + temp[1][3:]
            
            verb_string = ""
            temp[3] = ""
            flg = False
            first_flg = False
            
            for i in range(len(sent)):
                if sent[i].text == "then" and sent[i].dep_ == "advmod":
                    temp[3] += str(sent[i].head.lemma_)
                    verb_string = sent[i].head.text
                    flg = True
                elif flg:
                    if sent[i].pos_.lower() == "aux" and not first_flg:
                        first_flg = True
                    elif sent[i].text == "system":
                        continue
                    else:
                        if sent[i].text != verb_string:
                            if sent[i].tag_ == "ADJ":
                                continue
                            elif sent[i].text not in ["the"]:
                                temp[3] += " " + str(sent[i].text)
            
            if temp[1] == "" or temp[3] == "":
                return ""
            else:
                return "".join(temp)
        else:
            return ""
    
    def rupp_template_2(self, sent, rupp_template_2: List[str]) -> str:
        """WHEN template processing"""
        temp = list(rupp_template_2)
        
        comma_idx = sent.text.find(",")
        temp[1] = sent.text[5:comma_idx]
        
        comma_flg = False
        rem_text = ""
        verb_flg = False
        
        for token in sent:
            if token.tag_ == ",":
                comma_flg = True
            elif comma_flg:
                if token.pos_ == "VERB":
                    temp[3] += token.lemma_
                    temp[3] += " "
                    verb_flg = True
                elif verb_flg:
                    if token.text.lower() == "system":
                        continue
                    else:
                        rem_text += token.text
                        rem_text += " "
        
        temp[3] += rem_text
        
        if temp[1] != "" and temp[3] != "":
            return "".join(temp)
        else:
            return ""
    
    def rupp_template_3(self, sent, rupp_template_3: List[str]) -> str:
        """WHILE template processing"""
        temp = list(rupp_template_3)
        
        comma_idx = sent.text.find(",")
        temp[1] = sent.text[6:comma_idx]
        
        comma_flg = False
        rem_str = ""
        verb_flg = False
        
        for token in sent:
            if token.tag_ == ",":
                comma_flg = True
            elif comma_flg:
                if token.pos_ == "VERB":
                    temp[3] += token.lemma_
                    temp[3] += " "
                    verb_flg = True
                elif verb_flg:
                    if token.text.lower() == "system":
                        continue
                    else:
                        rem_str += token.text
                        rem_str += " "
        
        temp[3] += rem_str
        
        if temp[1] != "" and temp[3] != "":
            return "".join(temp)
        else:
            return ""
    
    def rupp_template_4(self, sent, rupp_template_4: List[str]) -> str:
        """WHERE template processing"""
        temp = list(rupp_template_4)
        
        comma_idx = sent.text.find(",")
        temp[1] = sent.text[6:comma_idx]
        
        comma_flg = False
        rem_str = ""
        verb_flg = False
        
        for token in sent:
            if token.tag_ == ",":
                comma_flg = True
            elif comma_flg:
                if token.pos_ == "VERB":
                    temp[3] += token.lemma_
                    temp[3] += " "
                    verb_flg = True
                elif verb_flg:
                    if token.text.lower() == "system":
                        continue
                    else:
                        rem_str += token.text
                        rem_str += " "
        
        temp[3] += rem_str
        
        if temp[1] != "" and temp[3] != "":
            return "".join(temp)
        else:
            return ""
    
    def rupp_template_5(self, sent, rupp_template_5: List[str], actor: List[str]) -> str:
        """System Action template"""
        if sent[0].text.lower() == "if":
            return ""
        
        temp = list(rupp_template_5)
        subj_flg = False
        verb_flg = False
        
        for token in sent:
            if token.dep_ == "nsubj" and token.text.lower() in actor:
                subj_flg = True
            elif subj_flg:
                if token.pos_ == "AUX":
                    continue
                if verb_flg == False and token.pos_.lower() == "verb":
                    verb_flg = True
                    temp[1] += token.lemma_ + " "
                else:
                    temp[1] += token.text
                    temp[1] += " "
        
        if temp[1] != "":
            return "".join(temp)
        else:
            return ""
    
    def rupp_template_6(self, sent, rupp_template_6: List[str], actor: List[str]) -> str:
        """Actor Action template"""
        if "nsubj" == "system":
            return ""
        
        temp = list(rupp_template_6)
        subj_flg = False
        verb_flg = False
        
        for token in sent:
            if token.dep_ == "nsubj" and token.text.lower() in actor and token.text.lower() != "system":
                subj_flg = True
                temp[1] = token.text
            elif subj_flg:
                if token.pos_ == "AUX":
                    continue
                if not verb_flg and token.pos_.lower() == "verb":
                    verb_flg = True
                    temp[3] += token.lemma_ + " "
                else:
                    if token.tag_ == "PRP" and token.text in ["he", "she"]:
                        chosen_actor = actor[0] if actor[0] != "system" else actor[1]
                        temp[3] += str(chosen_actor) + " "
                    else:
                        if token.pos_ not in ["AUX"]:
                            temp[3] += token.text + " "
        
        if temp[1] and temp[3]:
            return "".join(temp)
        else:
            return ""
    
    def rupp_template_7(self, sent, rupp_template_7: List[str], actor: List[str]) -> str:
        """Actor action future tense template"""
        if "nsubj" == "system":
            return ""
        
        temp = list(rupp_template_7)
        subj_flg = False
        verb_found = False
        verb_text = ""
        
        for token in sent:
            if (token.pos_ == "NOUN" or token.pos_ == "PROPN") and (token.tag_ in ["NN", "NNS"]) and token.text.lower() in actor and token.text.lower() != "system" and not subj_flg:
                subj_flg = True
                temp[1] = "The system shall provide " + token.text.lower() + " with the ability to " + ""
            if subj_flg:
                if token.pos_ == "VERB":
                    verb_found = True
                    verb_text += token.text + " "
                elif verb_found and token.text.lower() in ["in"]:
                    verb_text += token.text.lower() + ". "
        
        temp[3] = verb_text
        
        if temp[1] != "" and temp[3] != "":
            return temp[1] + temp[3]
        else:
            return ""
    
    def rupp_template_8(self, sent, rupp_template_8: List[str], actor: List[str]) -> str:
        """Additional template processing"""
        temp = list(rupp_template_8)
        
        subj_found = False
        verb_text = ""
        adj_text = ""
        noun_text = ""
        end_text = ""
        
        for token in sent:
            if token.pos_ in ["NOUN", "PROPN"] and token.tag_ in ["NN","NNS"] and token.text.lower() not in actor and not subj_found:
                subj_found = True
                noun_text = token.text.lower() + " "
            elif token.pos_ == "VERB" and not verb_text:
                verb_text = token.text.lower() + " "
            elif token.pos_ == "ADJ":
                adj_text += token.text + " "
            else:
                if subj_found and token.pos_ not in ["AUX"] and token.pos_ not in ["PART"] and token.text.lower() not in ["system"] and token.pos_ not in ["ADP", "in"] and token.pos_ not in ["DET"] and token.text.lower() not in ["to"]:
                    end_text += token.text_with_ws+" "
        
        temp[1] = verb_text + adj_text + noun_text + end_text+" "
        
        if temp[0] and temp[1]:
            return temp[0] + temp[1]
        else:
            return ""
    
    def generate_snl(self, requirements_text: str) -> Dict[str, Any]:
        """Generate SNL using RUPP's template methodology"""
        # Apply preprocessing
        preprocessed_text = self.apply_preprocessing(requirements_text)
        
        # Identify actors
        actors = self.identify_actors_with_actions(requirements_text)
        
        # Process with spaCy
        doc = self.nlp(preprocessed_text)
        
        # Apply corrections
        for token in doc:
            if token.text.lower() in self.corrections:
                token.pos_ = self.corrections[token.text.lower()]
        
        # Identify conditional sentences
        condition = []
        for sent in doc.sents:
            md_flag = False
            admod = False
            mark = False
            cond = False
            
            for token in sent:
                if token.dep_ == "advmod":
                    admod = True
                if token.dep_ == "mark":
                    mark = True
                if cond == False:
                    if admod == True and mark == True:
                        condition.append(sent)
                        cond = True
        
        # RUPP Templates
        rupp_template_1 = ["If", "", "then the system shall be able to ", ""]
        rupp_template_2 = ["When ", "", " the system shall be able to ", ""]
        rupp_template_3 = ["While ", "", " the system shall be able to ", ""]
        rupp_template_4 = ["Where ", "", " the system shall be able to ", ""]
        rupp_template_5 = ["The System shall be able to ", ""]
        rupp_template_6 = ["The System shall provide ", "", " with the ability to ", ""]
        
        results = []
        
        for sent in doc.sents:
            # Conditional processing
            if sent in condition:
                res = self.rupp_template_1(sent, rupp_template_1, actors)
                if res != "":
                    results.append(res)
            
            # When/While/Where processing
            if doc[0].text.lower() == "when":
                res = self.rupp_template_2(sent, rupp_template_2)
                if res != "":
                    results.append(res)
            if doc[0].text.lower() == "while":
                res = self.rupp_template_3(sent, rupp_template_3)
                if res != "":
                    results.append(res)
            if doc[0].text.lower() == "where":
                res = self.rupp_template_4(sent, rupp_template_4)
                if res != "":
                    results.append(res)
            
            # Skip certain starting patterns
            if sent.text.strip().lower().startswith(("when ", "while", "where ", "if ")):
                continue
            
            # System action processing
            if self.identify_nsubj(sent) == "system":
                res = self.rupp_template_5(sent, rupp_template_5, actors)
                if res != "":
                    results.append(res)
            
            # Actor action processing
            elif self.identify_nsubj(sent) != "system" and sent not in condition:
                res = self.rupp_template_6(sent, rupp_template_6, actors)
                if res != "":
                    results.append(res)
                else:
                    res = self.rupp_template_7(sent, rupp_template_6, actors)
                    if res != "":
                        results.append(res)
                    else:
                        res = self.rupp_template_8(sent, rupp_template_5, actors)
                        if res != "":
                            results.append(res)
            else:
                results.append(sent.text)
          # Format and clean results
        cleaned_results = []
        for result in results:
            if result and len(result.strip()) > 10:  # Filter out very short/empty results
                # Remove space before full stop and ensure space after
                result = result.replace(' .', '.').replace('.', '. ')
                # Capitalize first letter after each period
                result = '. '.join(map(lambda s: s.strip().capitalize(), result.split('. ')))
                # Additional cleanup
                result = self._clean_requirement(result)
                if result:  # Only add if not empty after cleaning
                    cleaned_results.append(result)
        
        final_snl = ''.join(cleaned_results)
        
        return {
            'snl_text': final_snl,
            'actors': actors,
            'preprocessed_text': preprocessed_text,
            'sentences_count': len(cleaned_results),
            'formatted_sentences': self.split_into_sentences(final_snl),
            'requirements': cleaned_results  # Add individual requirements
        }
    
    def _clean_requirement(self, requirement: str) -> str:
        """Clean up a single requirement text"""
        if not requirement or len(requirement.strip()) < 10:
            return ""
        
        # Remove extra spaces
        requirement = ' '.join(requirement.split())
        
        # Fix common issues
        requirement = requirement.replace('The system shall be able to The system', 'The system')
        requirement = requirement.replace('The system shall provide The system', 'The system')
        requirement = requirement.replace('  ', ' ')
        
        # Ensure proper sentence ending
        if not requirement.endswith('.'):
            requirement += '.'
        
        # Ensure it starts with capital letter
        if requirement and requirement[0].islower():
            requirement = requirement[0].upper() + requirement[1:]
        
        # Filter out requirements that are too incomplete
        required_phrases = ['shall be able to', 'shall provide', 'shall']
        if not any(phrase in requirement.lower() for phrase in required_phrases):
            return ""
        
        return requirement
