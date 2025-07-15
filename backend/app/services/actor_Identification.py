import openai
import os
import json
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import re

load_dotenv()

# Configure logging for the module
logger = logging.getLogger(__name__)

class ActorIdentificationService:
    def _extract_actors_from_class_diagram(self, class_diagram: str) -> List[str]:
        """
        Manually extract actor-like entities from the PlantUML class diagram.
        Only extracts classes that are likely to be actors (roles, users, people).
        """
        try:
            # Pattern for extracting class or participant definitions
            class_pattern = re.compile(r'(?:class|participant|actor)\s+("?)([A-Za-z0-9_ ]+)\1')

            matches = class_pattern.findall(class_diagram)
            raw_actors = [match[1].strip() for match in matches]

            # Enhanced filtering - only keep actor-like classes
            # Non-actor patterns (technical classes, pages, services, records)
            non_actor_patterns = [
                # Technical/System classes
                'system', 'database', 'service', 'manager', 'handler', 'controller',
                'repository', 'dao', 'api', 'interface', 'factory', 'builder',
                
                # UI/Page classes
                'page', 'view', 'form', 'dialog', 'window', 'screen', 'panel',
                'home', 'login', 'details', 'catalog', 'list', 'search',
                
                # Data/Record classes
                'record', 'data', 'info', 'details', 'log', 'history', 'report',
                'category', 'type', 'status', 'config', 'setting', 'preference',
                
                # Generic terms
                'item', 'object', 'entity', 'model', 'bean', 'dto', 'vo'
            ]
            
            # Actor-like patterns (roles, people, external systems)
            actor_patterns = [
                'user', 'admin', 'administrator', 'librarian', 'member', 'customer',
                'client', 'staff', 'employee', 'student', 'teacher', 'manager',
                'guest', 'visitor', 'operator', 'supervisor', 'owner', 'patron',
                'borrower', 'reader', 'author', 'publisher'
            ]

            actors = []
            for actor in raw_actors:
                if not actor or len(actor) <= 2:
                    continue
                    
                actor_lower = actor.lower()
                
                # Skip if it matches non-actor patterns
                is_non_actor = any(pattern in actor_lower for pattern in non_actor_patterns)
                if is_non_actor:
                    continue
                
                # Include if it matches actor patterns OR if it's a simple, short name that could be an actor
                is_actor_like = (
                    any(pattern in actor_lower for pattern in actor_patterns) or
                    (len(actor) <= 10 and actor.isalpha() and actor[0].isupper())
                )
                
                if is_actor_like:
                    actors.append(actor)

            print(f"Manual class diagram extraction: {raw_actors} -> filtered to: {actors}")
            return list(set(actors))
            
        except Exception as e:
            print(f"Error in manual class diagram actor extraction: {str(e)}")
            return []

    def _extract_all_classes_from_diagram(self, class_diagram: str) -> List[str]:
        """
        Extract ALL classes from the PlantUML class diagram for overspecification detection.
        """
        try:
            # Pattern for extracting class or participant definitions
            class_pattern = re.compile(r'(?:class|participant|actor)\s+("?)([A-Za-z0-9_ ]+)\1')

            matches = class_pattern.findall(class_diagram)
            raw_classes = [match[1].strip() for match in matches]

            return list(set(raw_classes))
            
        except Exception as e:
            print(f"Error extracting all classes from diagram: {str(e)}")
            return []
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1")
        
        # Initialize spaCy for NLP processing
        try:
            import spacy
            self.nlp = spacy.load('en_core_web_sm')
        except (ImportError, OSError):
            self.nlp = None

    def _resolve_actor_conflicts(self, actors: List[str], requirements_text: str) -> List[str]:
            """
            Resolve semantic conflicts between similar actors using NLP analysis
            e.g., User vs Member, Customer vs Client, etc.
            """
            if not self.nlp:
                return actors
                
            try:
                doc = self.nlp(requirements_text.lower())
                
                # Define conflict groups - actors that might represent the same role
                conflict_groups = [
                    ['member', 'customer', 'client'],
                    ['admin', 'administrator', 'manager'],
                    ['librarian', 'staff', 'employee'],
                    ['student', 'pupil', 'learner'],
                    ['guest', 'visitor', 'anonymous']
                ]
                
                resolved_actors = []
                used_groups = set()
                
                actors_lower = [actor.lower() for actor in actors]
                
                for actor in actors:
                    actor_lower = actor.lower()
                    
                    # Check if this actor belongs to any conflict group
                    conflict_group_index = None
                    for i, group in enumerate(conflict_groups):
                        if actor_lower in group:
                            conflict_group_index = i
                            break
                    
                    if conflict_group_index is not None:
                        # If we haven't processed this conflict group yet
                        if conflict_group_index not in used_groups:
                            used_groups.add(conflict_group_index)
                            
                            # Find which actors from this group are present
                            present_actors = [a for a in actors if a.lower() in conflict_groups[conflict_group_index]]
                            
                            if len(present_actors) > 1:
                                # Choose the most appropriate actor based on context frequency
                                chosen_actor = self._choose_primary_actor(present_actors, requirements_text)
                                resolved_actors.append(chosen_actor)
                            else:
                                resolved_actors.append(actor)
                    else:
                        # No conflict, add as-is
                        resolved_actors.append(actor)
                
                return resolved_actors
                
            except Exception as e:
                print(f"Error resolving actor conflicts: {str(e)}")
                return actors
        
    def _choose_primary_actor(self, conflicting_actors: List[str], requirements_text: str) -> str:
            """
            Choose the primary actor from a group of semantically similar actors
            based on frequency and context in requirements
            """
            try:
                doc = self.nlp(requirements_text.lower())
                actor_counts = {}
                
                # Count occurrences of each actor
                for actor in conflicting_actors:
                    count = 0
                    actor_lower = actor.lower()
                    
                    for token in doc:
                        if token.text == actor_lower:
                            count += 1
                    
                    actor_counts[actor] = count
                
                # Return the most frequently mentioned actor
                if actor_counts:
                    primary_actor = max(actor_counts, key=actor_counts.get)
                    print(f"Resolved conflict between {conflicting_actors} -> chose '{primary_actor}' (mentioned {actor_counts[primary_actor]} times)")
                    return primary_actor
                else:
                    return conflicting_actors[0]
                    
            except Exception:
                return conflicting_actors[0]
            
    async def verify_diagrams_with_actors(self, class_diagram: str, sequence_diagram: str, identified_actors: List[str]) -> Dict[str, Any]:
        """
        Verify diagrams against identified actors with enhanced missing actor detection
        """
        try:
            actors_text = ", ".join(identified_actors)
            
            # Extract all actors from class diagram to detect overspecified ones
            all_diagram_classes = self._extract_all_classes_from_diagram(class_diagram)
            overspecified_actors = [
                actor for actor in all_diagram_classes
                if actor not in identified_actors
            ]
            
            # Detect incorrect actors from overspecified ones
            incorrect_actors = []
            incorrect_patterns = ['system', 'database', 'service', 'page', 'record', 'catalog', 'home', 'login', 'details', 'validation', 'category']
            for actor in overspecified_actors:
                if any(pattern in actor.lower() for pattern in incorrect_patterns):
                    incorrect_actors.append(actor)
            
            prompt = f"""Strictly verify the following diagrams against the identified actors. Be thorough in checking for missing actors.

Identified Actors (ALL must be present): {actors_text}

Class Diagram:
{class_diagram}

Sequence Diagram:
{sequence_diagram}

IMPORTANT VERIFICATION RULES:
1. Check if EACH identified actor appears as a class in the class diagram
2. Check if EACH identified actor appears as a participant in the sequence diagram  
3. Do NOT consider "System" as a valid actor - it's too generic
4. An actor is MISSING if it's in the identified list but not found in the diagrams
5. Be strict about actor presence - partial matches don't count

Analyze and return JSON with:
{{
    "missing_actors": [actors from identified list that are completely absent from diagrams],
    "present_actors": [actors that are properly represented in both diagrams],
    "class_diagram_actors": [actors found in class diagram],
    "sequence_diagram_actors": [actors found in sequence diagram],
    "inconsistencies": [specific issues between class and sequence diagrams],
    "generic_elements": [any overly generic elements like "System" that should be avoided],
    "recommendations": [specific improvement suggestions],
    "overall_score": float (0.0 to 1.0 based on actor coverage)
}}

Be extremely strict about missing actors. If an identified actor is not explicitly present in the diagrams, it MUST be listed as missing."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict UML diagram analyst. Thoroughly verify that ALL identified actors are present in diagrams. Do not be lenient - missing actors must be flagged."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent analysis
                max_tokens=1000
            )
            
            try:
                import json
                verification_result = json.loads(response.choices[0].message.content)
                
                # Additional verification check - ensure we're not missing obvious actors
                class_diagram_lower = class_diagram.lower()
                sequence_diagram_lower = sequence_diagram.lower()
                
                detected_missing = []
                detected_present = []
                
                for actor in identified_actors:
                    actor_lower = actor.lower()
                    
                    # Check if actor appears in class diagram (as a class)
                    class_present = (f"class {actor_lower}" in class_diagram_lower or 
                                f"class {actor}" in class_diagram)
                    
                    # Check if actor appears in sequence diagram (as participant/actor)
                    sequence_present = (f"participant {actor_lower}" in sequence_diagram_lower or 
                                    f"actor {actor_lower}" in sequence_diagram_lower or
                                    f"participant {actor}" in sequence_diagram or
                                    f"actor {actor}" in sequence_diagram)
                    
                    if class_present and sequence_present:
                        detected_present.append(actor)
                    else:
                        detected_missing.append(actor)
                        print(f"DETECTED MISSING: '{actor}' - Class present: {class_present}, Sequence present: {sequence_present}")
                
                # Override LLM results with our more accurate detection
                verification_result['missing_actors'] = detected_missing
                verification_result['present_actors'] = detected_present
                verification_result['overspecified_classes'] = overspecified_actors
                verification_result['incorrect_classes'] = incorrect_actors
                
                # Add statistics for the frontend
                total_actors = len(identified_actors)
                missing_actors = len(detected_missing)
                actor_coverage = (total_actors - missing_actors) / total_actors if total_actors > 0 else 0
                
                verification_result['statistics'] = {
                    'total_identified_actors': len(identified_actors),
                    'present_count': len(detected_present),
                    'missing_count': len(detected_missing),
                    'overspecified_count': len(overspecified_actors),
                    'coverage_percentage': actor_coverage * 100
                }
                
                # Recalculate score based on actual actor coverage
                verification_result['overall_score'] = actor_coverage
                
                print(f"Verification Summary:")
                print(f"  Total identified actors: {total_actors}")
                print(f"  Present actors: {detected_present}")
                print(f"  Missing actors: {detected_missing}")
                print(f"  Overspecified actors: {overspecified_actors}")
                print(f"  Actor coverage: {actor_coverage:.2%}")
                
                return verification_result
                
            except json.JSONDecodeError:
                # Fallback - manually check all actors
                detected_missing = []
                detected_present = []
                
                for actor in identified_actors:
                    actor_lower = actor.lower()
                    class_present = f"class {actor_lower}" in class_diagram.lower() or f"class {actor}" in class_diagram
                    sequence_present = (f"participant {actor_lower}" in sequence_diagram.lower() or 
                                    f"actor {actor_lower}" in sequence_diagram.lower() or
                                    f"participant {actor}" in sequence_diagram or
                                    f"actor {actor}" in sequence_diagram)
                    
                    if class_present and sequence_present:
                        detected_present.append(actor)
                    else:
                        detected_missing.append(actor)
                
                return {
                    "missing_actors": detected_missing,
                    "present_actors": detected_present,
                    "overspecified_classes": overspecified_actors,
                    "incorrect_classes": incorrect_actors,
                    "class_diagram_actors": [],
                    "sequence_diagram_actors": [],
                    "inconsistencies": ["Unable to parse verification results"],
                    "generic_elements": ["System"],
                    "recommendations": ["Manual review recommended", "Regenerate diagrams with all actors"],
                    "statistics": {
                        'total_identified_actors': len(identified_actors),
                        'present_count': len(detected_present),
                        'missing_count': len(detected_missing),
                        'overspecified_count': len(overspecified_actors),
                        'coverage_percentage': (len(detected_present) / len(identified_actors) * 100) if identified_actors else 0
                    },
                    "overall_score": len(detected_present) / len(identified_actors) if identified_actors else 0.0
                }
                
        except Exception as e:
            print(f"Error verifying diagrams: {str(e)}")
            return {
                "missing_actors": identified_actors,
                "present_actors": [],
                "overspecified_classes": [],
                "incorrect_classes": [],
                "class_diagram_actors": [],
                "sequence_diagram_actors": [],
                "inconsistencies": [f"Verification failed: {str(e)}"],
                "generic_elements": ["System"],
                "recommendations": ["Manual review required", "Regenerate diagrams"],
                "statistics": {
                    'total_identified_actors': len(identified_actors),
                    'present_count': 0,
                    'missing_count': len(identified_actors),
                    'overspecified_count': 0,
                    'coverage_percentage': 0
                },
                "overall_score": 0.0
            }

    async def extract_actors_from_requirements(self, original_requirements: str, class_diagram: str, sequence_diagram: str) -> List[str]:
            """
            Extract actors from original requirements and verify against generated diagrams
            """
            try:
                # Use NLP to extract potential actors from requirements
                extracted_actors = []
                if self.nlp:
                    doc = self.nlp(original_requirements)
                    # Extract actors using NER and POS tagging
                    for ent in doc.ents:
                        if ent.label_ in ['PERSON', 'ORG', 'GPE']:
                            extracted_actors.append(ent.text)
                    # Extract actors from nouns that might represent roles or domain entities
                    role_keywords = ['user', 'admin', 'administrator', 'customer', 'member', 'librarian', 'student', 'teacher', 'manager', 'employee', 'staff', 'operator', 'supervisor', 'owner', 'guest', 'visitor']
                    domain_entities = ['book', 'library', 'document', 'article', 'journal', 'magazine', 'publication', 'author', 'publisher', 'reader', 'patron', 'borrower']
                    # Words that should not be considered actors even if capitalized
                    excluded_words = [
                        # UI/Navigation
                        'view', 'click', 'enter', 'select', 'login', 'issue', 'return', 
                        'home', 'page', 'button', 'id', 'details', 'form', 'dialog',
                        'window', 'screen', 'panel', 'catalog', 'list', 'search',
                        
                        # Technical/System
                        'system', 'database', 'service', 'handler', 'controller', 
                        'manager', 'api', 'interface', 'factory', 'builder',
                        
                        # Data/Records
                        'record', 'data', 'info', 'log', 'history', 'report', 
                        'category', 'type', 'status', 'config', 'setting',
                        
                        # Plurals
                        'books', 'members', 'users', 'records', 'categories', 'items'
                    ]
                    for token in doc:
                        # Skip if it's an excluded word
                        if token.text.lower() in excluded_words:
                            continue
                        # Check for role-based actors
                        if token.pos_ == 'NOUN' and token.text.lower() in role_keywords:
                            extracted_actors.append(token.text.capitalize())
                        # Check for domain-specific entities that could be actors
                        elif token.pos_ == 'NOUN' and token.text.lower() in domain_entities:
                            extracted_actors.append(token.text.capitalize())
                        # Check for capitalized nouns that might be proper nouns (entities/systems)
                        elif token.pos_ in ['NOUN', 'PROPN'] and token.text[0].isupper() and len(token.text) > 2:
                            # Avoid common words that are capitalized due to sentence start
                            if token.i > 0 or token.text.lower() not in ['the', 'a', 'an', 'this', 'that']:
                                # Additional check: don't include if it's actually a verb being used as noun
                                if not (token.lemma_.lower() in ['view', 'click', 'enter', 'select', 'login']):
                                    extracted_actors.append(token.text)

                # 1. Manually extract actors from class diagram
                manual_diagram_actors = self._extract_actors_from_class_diagram(class_diagram)
                print(f"Manual diagram actors: {manual_diagram_actors}")

                # Also extract ALL classes from diagram for overspecification detection
                raw_diagram_classes = self._extract_all_classes_from_diagram(class_diagram)
                print(f"All diagram classes: {raw_diagram_classes}")

                # Also use LLM to extract actors from requirements text
                prompt = f"""Analyze the following requirements and identify ONLY the human roles and external entities that interact with the system.

Requirements:
{original_requirements}

IMPORTANT: Only extract ACTORS (users, roles, people, external systems) - NOT technical classes, pages, or data entities.

Examples of VALID actors: User, Admin, Librarian, Member, Guest, Customer, Student, Teacher
Examples of INVALID actors: LoginPage, Database, BookCatalog, IssueRecord, HomePage, Category, Service

Focus ONLY on:
1. Human roles (Admin, User, Librarian, Member, Guest, etc.)
2. External systems that the main system interacts with
3. Stakeholders who use or interact with the system

DO NOT include:
- UI pages (LoginPage, HomePage, etc.)
- Technical services (DatabaseService, etc.)
- Data records (IssueRecord, Category, etc.)
- System components or classes

Return only the valid actor names separated by commas, nothing else."""

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert requirements analyst. Extract actors from requirements text."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=200
                )

                llm_actors = [actor.strip() for actor in response.choices[0].message.content.split(',')]
                print(f"LLM extracted actors: {llm_actors}")
                print(f"spaCy extracted actors: {extracted_actors}")

                # Combine and deduplicate actors
                all_actors = list(set(extracted_actors + llm_actors + manual_diagram_actors))
                print(f"All actors before filtering: {all_actors}")

                # Filter out empty strings and overly generic terms
                excluded_terms = [
                    # Technical/System terms
                    'system', 'database', 'application', 'data', 'information', 'details', 
                    'management', 'service', 'handler', 'controller', 'manager', 'api',
                    
                    # UI/Navigation terms
                    'view', 'click', 'enter', 'select', 'login', 'home', 'page', 'button', 
                    'id', 'form', 'dialog', 'window', 'screen', 'panel', 'catalog', 'list',
                    
                    # Data/Record terms
                    'record', 'log', 'history', 'report', 'category', 'type', 'status',
                    'config', 'setting', 'preference', 'item', 'object', 'entity',
                    
                    # Plural forms that are usually not actors
                    'books', 'members', 'users', 'records', 'categories', 'items',
                    
                    # Common non-actor terms
                    'issuerecord', 'loginpage', 'databaseservice', 'homepage', 'bookcatalog',
                    'userdetailspage', 'searchpage', 'listpage'
                ]
                
                filtered_actors = [
                    actor for actor in all_actors 
                    if actor and len(actor) > 1 and actor.lower() not in excluded_terms 
                    and not actor.endswith('.') and not actor.endswith('page') 
                    and not actor.endswith('service') and not actor.endswith('record')
                    and not actor.endswith('catalog') and not actor.endswith('list')
                ]
                
                print(f"Filtered actors: {filtered_actors}")

                # Resolve semantic conflicts between similar actors (e.g., User vs Member)
                resolved_actors = self._resolve_actor_conflicts(filtered_actors, original_requirements)
                print(f"Final resolved actors: {resolved_actors}")

                # Detect overspecified/incorrect actors from class diagram
                # Use raw diagram classes (not filtered ones) to detect overspecification
                overspecified_actors = [
                    actor for actor in raw_diagram_classes
                    if actor not in resolved_actors
                ]
                
                # Detect incorrect actors (generic/technical classes that shouldn't be actors)
                incorrect_actors = []
                incorrect_patterns = ['system', 'database', 'service', 'page', 'record', 'catalog', 'home', 'login', 'details', 'validation', 'category']
                for actor in overspecified_actors:
                    if any(pattern in actor.lower() for pattern in incorrect_patterns):
                        incorrect_actors.append(actor)
                
                # Log overspecified actors for debugging
                if overspecified_actors:
                    print(f"Overspecified actors detected: {overspecified_actors}")
                    print(f"These actors appear in class diagram but not in requirements analysis")
                
                if incorrect_actors:
                    print(f"Incorrect actors detected: {incorrect_actors}")
                    print(f"These are generic/technical classes that shouldn't be actors")

                return resolved_actors[:10]  # Limit to 10 actors for manageable processing

            except Exception as e:
                print(f"Error extracting actors: {str(e)}")
                return ['User', 'System', 'Admin']  # Fallback actors
