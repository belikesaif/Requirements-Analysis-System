"""
RUPP Template-based SNL Generator - Notebook Faithful Implementation
Replicates the exact logic from PreCodedNotebook.ipynb
"""

import spacy
import re
from typing import List, Dict, Any

# Required import for textacy - critical for notebook fidelity
try:
    import textacy
    HAS_TEXTACY = True
except ImportError:
    HAS_TEXTACY = False
    print("Warning: textacy not available - this will affect actor identification accuracy")

class NotebookFaithfulRUPPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
            print("SpaCy model 'en_core_web_sm' loaded successfully")
        except OSError as e:
            print(f"SpaCy model not available: {e}")
            self.nlp = None
        
        # Notebook corrections mapping
        self.corrections = {
            'librarian': 'NOUN',
        }
        
        # Notebook abbreviation mapping
        self.abbreviation_mapping = {
            'guest user': 'guest_user',
            'into': 'in to'
        }
        
        # Initialize RUPP templates exactly as in notebook
        self.initialize_rupp_templates()
        
    def initialize_rupp_templates(self):
        """Initialize RUPP templates exactly as defined in the notebook"""
        self.rupp_template_1 = ["If", "", "then the system shall be able to ", ""]
        self.rupp_template_2 = ["When ", "", " the system shall be able to ", ""]
        self.rupp_template_3 = ["While ", "", " the system shall be able to ", ""]
        self.rupp_template_4 = ["Where ", "", " the system shall be able to ", ""]
        self.rupp_template_5 = ["The System shall be able to ", ""]
        self.rupp_template_6 = ["The System shall provide ", "", " with the ability to ", ""]
        
    def split_into_sentences(self, paragraph: str) -> str:
        """Split the paragraph into sentences using regular expressions - Notebook Implementation"""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', paragraph)
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences, start=1):
            formatted_sentences.append(f"{i}. {sentence}")
        
        return '\n'.join(formatted_sentences)
    
    def split_and_add_full_stop(self, sentence: str):
        """Split sentences containing 'and' and add full stops - Notebook Implementation"""
        if " and " in sentence:
            before_and, after_and = sentence.split("and", 1)
            before_and = before_and.strip() + '. '
            after_and = after_and.strip()
            return before_and, after_and
        else:
            return sentence + '. '
    
    def replace_and(self, input_string: str) -> str:
        """Replace & with 'and' - Notebook Implementation"""
        words = input_string.split()
        replaced_words = [word.replace("&", "and") for word in words]
        combined_string = ' '.join(replaced_words)
        return combined_string
    
    def add_space_after_period(self, sentence: str) -> str:
        """Add space after periods - Notebook Implementation"""
        result = ''
        for char in sentence:
            result += char
            if char == '.':
                result += ' '
        return result
    
    def join_abbreviation(self, text: str, abbreviation_mapping: Dict[str, str]) -> str:
        """Join abbreviations based on mapping - Notebook Implementation"""
        for word, replacement in abbreviation_mapping.items():
            if word in text:
                text = text.replace(word, replacement)
        return text
    
    def apply_preprocessing(self, text: str) -> str:
        """Apply complete preprocessing pipeline - Notebook Implementation"""
        # Text lowercasing
        lowercased_paragraph = text.lower()
        
        # Replace & with 'and'
        and_replace = self.replace_and(lowercased_paragraph)
        
        # Expand contractions - simplified version without contractions library
        expanded_paragraph = self.expand_contractions_simple(and_replace)
        
        # Remove punctuation and special characters (except full stop)
        remove_punctuation = re.sub(r'[^a-zA-Z0-9\s\.,]', '', expanded_paragraph)
        
        # Remove extra whitespace
        remove_extra_whitespace = re.sub(r'\s+', ' ', remove_punctuation).strip()
        
        # Apply abbreviation mapping
        normalized_text = self.join_abbreviation(remove_extra_whitespace, self.abbreviation_mapping)
        
        # Split and add full stops
        split_and_sentences = self.split_and_add_full_stop(normalized_text)
        
        # Add space after periods
        full_stop_space = self.add_space_after_period(split_and_sentences)
        
        return full_stop_space
    
    def expand_contractions_simple(self, text: str) -> str:
        """Simple contraction expansion - Notebook equivalent"""
        contractions_map = {
            "can't": "cannot", "won't": "will not", "don't": "do not",
            "isn't": "is not", "aren't": "are not", "wasn't": "was not",
            "weren't": "were not", "haven't": "have not", "hasn't": "has not",
            "wouldn't": "would not", "shouldn't": "should not", "couldn't": "could not"
        }
        
        for contraction, expansion in contractions_map.items():
            text = text.replace(contraction, expansion)
        
        return text

    def identify_actors_with_actions(self, description: str) -> List[str]:
        """Identify actors with actions - Notebook Implementation using textacy"""
        if not self.nlp:
            return ['system', 'user']  # Fallback
            
        doc = self.nlp(description)
        actors_with_actions = set()

        for sent in doc.sents:
            if HAS_TEXTACY:
                try:
                    SBOV_ext = textacy.extract.subject_verb_object_triples(sent)
                    SBOV = list(SBOV_ext)

                    for triple in SBOV:
                        subject, verb, _ = triple
                        for token in subject:
                            if token.pos_ == "NOUN":
                                actors_with_actions.add(token.text.lower())
                except:
                    # Fallback to basic noun extraction
                    for token in sent:
                        if token.pos_ == "NOUN" and token.text.lower() in ['system', 'user', 'member', 'librarian', 'administrator', 'guest']:
                            actors_with_actions.add(token.text.lower())
            else:
                # Basic fallback without textacy
                for token in sent:
                    if token.pos_ == "NOUN" and token.text.lower() in ['system', 'user', 'member', 'librarian', 'administrator', 'guest']:
                        actors_with_actions.add(token.text.lower())

        return list(actors_with_actions)
    
    def identify_nsubj(self, sent) -> str:
        """Identify nominal subject - Notebook Implementation"""
        for token in sent:
            if token.dep_ == "nsubj":
                return token.text.lower()
        return ""

    def ruppTemplate_1(self, sent, rupp_template_2, actor):
        """RUPP Template 1: If-then conditional statements - Notebook Implementation"""
        if "if" in sent.text.lower() and "then" in sent.text.lower():
            temp = list.copy(rupp_template_2)

            then_idx = sent.text.find("then")
            then_next = then_idx + 5

            if then_idx == -1:  # if then not found
                then_idx = sent.text.find(",")
                then_next = then_idx + 1

            if sent.text.startswith("If"):
                temp[1] = sent.text[3:then_idx]
            else:
                temp[1] = sent.text[:then_idx]

            # Remove "if" from the beginning of the sentence
            if temp[1].lower().startswith("if "):
                temp[1] = " " + temp[1][3:]

            verb_string = str("")
            temp[3] = ""
            idx_rest_of_sent = 0
            idx_aux = 0
            flg = False
            first_flg = False

            # without then statements remaining
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

    def ruppTemplate_2(self, sent, rupp_template_2):
        """RUPP Template 2: WHEN statements - Notebook Implementation"""
        temp = list.copy(rupp_template_2)

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

    def ruppTemplate_3(self, sent, rupp_template_3):
        """RUPP Template 3: WHILE statements - Notebook Implementation"""
        temp = list.copy(rupp_template_3)

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

    def ruppTemplate_4(self, sent, rupp_template_4):
        """RUPP Template 4: WHERE statements - Notebook Implementation"""
        temp = list.copy(rupp_template_4)

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

    def ruppTemplate_5(self, sent, rupp_template_5, actor):
        """RUPP Template 5: System Action - Notebook Implementation"""
        # Check if the sentence starts with "if" and block it
        if sent[0].text.lower() == "if":
            return ""
        temp = list.copy(rupp_template_5)  # change index 1-PROCESS
        subj_flg = False
        verb_flg = False
        for token in sent:
            if token.dep_ == "nsubj" and token.text.lower() in actor:
                subj_flg = True
            elif subj_flg == True:
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

    def ruppTemplate_6(self, sent, rupp_template_6, actor):
        """RUPP Template 6: Actor Action - Notebook Implementation"""
        if "nsubj" == "system":
            return ""

        temp = list(rupp_template_6)  # change index 1-customer 3-PROCESS
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

    def ruppTemplate_7(self, sent, rupp_template_7, actor):
        """RUPP Template 7: Actor action future tense - Notebook Implementation"""
        if "nsubj" == "system":
            return ""
        temp = list.copy(rupp_template_7)
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

    def ruppTemplate_8(self, sent, rupp_template_8, actor):
        """RUPP Template 8: Additional patterns - Notebook Implementation"""
        temp = list.copy(rupp_template_8)

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
                adj_text += token.text + " "  # Capture adjectives
            else:
                if subj_found and token.pos_ not in ["AUX"] and token.pos_ not in ["PART"] and token.text.lower() not in ["system"] and token.pos_ not in ["ADP"] and token.pos_ not in ["DET"] and token.text.lower() not in ["to"]:
                    end_text += token.text_with_ws+" "  # Collect the rest of the text with spaces

        temp[1] = verb_text + adj_text + noun_text + end_text+" "

        if temp[0] and temp[1]:
            return temp[0] + temp[1]
        else:
            return ""
    def generate_snl_from_text(self, description: str) -> Dict[str, Any]:
        """
        Generate SNL from natural language description - Notebook Faithful Implementation
        """
        try:
            if not self.nlp:
                return {
                    'snl_text': "Error: SpaCy model not available",
                    'actors': [],
                    'preprocessed_text': description,
                    'sentences_count': 0,
                    'formatted_sentences': "",
                    'requirements': [],
                    'error': "SpaCy model not available"
                }

            # Step 1: Apply preprocessing (notebook style)
            preprocessed_text = self.apply_preprocessing(description)
            
            # Step 2: Identify actors using notebook method
            actor = self.identify_actors_with_actions(description)
            
            # Step 3: Process with spaCy and apply POS corrections
            doc = self.nlp(preprocessed_text)
            for token in doc:
                if token.text.lower() in self.corrections:
                    token.pos_ = self.corrections[token.text.lower()]
            
            # Step 4: Identify conditional sentences (notebook logic)
            condition = []
            for sent in doc.sents:
                md_flag = False
                admod = False
                mark = False
                cond = False
                sys_flg = False

                for token in sent:
                    # conditional detection
                    if token.dep_ == "advmod":
                        admod = True
                    if token.dep_ == "mark":
                        mark = True
                    if cond == False:
                        if admod == True and mark == True:
                            condition.append(sent)
                            cond = True

            # Step 5: Apply RUPP templates in notebook order
            results = []

            for sent in doc.sents:
                # Template 1: Conditional statements
                if sent in condition:
                    res = self.ruppTemplate_1(sent, self.rupp_template_1, actor)
                    if res != "":
                        results.append(res)

                # Template 2-4: Temporal conditions
                if doc[0].text.lower() == "when":
                    res = self.ruppTemplate_2(sent, self.rupp_template_2)
                    if res != "":
                        results.append(res)
                if doc[0].text.lower() == "while":
                    res = self.ruppTemplate_3(sent, self.rupp_template_3)
                    if res != "":
                        results.append(res)
                if doc[0].text.lower() == "where":
                    res = self.ruppTemplate_4(sent, self.rupp_template_4)
                    if res != "":
                        results.append(res)

                # Skip certain sentence patterns
                if sent.text.strip().lower().startswith("when "):
                    continue
                if sent.text.strip().lower().startswith("while"):
                    continue
                if sent.text.strip().lower().startswith("where "):
                    continue

                # Template 5: System actions
                if self.identify_nsubj(sent) == "system":
                    res = self.ruppTemplate_5(sent, self.rupp_template_5, actor)
                    if res != "":
                        results.append(res)

                # Template 6-8: Actor actions
                elif self.identify_nsubj(sent) != "system" and sent not in condition:
                    res = self.ruppTemplate_6(sent, self.rupp_template_6, actor)
                    if res != "":
                        results.append(res)
                    else:
                        res = self.ruppTemplate_7(sent, self.rupp_template_6, actor)
                        if res != "":
                            results.append(res)
                        else:
                            res = self.ruppTemplate_8(sent, self.rupp_template_5, actor)
                            if res != "":
                                results.append(res)
                elif sent.text.strip().lower().startswith("if "):
                    continue
                else:
                    results.append(sent.text)

            # Step 6: Format results (notebook style)
            formatted_results = []
            for result in results:
                # Remove space before the full stop and ensure there's a space after the full stop
                result = result.replace(' .', '.').replace('.', '. ')
                # Capitalize the first letter after each period
                result = '. '.join(map(lambda s: s.strip().capitalize(), result.split('. ')))
                formatted_results.append(result)
            
            final_snl = ''.join(formatted_results)
            separate_sentences = self.split_into_sentences(final_snl)

            return {
                'snl_text': final_snl,
                'actors': actor,
                'preprocessed_text': preprocessed_text,
                'sentences_count': len(formatted_results),
                'formatted_sentences': separate_sentences,
                'requirements': formatted_results,
                'original_sentences_processed': len(list(doc.sents)),
                'processing_stats': {
                    'total_input_sentences': len(list(doc.sents)),
                    'requirements_generated': len(results),
                    'unique_requirements': len(formatted_results),
                    'actors_identified': len(actor)
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

    # Legacy method name for backward compatibility
    def generate_snl(self, description: str) -> Dict[str, Any]:
        """Legacy method name - calls the notebook faithful implementation"""
        return self.generate_snl_from_text(description)

    def calculate_accuracy_metrics(self, results: List[str]) -> Dict[str, float]:
        """Calculate accuracy metrics against notebook expected results"""
        expected_results = [
            'The system shall provide member with the ability to click the login button on the home page.',
            'The System shall be able to display the login page. ',
            'The system shall provide member with the ability to enter his login i d with password.',
            'The system shall provide member with the ability to click on the confirm button.',
            'The system shall be able to check that all of the required information entered.',
            'If the entered information is wrong then the system shall be able to ask member to reenter details.',
            'The system shall be able to validate the entered information against the tables stored in the database.',
            'The system shall provide member with the ability to logged in.',
            'The system shall provide member with the ability to click on view user details.',
            'The system shall be able to open a page showing the details of the member.',
            'The details include the total number of issued books, date of issue, return date, fine to paid.',
            'The system shall provide member with the ability to close the page.',
            'The system shall be able to show ok message.',
            'The system shall be able to stored books in  database.',
            'The system shall be able to retrieve ready books.',
            'The system shall be able to ask user login.',
            'The system shall be able to identify the type of user member , guest or administrator.',
            'The system shall be able to show the categories to browse.',
            'The system shall provide user with the ability to select a category of books to view.',
            'If no category is selected by the user then the system shall be able to ask again user to select category.',
            'The system shall be able to check the books in the database.',
            'The system shall be able to retrieve all the books falling in that category.',
            'The system shall provide user with the ability to select the desired books.',
            'The system shall be able to show the details of the selected books.',
            'The system shall be able to ask user to print the details.',
            'If user does not want to print the details then the system shall be able to print user ignore the step.',
            'The system shall provide user with the ability to reserve a book by inputting the relevant details.',
            'The system shall provide librarian with the ability to also reserve a book for a member.',
            'The system shall provide user with the ability to logged in.',
            'The system shall provide user with the ability to have correct book i d.',
            'The system shall be able to reserve  available books.',
            'The system shall be able to ask user login.',
            'The system shall be able to identify the type of user member , guest or administrator.',
            'The system shall be able to show the categories to browse.',
            'The system shall provide user with the ability to select book to reserve.',
            'If no book is selected by the user then the system shall be able to ask again user to select book to reserve.',
            'The system shall provide user with the ability to enter book i d to reserve.',
            'If the book id is wrong then the system shall be able to ask user to recheck book i d.',
            'The system shall be able to check books in database.',
            'If the selected book is already reserved on another id then the system shall be able to ask user to select book.',
            'The system shall provide member with the ability to logged in.',
            'The system shall provide guest_user with the ability to also search books.',
            'The system shall be able to search  available  book.',
            'The system shall be able to show the categories to browse.',
            'The system shall provide member with the ability to select a category of searching a book.',
            'If no category is selected by the member then the system shall be able to ask again user to select category.',
            'The system shall be able to check the books in the database.',
            'The system shall be able to retrieve all the books falling in that category.',
            'The system shall provide member with the ability to give the member i d to the librarian.',
            'The system shall be able to issue available books.',
            'The system shall provide librarian with the ability to check the availability of the books.',
            'The system shall provide librarian with the ability to check total number of books issued on that Id.',
            'The system shall provide user with the ability to not issue the books if the has three books issued on his i d.',
            'The system shall provide librarian with the ability to issue the book.',
            'The system updates the information in database.',
            'The system shall provide librarian with ability to logged in.',
            'The system shall provide member with the ability to borrow books.',
            'The system shall provide member with the ability to give the member i d to the librarian.',
            'The system shall provide member with the ability to return the book.',
            'The system shall provide librarian with the ability to enter book i d , member i d in the system.',
            'If the entered book id is incorrect then the system shall be able to be asks to reenter book i d.',
            'The system shall be able to prompt message that book with book i d successfully returned.',
            'The system shall be able to stored members in database.',
            'The system shall be able to retrieve available members.',
            'The system shall provide member with the ability to logged in.',
            'The system shall provide guest with the ability to also view members.',
            'The system shall provide user with the ability to click on view members.',
            'The system shall be able to open a page showing the details of the member.',
            'The details include name of member, the total number of issued books, date of issue, return date, fine to paid.',
            'The system shall provide member with the ability to close the page.',
            'The system shall provide librarian with the ability to logged in.',
            'The system shall be able to remove available books.',
            'The system shall be able to add or remove available book details in the database.',
            'The system shall provide librarian with the ability to have option of adding or removing a book in database.',
            'The system shall be able to ask librarian to add or remove the book.',
            'The system shall be able to ask librarian to enter all the required details about the new book to added.',
            'The system shall provide librarian with the ability to add a book.',
            'The system shall provide librarian with the ability to enter the details.',
            'If the librarian selects to remove a book then the system shall be able to remove book be outdated.',
            'The system shall provide system_administrator with the ability to correct all the information has been provided. ',
            'The system shall provide administrator with the ability to logged in.',
            'The system shall provide member with the ability to available to remove.',
            'The system shall provide details with the ability to available to add or remove member in the database.',
            'The system shall be able to ask administrator to add or remove a member.',
            'The system shall provide administrator with the ability to select to add a member.',
            'The system shall be able to ask administrator to enter all the required details about the new member to added.',
            'The system shall provide administrator with the ability to enter the details.',
            'If the administrator selects to remove a member then the system shall be able to remove valid reason of removal required.',
            'The system shall be able to validate that all the information correctly provided.'
        ]
        
        # Simple similarity calculation - in production, would use more sophisticated methods
        try:
            from sklearn.metrics import precision_score, recall_score, f1_score
            import difflib
            
            def calculate_similarity(expected, actual):
                matcher = difflib.SequenceMatcher(None, expected, actual)
                return matcher.ratio()
            
            similarities = [
                max(calculate_similarity(expected, actual) for actual in results)
                for expected in expected_results
            ]
            threshold = 0.8
            binary_results = [1 if similarity > threshold else 0 for similarity in similarities]
            true_positives = sum(binary_results)
            
            precision = precision_score([1] * len(expected_results), binary_results) if true_positives > 0 else 0
            recall = recall_score([1] * len(expected_results), binary_results)
            overspecification = max(0, len(results) - true_positives)
            f1 = f1_score([1] * len(expected_results), binary_results)
            
            return {
                'precision': precision,
                'recall': recall,
                'overspecification': overspecification,
                'f1_score': f1
            }
        except ImportError:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'overspecification': 0,
                'f1_score': 0.0,
                'error': 'sklearn not available for accuracy calculation'
            }


# Factory function for backward compatibility
def create_rupp_processor():
    """Factory function to create RUPP processor instance"""
    return NotebookFaithfulRUPPProcessor()

# Legacy class alias for backward compatibility
FixedRUPPProcessor = NotebookFaithfulRUPPProcessor
