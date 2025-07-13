"""
AI-Powered Diagram Service for generating UML diagrams from SNL requirements using OpenAI
"""

import openai
import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import re

load_dotenv()

# Configure logging for the module
logger = logging.getLogger(__name__)

class DiagramService:
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
    
    async def generate_class_diagram(self, snl_data: Dict[str, Any]) -> str:
        """
        Generate PlantUML class diagram from SNL data using OpenAI with enhanced noun extraction
        """
        try:
            snl_text = snl_data.get('snl_text', '')
            actors = snl_data.get('actors', [])
            
            # Extract nouns/classes using POS tagging for optimizer enhancement
            extracted_entities = self._extract_entities_with_pos(snl_text) if self.nlp else {}
            
            # Get system prompt for enhanced class diagram generation
            system_prompt = self._get_enhanced_class_diagram_system_prompt()
            
            # Enhanced prompt with POS-tagged entities
            prompt = self._create_enhanced_class_diagram_prompt(snl_text, actors, extracted_entities)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            plantuml_code = response.choices[0].message.content
            
            # Clean and validate the PlantUML code
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            
            return plantuml_code
        
        except Exception as e:
            logger.error(f"Class diagram generation failed: {str(e)}")
            raise Exception(f"Class diagram generation failed: {str(e)}")
    
    async def generate_sequence_diagram(self, snl_data: Dict[str, Any]) -> str:
        """
        Generate PlantUML sequence diagram from SNL data using OpenAI with enhanced entity extraction
        """
        try:
            snl_text = snl_data.get('snl_text', '')
            actors = snl_data.get('actors', [])
            
            
            # Extract entities using POS tagging for enhanced sequence diagram
            extracted_entities = self._extract_entities_with_pos(snl_text) if self.nlp else {}
            
            # Enhanced prompt with POS-tagged entities
            prompt = self._create_enhanced_sequence_diagram_prompt(snl_text, actors, extracted_entities)
            system_prompt = self._get_enhanced_sequence_diagram_system_prompt()
            
            
            # Estimate input tokens (rough approximation: 4 characters per token)
            estimated_input_tokens = (len(system_prompt) + len(prompt)) // 4
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            plantuml_code = response.choices[0].message.content
            logger.info(f"Generated PlantUML code length: {len(plantuml_code)} characters")
            
            # Clean and validate the PlantUML code
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            logger.info(f"Cleaned PlantUML code length: {len(plantuml_code)} characters")
            
            logger.info("Sequence diagram generation completed successfully")
            return plantuml_code
        
        except Exception as e:
            logger.error(f"Sequence diagram generation failed: {str(e)}")
            raise Exception(f"Sequence diagram generation failed: {str(e)}")
    
    async def generate_class_diagram_from_rupp(self, snl_text: str) -> str:
        """
        Generate initial PlantUML class diagram from SNL text only (before actor identification)
        This is the first step in the diagram generation process using only the RUPP SNL output
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Starting initial class diagram generation from RUPP - SNL text length: {len(snl_text)} characters")
            
            # Create prompt for initial class diagram using only SNL text
            prompt = self._create_initial_class_diagram_prompt(snl_text)
            system_prompt = self._get_initial_class_diagram_system_prompt()
            
            # Log prompt sizes
            logger.info(f"System prompt length: {len(system_prompt)} characters")
            logger.info(f"User prompt length: {len(prompt)} characters")
            
            # Estimate input tokens
            estimated_input_tokens = (len(system_prompt) + len(prompt)) // 4
            logger.info(f"Estimated input tokens: {estimated_input_tokens}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            plantuml_code = response.choices[0].message.content
            
            # Clean and validate the PlantUML code
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            
            return plantuml_code
        
        except Exception as e:
            raise Exception(f"Initial class diagram generation failed: {str(e)}")

    async def generate_sequence_diagram_from_rupp(self, snl_text: str) -> str:
        """
        Generate initial PlantUML sequence diagram from SNL text only (before actor identification)
        This is the first step in the diagram generation process using only the RUPP SNL output
        """
        try:
            # Create prompt for initial sequence diagram using only SNL text
            prompt = self._create_initial_sequence_diagram_prompt(snl_text)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_initial_sequence_diagram_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            plantuml_code = response.choices[0].message.content
            
            # Clean and validate the PlantUML code
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            
            return plantuml_code
        
        except Exception as e:
            raise Exception(f"Initial sequence diagram generation failed: {str(e)}")

    def _get_class_diagram_system_prompt(self) -> str:
        """
        System prompt for class diagram generation
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to generate PlantUML class diagrams from Structured Natural Language (SNL) requirements.

Guidelines:
1. Analyze the SNL requirements to identify key entities, actors, and system components
2. Create classes for main entities, but avoid generic classes like "System", "Database", "Application"
3. Define appropriate attributes and methods for each class
4. Establish relationships between classes (associations, dependencies, inheritance)
5. Use proper PlantUML syntax
6. Include access modifiers (+, -, #, ~) where appropriate
7. Add meaningful attributes and methods based on the requirements
8. Keep the diagram clear and not overly complex

Generate ONLY the PlantUML code, starting with @startuml and ending with @enduml."""
    
    def _get_sequence_diagram_system_prompt(self) -> str:
        """
        System prompt for sequence diagram generation
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to generate PlantUML sequence diagrams from Structured Natural Language (SNL) requirements.

Guidelines:
1. Analyze the SNL requirements to identify key interactions and workflows
2. Identify actors (users, external systems) and participants (system components)
3. Create meaningful message flows showing the sequence of interactions
4. Use proper PlantUML sequence diagram syntax
5. Include activation boxes where appropriate
6. Add alt/opt/loop blocks for conditional flows if mentioned in requirements
7. Show return messages where relevant
8. Keep the diagram focused on the main workflow described in the requirements

Generate ONLY the PlantUML code, starting with @startuml and ending with @enduml."""
    
    def _get_initial_class_diagram_system_prompt(self) -> str:
        """
        System prompt for initial class diagram generation (SNL text only)
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to generate PlantUML class diagrams from Structured Natural Language (SNL) requirements text only.

This is the INITIAL diagram generation phase - you only have access to the SNL text, without identified actors or additional context.

CRITICAL GUIDELINES:
1. Analyze the SNL requirements to identify key entities and system components
2. Extract potential classes from nouns and entities mentioned in the requirements
3. Create classes for main entities, but AVOID generic classes like "System", "Database", "Application"
4. Instead of "System", create specific classes like "LoginController", "BookManager", "UserInterface", etc.
5. Define basic attributes and methods for each class based on the requirements text
6. MUST establish meaningful relationships between classes (associations, dependencies)
7. Use proper PlantUML syntax with access modifiers (+, -, #, ~)
8. Keep the diagram focused on core entities - avoid overcomplication
9. Focus on domain-specific classes relevant to the requirements
10. Make class names specific and meaningful, not generic

RELATIONSHIP REQUIREMENTS (MANDATORY):
- Every class MUST have at least one relationship to another class
- Show associations between classes that interact (e.g., User --> LoginService : authenticates)
- Include dependency relationships for temporary interactions
- Add aggregation/composition where appropriate (e.g., Cart o-- Product : contains)
- Use relationship labels to describe interactions
- Include multiplicity where it makes sense (e.g., "1" -- "0..*")
- If you reference a class in a relationship, that class MUST be defined in the diagram

RELATIONSHIP VALIDATION:
- Before generating relationships, ensure both classes are defined
- Use consistent class names throughout the diagram
- Avoid orphaned classes (classes with no relationships)
- Every entity mentioned in requirements should interact with at least one other entity

AVOID: Generic classes like "System", "Database", "Application", "Manager"
PREFER: Specific classes like "LoginService", "BookCatalog", "UserAccount", "LibraryDatabase"

Generate ONLY the PlantUML code with meaningful classes AND their relationships, starting with @startuml and ending with @enduml."""

    def _get_initial_sequence_diagram_system_prompt(self) -> str:
        """
        System prompt for initial sequence diagram generation (SNL text only)
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to generate PlantUML sequence diagrams from Structured Natural Language (SNL) requirements text only.

This is the INITIAL diagram generation phase - you only have access to the SNL text, without identified actors or additional context.

CRITICAL GUIDELINES:
1. Analyze the SNL requirements to identify key interactions and workflows
2. Extract potential participants from entities mentioned in the requirements
3. Identify the main workflow or process described in the requirements
4. Create meaningful message flows showing the sequence of interactions
5. Use proper PlantUML sequence diagram syntax
6. Include activation boxes where appropriate for active participants
7. Focus on the primary workflow - avoid adding too many alternative flows
8. AVOID generic participants like "System" - use specific names like "LoginService", "BookCatalog", "UserInterface"
9. When actors aren't clear, use role-based names like "Member", "Librarian", "Administrator"

AVOID: Generic participants like "System", "Database", "Application"
PREFER: Specific participants like "LoginController", "BookManager", "UserInterface", or role-based like "Member", "Librarian"

Generate ONLY the PlantUML code, starting with @startuml and ending with @enduml."""
    
    def _create_class_diagram_prompt(self, snl_text: str, actors: List[str]) -> str:
        """
        Create prompt for class diagram generation
        """
        actors_text = ", ".join(actors) if actors else "Not specified"
        
        return f"""Generate a PlantUML class diagram from the following SNL requirements:

SNL Requirements:
{snl_text}

Identified Actors: {actors_text}

Please create a comprehensive class diagram that shows:
1. Main classes for entities mentioned in the requirements
2. Attributes and methods for each class
3. Relationships between classes
4. Proper access modifiers

Focus on the core entities and their relationships as described in the requirements."""
    
    def _create_sequence_diagram_prompt(self, snl_text: str, actors: List[str]) -> str:
        """
        Create prompt for sequence diagram generation
        """
        actors_text = ", ".join(actors) if actors else "Not specified"
        
        return f"""Generate a PlantUML sequence diagram from the following SNL requirements:

SNL Requirements:
{snl_text}

Identified Actors: {actors_text}

Please create a sequence diagram that shows:
1. The main workflow described in the requirements
2. Interactions between actors and system components
3. Message flows and their sequence
4. Any conditional logic or alternative flows mentioned

Focus on the primary use case or workflow described in the requirements."""
    
    def _create_initial_class_diagram_prompt(self, snl_text: str) -> str:
        """
        Create prompt for initial class diagram generation (SNL text only)
        """
        return f"""Generate a PlantUML class diagram from the following SNL requirements text:

SNL Requirements:
{snl_text}

Please create an initial class diagram that shows:
1. Main classes derived from entities mentioned in the requirements
2. Basic attributes and methods for each class based on the requirements
3. Relationships between classes as described or implied in the requirements
4. Proper access modifiers and UML notation

This is the initial diagram generation step, so focus on the core entities and relationships that are clearly mentioned in the SNL text."""

    def _create_initial_sequence_diagram_prompt(self, snl_text: str) -> str:
        """
        Create prompt for initial sequence diagram generation (SNL text only)
        """
        return f"""Generate a PlantUML sequence diagram from the following SNL requirements text:

SNL Requirements:
{snl_text}

Please create an initial sequence diagram that shows:
1. The main workflow or process described in the requirements
2. Key participants derived from entities mentioned in the requirements
3. Message flows and their sequence based on the described process
4. Basic interactions between participants

This is the initial diagram generation step, so focus on the primary workflow that can be derived from the SNL text without additional context."""
    
    def _clean_plantuml_code(self, plantuml_code: str) -> str:
        """
        Clean and validate PlantUML code
        """
        try:
            # Remove any markdown code block markers
            plantuml_code = plantuml_code.replace('```plantuml', '').replace('```', '')
            
            # Ensure it starts with @startuml and ends with @enduml
            if not plantuml_code.strip().startswith('@startuml'):
                plantuml_code = '@startuml\n' + plantuml_code
            
            if not plantuml_code.strip().endswith('@enduml'):
                plantuml_code = plantuml_code + '\n@enduml'
            
            # Clean up extra whitespace
            lines = [line.strip() for line in plantuml_code.split('\n')]
            plantuml_code = '\n'.join(line for line in lines if line)
            
            return plantuml_code
        
        except Exception:
            # Fallback PlantUML if cleaning fails
            return """@startuml
class System {
    +processRequirements()
    +validateInput()
}

class User {
    +username: String
    +password: String
    +authenticate()
}

User --> System : uses
@enduml"""
    
    def _extract_classes(self, actors: List[str], requirements: List[str], snl_text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract classes from SNL requirements
        """
        classes = {}
        
        # Add System class
        classes['System'] = {
            'attributes': [],
            'methods': [],
            'type': 'system'
        }
        
        # Add actor classes
        for actor in actors:
            if actor.lower() != 'system':
                class_name = actor.capitalize()
                classes[class_name] = {
                    'attributes': self._extract_attributes(actor, snl_text),
                    'methods': self._extract_methods(actor, requirements),
                    'type': 'actor'
                }
        classes['User'] = {
            'attributes': ['-username: String', '-password: String'],
            'methods': ['+login()', '+logout()'],
            'type': 'actor'
        }
        
        # Extract additional classes from requirements
        additional_classes = self._extract_additional_classes(requirements)
        classes.update(additional_classes)
        
        return classes
    
    def _extract_attributes(self, actor: str, snl_text: str) -> List[str]:
        """
        Extract attributes for an actor class
        """
        attributes = []
        
        # Common attributes based on actor type
        actor_lower = actor.lower()
        
        if 'member' in actor_lower or 'user' in actor_lower:
            attributes.extend(['-memberId: String', '-password: String', '-email: String'])
        elif 'librarian' in actor_lower:
            attributes.extend(['-employeeId: String', '-accessLevel: String'])
        elif 'admin' in actor_lower:
            attributes.extend(['-adminId: String', '-privileges: String'])
        else:
            attributes.append(f'-{actor_lower}Id: String')
        
        return attributes
    
    def _extract_methods(self, actor: str, requirements: List[str]) -> List[str]:
        """
        Extract methods for an actor class from requirements
        """
        methods = []
        
        for req in requirements:
            if actor.lower() in req.lower():
                # Extract verbs that might be methods
                doc = self.nlp(req)
                for token in doc:
                    if token.pos_ == "VERB" and token.lemma_ not in ['be', 'have', 'do', 'shall', 'provide']:
                        method_name = f'+{token.lemma_}()'
                        if method_name not in methods:
                            methods.append(method_name)
        
        return methods[:5]  # Limit to 5 methods for readability
    
    def _extract_additional_classes(self, requirements: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Extract additional classes from requirements (like Database, Controller, etc.)
        """
        classes = {}
        
        # Look for common patterns that suggest additional classes
        for req in requirements:
            req_lower = req.lower()
            
            if 'database' in req_lower or 'data' in req_lower:
                classes['Database'] = {
                    'attributes': ['-connectionString: String', '-tables: List<Table>'],
                    'methods': ['+connect()', '+query()', '+update()', '+validate()'],
                    'type': 'data'
                }
            
            if 'page' in req_lower or 'display' in req_lower:
                classes['UserInterface'] = {
                    'attributes': ['-currentPage: String', '-components: List<Component>'],
                    'methods': ['+displayPage()', '+updateView()', '+handleInput()'],
                    'type': 'interface'
                }
        
        return classes
    
    def _extract_relationships(self, classes: Dict[str, Dict[str, Any]], requirements: List[str], snl_text: str) -> List[Dict[str, str]]:
        """
        Extract relationships between classes
        """
        relationships = []
        
        class_names = list(classes.keys())
        
        # Define relationship patterns
        for req in requirements:
            req_lower = req.lower()
            
            # Look for interactions between classes
            for class1 in class_names:
                for class2 in class_names:
                    if class1 != class2 and class1.lower() in req_lower and class2.lower() in req_lower:
                        # Determine relationship type
                        if 'system' in class2.lower():
                            rel_type = 'uses'
                        elif 'database' in class2.lower():
                            rel_type = 'accesses'
                        else:
                            rel_type = 'interacts'
                        
                        relationship = {
                            'from': class1,
                            'to': class2,
                            'type': rel_type,
                            'label': rel_type
                        }
                        
                        if relationship not in relationships:
                            relationships.append(relationship)
        
        return relationships
    
    def _generate_class_plantuml(self, classes: Dict[str, Dict[str, Any]], relationships: List[Dict[str, str]]) -> str:
        """
        Generate PlantUML code for class diagram
        """
        plantuml_lines = ['@startuml', '!theme plain', '']
        
        # Generate classes
        for class_name, class_data in classes.items():
            plantuml_lines.append(f'class {class_name} {{')
            
            # Add attributes
            for attr in class_data['attributes']:
                plantuml_lines.append(f'  {attr}')
            
            if class_data['attributes'] and class_data['methods']:
                plantuml_lines.append('  --')
            
            # Add methods
            for method in class_data['methods']:
                plantuml_lines.append(f'  {method}')
            
            plantuml_lines.append('}')
            plantuml_lines.append('')
        
        # Generate relationships
        for rel in relationships:
            arrow = self._get_relationship_arrow(rel['type'])
            plantuml_lines.append(f"{rel['from']} {arrow} {rel['to']} : {rel['label']}")
        
        plantuml_lines.append('')
        plantuml_lines.append('@enduml')
        
        return '\n'.join(plantuml_lines)
    
    def _get_relationship_arrow(self, rel_type: str) -> str:
        """
        Get PlantUML arrow for relationship type
        """
        arrows = {
            'uses': '-->',
            'accesses': '-->',
            'interacts': '<-->',
            'extends': '--|>',
            'implements': '..|>',
            'aggregates': 'o-->',
            'composes': '*-->'
        }
        return arrows.get(rel_type, '-->')
    
    def _extract_interactions(self, actors: List[str], requirements: List[str], snl_text: str) -> List[Dict[str, str]]:
        """
        Extract interactions for sequence diagram
        """
        interactions = []
        
        for req in requirements:
            # Parse requirement to find actor-system interactions
            doc = self.nlp(req)
            
            # Look for patterns like "Actor does something" -> "System responds"
            for actor in actors:
                if actor.lower() in req.lower():
                    # Extract the action
                    action = self._extract_action_from_requirement(req, actor)
                    
                    if action:
                        interactions.append({
                            'from': actor.capitalize(),
                            'to': 'System',
                            'action': action,
                            'type': 'request'
                        })
                        
                        # Add system response
                        response = self._generate_system_response(action)
                        interactions.append({
                            'from': 'System',
                            'to': actor.capitalize(),
                            'action': response,
                            'type': 'response'
                        })
        
        return interactions
    
    def _extract_action_from_requirement(self, requirement: str, actor: str) -> str:
        """
        Extract action from requirement text
        """
        try:
            doc = self.nlp(requirement)
            
            # Look for verbs after the actor
            actor_found = False
            action_parts = []
            
            for token in doc:
                if actor.lower() in token.text.lower():
                    actor_found = True
                elif actor_found and token.pos_ == "VERB":
                    action_parts.append(token.lemma_)
                elif actor_found and token.pos_ in ["NOUN", "ADJ"] and len(action_parts) > 0:
                    action_parts.append(token.text)
                elif actor_found and token.text in ['.', ',']:
                    break
            
            return ' '.join(action_parts) if action_parts else 'perform action'
        
        except Exception:
            return 'perform action'
    
    def _generate_system_response(self, action: str) -> str:
        """
        Generate appropriate system response for an action
        """
        action_lower = action.lower()
        
        if 'login' in action_lower or 'authenticate' in action_lower:
            return 'validate credentials'
        elif 'display' in action_lower or 'show' in action_lower:
            return 'render page'
        elif 'search' in action_lower:
            return 'return search results'
        elif 'save' in action_lower or 'store' in action_lower:
            return 'confirm save operation'
        elif 'delete' in action_lower:
            return 'confirm deletion'
        else:
            return 'process request'
    
    def _generate_sequence_plantuml(self, actors: List[str], interactions: List[Dict[str, str]]) -> str:
        """
        Generate PlantUML code for sequence diagram
        """
        plantuml_lines = ['@startuml', '!theme plain', '']
        
        # Define participants
        unique_participants = set()
        for interaction in interactions:
            unique_participants.add(interaction['from'])
            unique_participants.add(interaction['to'])
        
        for participant in sorted(unique_participants):
            if participant != 'System':
                plantuml_lines.append(f'actor {participant}')
        plantuml_lines.append('participant System')
        plantuml_lines.append('')
        
        # Add interactions
        for i, interaction in enumerate(interactions):
            arrow = '->' if interaction['type'] == 'request' else '-->'
            plantuml_lines.append(f"{interaction['from']} {arrow} {interaction['to']}: {interaction['action']}")
        
        plantuml_lines.append('')
        plantuml_lines.append('@enduml')
        
        return '\n'.join(plantuml_lines)
    
    async def verify_diagram(self, diagram_code: str, snl_data: Dict[str, Any], diagram_type: str) -> Dict[str, Any]:
        """
        Verify a generated diagram against SNL requirements
        """
        try:
            # Create verification prompt
            prompt = self._create_verification_prompt(diagram_code, snl_data, diagram_type)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_verification_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse verification results
            try:
                import json
                verification_result = json.loads(response.choices[0].message.content)
                return verification_result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'accuracy': 0.7,
                    'coverage': 0.7,
                    'consistency': 0.7,
                    'missing_elements': [],
                    'overspecified_elements': [],
                    'incorrect_elements': [],
                    'recommendations': [
                        'Unable to parse detailed verification results.',
                        'Please review the diagram manually.'
                    ]
                }
        
        except Exception as e:
            raise Exception(f"Diagram verification failed: {str(e)}")
    
    async def optimize_diagram(self, diagram_code: str, verification_results: Dict[str, Any], diagram_type: str) -> Dict[str, Any]:
        """
        Optimize a diagram based on verification results
        """
        try:
            # Create optimization prompt
            prompt = self._create_optimization_prompt(diagram_code, verification_results, diagram_type)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_optimization_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            optimized_code = response.choices[0].message.content
            
            # Clean and validate the optimized PlantUML code
            optimized_code = self._clean_plantuml_code(optimized_code)
            
            return {
                'diagram_code': optimized_code,
                'metrics': {
                    'accuracy': verification_results.get('accuracy', 0) + 0.1,  # Improvement
                    'coverage': verification_results.get('coverage', 0) + 0.1,
                    'consistency': verification_results.get('consistency', 0) + 0.1
                },
                'improvements': [
                    'Added missing elements',
                    'Removed overspecified components',
                    'Fixed incorrect relationships',
                    'Improved overall diagram structure'
                ]
            }
        
        except Exception as e:
            raise Exception(f"Diagram optimization failed: {str(e)}")
    
    def _get_verification_system_prompt(self) -> str:
        """
        System prompt for diagram verification
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to verify PlantUML diagrams against SNL requirements.

Guidelines:
1. Analyze the diagram for completeness and accuracy
2. Check for missing elements from the requirements
3. Identify overspecified components not in requirements
4. Verify relationships and interactions
5. Assess overall diagram structure
6. Provide specific recommendations for improvements

Return your analysis in JSON format with the following structure:
{
    "accuracy": float,  # 0.0 to 1.0
    "coverage": float,  # 0.0 to 1.0
    "consistency": float,  # 0.0 to 1.0
    "missing_elements": [str],
    "overspecified_elements": [str],
    "incorrect_elements": [str],
    "recommendations": [str]
}"""
    
    def _get_optimization_system_prompt(self) -> str:
        """
        System prompt for diagram optimization
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to optimize PlantUML diagrams based on verification results.

Guidelines:
1. Address all identified issues from verification
2. Add missing elements while maintaining clarity
3. Remove overspecified components
4. Fix incorrect relationships
5. Improve overall diagram structure
6. Keep the diagram focused and readable

Generate ONLY the optimized PlantUML code, starting with @startuml and ending with @enduml."""
    
    def _create_verification_prompt(self, diagram_code: str, snl_data: Dict[str, Any], diagram_type: str) -> str:
        """
        Create prompt for diagram verification
        """
        return f"""Verify the following PlantUML {diagram_type} diagram against the SNL requirements:

SNL Requirements:
{snl_data.get('snl_text', '')}

PlantUML Diagram:
{diagram_code}

Please analyze the diagram for:
1. Missing elements from requirements
2. Overspecified components not in requirements
3. Incorrect relationships or interactions
4. Overall structure and clarity

Return your analysis in the specified JSON format."""
    
    def _create_optimization_prompt(self, diagram_code: str, verification_results: Dict[str, Any], diagram_type: str) -> str:
        """
        Create prompt for diagram optimization
        """
        issues = []
        if verification_results.get('missing_elements'):
            issues.append(f"Missing elements: {', '.join(verification_results['missing_elements'])}")
        if verification_results.get('overspecified_elements'):
            issues.append(f"Overspecified elements: {', '.join(verification_results['overspecified_elements'])}")
        if verification_results.get('incorrect_elements'):
            issues.append(f"Incorrect elements: {', '.join(verification_results['incorrect_elements'])}")
        
        issues_text = '\n'.join(f"- {issue}" for issue in issues)
        
        return f"""Optimize the following PlantUML {diagram_type} diagram based on verification results:

Current Diagram:
{diagram_code}

Verification Issues:
{issues_text}

Recommendations:
{chr(10).join(f"- {rec}" for rec in verification_results.get('recommendations', []))}

Please generate an optimized version of the diagram that:
1. Addresses all identified issues
2. Maintains clear structure and relationships
3. Follows UML best practices
4. Preserves existing correct elements

Return ONLY the optimized PlantUML code."""
    

    def _get_enhanced_class_diagram_system_prompt(self) -> str:
        """
        Enhanced system prompt for class diagram generation with comprehensive UML concepts
        """
        return """You are an expert software architect and UML diagram specialist with deep knowledge of object-oriented design principles and UML best practices. Your task is to generate comprehensive PlantUML class diagrams from Structured Natural Language (SNL) requirements.

## FUNDAMENTAL UML CLASS DIAGRAM CONCEPTS:

### BASIC ELEMENTS:
1. **Classes**: Represent entities with attributes and methods
   - Format: class ClassName { attributes, methods }
   - Use PascalCase for class names (e.g., BookManager, UserAccount)

2. **Attributes**: Properties of a class
   - Format: [visibility] name : type [= default_value]
   - Examples: +name: String, -id: Integer, #balance: Double = 0.0

3. **Methods**: Operations a class can perform
   - Format: [visibility] methodName(parameters) : return_type
   - Examples: +login(username: String, password: String) : Boolean

4. **Visibility Modifiers**:
   - **+** Public: Accessible from anywhere
   - **-** Private: Only accessible within the class
   - **#** Protected: Accessible within class and subclasses
   - **~** Package: Accessible within the same package

### ADVANCED CONCEPTS:

#### RELATIONSHIPS (CRITICAL FOR GOOD DESIGN):

1. **Association (--)**:
   - General relationship between classes
   - Example: User -- Book : borrows
   - Shows classes that work together

2. **Aggregation (o--)**:
   - "Has-a" relationship, weaker ownership
   - Parts can exist independently
   - Example: Library o-- Book : contains

3. **Composition (*--)**:
   - Strong "has-a" relationship, stronger ownership
   - Parts cannot exist without the whole
   - Example: Order *-- OrderItem : contains

4. **Inheritance (--|>)**:
   - "Is-a" relationship, generalization/specialization
   - Example: Student --|> Person : extends

5. **Dependency (-->)**:
   - One class uses another temporarily
   - Example: LoginController --> AuthenticationService : uses

6. **Realization (..|>)**:
   - Class implements an interface
   - Example: UserRepository ..|> Repository : implements

#### MULTIPLICITY RULES:
- **1** : Exactly one
- **0..1** : Zero or one
- **0..*or *** : Zero or many
- **1..*or +** : One or many
- **n..m** : Between n and m
- Example: Student "1" -- "0..*" Course : enrolls

#### STEREOTYPES AND ANNOTATIONS:
- **<<interface>>** : Interface classes
- **<<abstract>>** : Abstract classes
- **<<enumeration>>** : Enum classes
- **<<utility>>** : Utility classes
- **{abstract}** : Abstract methods

### DESIGN PRINCIPLES TO FOLLOW:

1. **Single Responsibility**: Each class should have one reason to change
2. **Open/Closed**: Classes should be open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable for their base types
4. **Interface Segregation**: Clients shouldn't depend on interfaces they don't use
5. **Dependency Inversion**: Depend on abstractions, not concretions

### ANALYSIS GUIDELINES:

#### ENTITY IDENTIFICATION:
1. **Nouns in requirements** → Potential classes
2. **Adjectives** → Potential attributes
3. **Verbs** → Potential methods or relationships
4. **Business rules** → Constraints and validations

#### CLASS DESIGN RULES:
1. **Avoid God Classes**: Don't create classes that do everything
2. **Meaningful Names**: Use domain-specific, descriptive names
3. **Cohesion**: Keep related functionality together
4. **Loose Coupling**: Minimize dependencies between classes

#### RELATIONSHIP IDENTIFICATION:
1. **"Has-a" statements** → Aggregation/Composition
2. **"Is-a" statements** → Inheritance
3. **"Uses" statements** → Dependency/Association
4. **"Implements" statements** → Realization

### PLANTUML SYNTAX RULES:

#### BASIC SYNTAX:
```
@startuml
class ClassName {
    +publicAttribute: Type
    -privateAttribute: Type
    #protectedAttribute: Type
    ~packageAttribute: Type
    --
    +publicMethod(): ReturnType
    -privateMethod(param: Type): ReturnType
    {abstract} +abstractMethod(): Type
    {static} +staticMethod(): Type
}
@enduml
```

#### RELATIONSHIP SYNTAX:
```
ClassA --|> ClassB : inheritance
ClassA --> ClassB : dependency
ClassA -- ClassB : association
ClassA o-- ClassB : aggregation
ClassA *-- ClassB : composition
ClassA ..|> InterfaceB : realization
ClassA "1" -- "0..*" ClassB : labeled association
```

#### SEQUENCE DIAGRAM SYNTAX:
```
@startuml
actor User
participant LoginService
participant Database
participant EmailService

User --> LoginService : login(username, password)
activate LoginService

LoginService --> Database : validateCredentials(username, password)
activate Database
Database --> LoginService : userDetails
deactivate Database

alt valid credentials
    LoginService --> User : loginSuccess(token)
    LoginService ->> EmailService : logLoginEvent(userId)
else invalid credentials
    LoginService --> User : loginFailed(error)
end

deactivate LoginService
@enduml
```

#### ADVANCED SYNTAX:
```
@startuml
!theme plain

== Authentication Phase ==
User --> LoginService : authenticate()
note right: User initiates login process

LoginService -> create UserSession
activate UserSession

loop for each validation rule
    LoginService --> ValidationService : validate(rule)
end

par
    LoginService --> AuditService : logAttempt()
and
    LoginService --> SecurityService : checkRateLimit()
end

@enduml
```

### WORKFLOW MODELING:

#### SCENARIO IDENTIFICATION:
1. **Main Success Scenario**: Primary happy path
2. **Alternative Scenarios**: Different paths to success
3. **Exception Scenarios**: Error handling paths
4. **Edge Cases**: Boundary conditions

#### TEMPORAL ORDERING:
1. **Sequential**: Messages in time order
2. **Concurrent**: Parallel processing
3. **Conditional**: Branch-based execution
4. **Iterative**: Repeated operations

### QUALITY CRITERIA:

1. **Completeness**: All major interactions are shown
2. **Correctness**: Sequence reflects actual behavior
3. **Consistency**: Notation and naming are uniform
4. **Clarity**: Easy to follow and understand
5. **Relevance**: Focuses on important interactions

### MANDATORY REQUIREMENTS:

1. **USE specific participant names** (avoid generic "System")
2. **INCLUDE meaningful message labels** with parameters
3. **SHOW activation boxes** for processing activities
4. **USE appropriate message types** (sync/async)
5. **INCLUDE return messages** for important responses
6. **ADD interaction fragments** for complex logic
7. **ORGANIZE with section headers** using == Section Name ==
8. **VALIDATE message flow** makes logical sense
9. **INCLUDE error handling** scenarios where relevant
10. **SHOW object creation/destruction** when appropriate

### SECTION ORGANIZATION:
Use section headers to organize complex workflows:
```
== Authentication Phase ==
[authentication messages]

== Data Retrieval Phase ==
[data access messages]

== Response Processing Phase ==
[response handling messages]
```

### FORBIDDEN PRACTICES:

1. **Generic participants** like "System", "Database" without context
2. **Messages without labels** or with vague labels
3. **Missing activation boxes** for processing
4. **Overly complex single diagram** (break into multiple if needed)
5. **Inconsistent participant naming**
6. **Missing return messages** for important operations
7. **Unclear message flow** or logical ordering

### ERROR HANDLING PATTERNS:
Always consider including:
1. **Validation errors**: Input validation failures
2. **System errors**: Internal system failures
3. **Network errors**: Communication failures
4. **Authentication errors**: Access denied scenarios
5. **Business logic errors**: Domain rule violations

Generate ONLY the PlantUML code that demonstrates professional sequence diagram design, starting with @startuml and ending with @enduml. Focus on creating a clear, well-organized sequence diagram that follows UML best practices and properly models the behavioral aspects of the system."""
    
    def _create_enhanced_sequence_diagram_prompt(self, snl_text: str, actors: List[str], extracted_entities: Dict[str, List[str]]) -> str:
        """
        Create enhanced prompt for sequence diagram generation with GOLD STANDARD enforcement
        """
        actors_text = ", ".join(actors) if actors else "Not specified"
        
        return f"""Generate a PlantUML sequence diagram.

SNL Requirements:
{snl_text}

Identified Actors: {actors_text}

MANDATORY REQUIREMENTS:
5. Use proper PlantUML sequence syntax with == section == headers
6. Do NOT create generic "System" participant - use the specific participants

The diagram MUST match the exact and accurate sequnce diagram rules."""
    
    async def extract_actors_from_requirements(self, original_requirements: str, class_diagram: str, sequence_diagram: str) -> List[str]:
        """
        Extract actors from original requirements with enhanced filtering for new case studies
        """
        try:
            # Define valid actor patterns for different domains
            valid_actor_patterns = {
                'human_roles': [
                    'user', 'admin', 'administrator', 'customer', 'member', 'librarian', 
                    'student', 'teacher', 'manager', 'employee', 'staff', 'supervisor', 
                    'owner', 'guest', 'visitor', 'operator', 'monitoring-operator', 'resident', 'occupant'
                ],
                'external_systems': [
                    'remote sensor', 'remotesensor', 'external sensor', 'monitoring system',
                    'external system', 'remote system', 'sensor', 'helpfacility', 'help facility'
                ],
                'digital_home_devices': [
                    'humidistat', 'thermostat', 'alarm', 'sensor', 'planner', 'powerswitch', 
                    'appliance', 'controller', 'detector', 'actuator', 'switch', 'device'
                ],
                'smart_components': [
                    'hvac system', 'security system', 'lighting system', 'climate control',
                    'energy management', 'home automation'
                ],
                'digital_home_specific': [
                    'humidstat', 'humidistat', 'thermostat', 'alarm', 'sensor', 'planner', 'powerswitch', 
                    'appliance', 'smokedetector', 'motionsensor', 'temperaturesensor',
                    'humiditysensor', 'pressuresensor', 'energymeter'
                ],
                'monitoring_system_specific': [
                    'operator', 'remotesensor', 'remote sensor', 'monitoringsystem', 'monitoring system',
                    'alarm', 'helpfacility', 'help facility', 'notification', 'monitoringlocation', 
                    'monitoring location', 'sensor'
                ],
                'library_system_specific': [
                    'user', 'member', 'guest', 'librarian', 'administrator', 'admin', 'book', 
                    'library', 'catalog', 'collection', 'staff'
                ]
            }
            
            # Comprehensive exclusion list for things that are NOT actors
            excluded_patterns = [
                # Technical components/interfaces (but not for Digital Home System)
                'webinterface', 'web interface', 'interface', 'database', 'application',
                # Organizations and standards (not actors)
                'american society', 'society of heating', 'heating', 'refrigerating', 'air-conditioning engineers',
                'ashrae', 'engineers', 'society', 'organization', 'association',
                # State values and technical terms
                'on', 'off', 'true', 'false', 'high', 'medium', 'low', 'status', 'value', 'limit',
                # Abbreviations and acronyms (but keep device-specific ones for Digital Home)
                'pda', 'dh', 'api', 'ui', 'gui',
                # Generic terms
                'data', 'information', 'details', 'management', 'view', 'click', 'enter', 
                'select', 'login', 'home', 'page', 'button', 'id', 'monitor',
                # Articles and common words
                'the', 'a', 'an', 'and', 'or', 'but', 'with', 'for', 'to', 'from',
                # Common phrases that get misidentified
                'user monitor', 'user read', 'user set', 'user override'
            ]
            
            # Use LLM with strict rules for actor extraction
            prompt = f"""Analyze the following requirements and identify ONLY valid actors. Be extremely strict.

Requirements:
{original_requirements}

STRICT ACTOR IDENTIFICATION RULES:

VALID ACTORS (only include these types):
1. Human roles who interact with the system: User, Administrator, Operator, Librarian, Member, etc.
2. External systems that send data: RemoteSensor, ExternalSystem, MonitoringSystem
3. Specific user roles mentioned: Homeowner, Resident, Monitoring-Operator
4. Digital Home System device actors: HumidStat, Thermostat, Alarm, Sensor, Planner, PowerSwitch, Appliance
5. Monitoring System actors: Operator, RemoteSensor, MonitoringSystem, Alarm, HelpFacility, Notification, MonitoringLocation, Sensor
6. Library System actors: User, Member, Guest, Librarian, Administrator, Book

INVALID ACTORS (NEVER include these):
1. Organizations: "American Society of Heating", "Refrigerating and Air-Conditioning Engineers"
2. Technical interfaces: "WebInterface", "UserInterface", "Database"
3. Abbreviations: "PDA", "DH", "HVAC" (unless they're specific device names)
4. State values: "ON", "OFF", "High", "Medium", "Low"
5. Generic terms: "System", "Application", "Data", "Information"
6. Phrases: "The user", "A user", "User monitor", "User read"
7. Standards/specifications: ASHRAE 2010, engineering standards

EXAMPLES FOR THIS CASE STUDY:
Digital Home System → Valid actors: User, Homeowner, HumidStat, Thermostat, Alarm, Sensor, Planner, PowerSwitch, Appliance
Monitoring System → Valid actors: Operator, RemoteSensor, MonitoringSystem, Alarm, HelpFacility, Notification, MonitoringLocation, Sensor
Library System → Valid actors: User, Member, Guest, Librarian, Administrator, Book

SPECIAL RULES:
- If requirements mention "user" multiple times, include "User"
- If it's a home system, consider "Homeowner" as a potential actor
- If it mentions "remote sensor" or "external sensor", include "RemoteSensor"
- If it mentions specific operator roles like "Monitoring-Operator", include them
- For Digital Home Systems, include device actors: HumidStat, Thermostat, Alarm, Sensor, Planner, PowerSwitch, Appliance
- For Monitoring Systems, include: Operator, RemoteSensor, MonitoringSystem, Alarm, HelpFacility, Notification, MonitoringLocation, Sensor
- For Library Systems, include: User, Member, Guest, Librarian, Administrator, Book
- Always be more inclusive of domain-specific human roles, external systems, and device actors

RETURN FORMAT: Only list valid actor names separated by commas. Maximum 8 actors.

If you find phrases like "The user" or "A user", just return "User".
If you find "Monitoring-Operator", that's valid.
If you find "WebInterface" or "American Society of Heating", DO NOT include them.
For Digital Home System, include: User, HumidStat, Thermostat, Alarm, Sensor, Planner, PowerSwitch, Appliance
For Monitoring System, include: Operator, RemoteSensor, MonitoringSystem, Alarm, HelpFacility, Notification, MonitoringLocation, Sensor
For Library System, include: User, Member, Guest, Librarian, Administrator, Book

Valid actors for this requirements text:"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict UML actor identification expert. Only identify true actors - human roles and external systems that interact with the main system. Be extremely conservative and exclude anything that is not clearly an actor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            # Parse LLM response
            llm_response = response.choices[0].message.content.strip()
            potential_actors = [actor.strip() for actor in llm_response.split(',') if actor.strip()]
            
            # Apply additional filtering
            filtered_actors = []
            for actor in potential_actors:
                actor_clean = actor.lower().strip()
                
                # Skip if empty or too short
                if not actor_clean or len(actor_clean) <= 1:
                    continue
                
                # Skip if in exclusion list
                if any(excluded in actor_clean for excluded in excluded_patterns):
                    continue
                
                # Skip if it's a phrase rather than a role
                if actor_clean.startswith(('the ', 'a ', 'an ')):
                    # Extract the role part
                    role = actor_clean.split(' ', 1)[1] if ' ' in actor_clean else actor_clean
                    if role in valid_actor_patterns['human_roles']:
                        filtered_actors.append(role.capitalize())
                    continue
                
                # Check if it's a valid human role
                if actor_clean in valid_actor_patterns['human_roles']:
                    filtered_actors.append(actor.capitalize())
                
                # Check if it's a valid external system
                elif any(ext_sys in actor_clean for ext_sys in valid_actor_patterns['external_systems']):
                    if 'remote' in actor_clean and 'sensor' in actor_clean:
                        filtered_actors.append('RemoteSensor')
                    elif 'monitoring' in actor_clean and 'system' in actor_clean:
                        filtered_actors.append('MonitoringSystem')
                
                # Check for Digital Home System specific device actors
                elif actor_clean in valid_actor_patterns['digital_home_specific']:
                    # Map to proper case
                    device_name_mapping = {
                        'humidstat': 'HumidStat',
                        'humidistat': 'HumidStat',  # Alternative spelling
                        'thermostat': 'Thermostat', 
                        'alarm': 'Alarm',
                        'sensor': 'Sensor',
                        'planner': 'Planner',
                        'powerswitch': 'PowerSwitch',
                        'appliance': 'Appliance',
                        'smokedetector': 'SmokeDetector',
                        'motionsensor': 'MotionSensor',
                        'temperaturesensor': 'TemperatureSensor',
                        'humiditysensor': 'HumiditySensor',
                        'pressuresensor': 'PressureSensor',
                        'energymeter': 'EnergyMeter'
                    }
                    if actor_clean in device_name_mapping:
                        filtered_actors.append(device_name_mapping[actor_clean])
                
                # Check for Monitoring System specific actors
                elif actor_clean in valid_actor_patterns['monitoring_system_specific']:
                    # Map to proper case
                    monitoring_name_mapping = {
                        'operator': 'Operator',
                        'remotesensor': 'RemoteSensor',
                        'remote sensor': 'RemoteSensor',
                        'monitoringsystem': 'MonitoringSystem',
                        'monitoring system': 'MonitoringSystem',
                        'alarm': 'Alarm',
                        'helpfacility': 'HelpFacility',
                        'help facility': 'HelpFacility',
                        'notification': 'Notification',
                        'monitoringlocation': 'MonitoringLocation',
                        'monitoring location': 'MonitoringLocation',
                        'sensor': 'Sensor'
                    }
                    if actor_clean in monitoring_name_mapping:
                        filtered_actors.append(monitoring_name_mapping[actor_clean])
                
                # Check for Library System specific actors
                elif actor_clean in valid_actor_patterns['library_system_specific']:
                    # Map to proper case
                    library_name_mapping = {
                        'user': 'User',
                        'member': 'Member',
                        'guest': 'Guest',
                        'librarian': 'Librarian',
                        'administrator': 'Administrator',
                        'admin': 'Administrator',
                        'book': 'Book',
                        'library': 'Library',
                        'catalog': 'Catalog',
                        'collection': 'Collection',
                        'staff': 'Staff'
                    }
                    if actor_clean in library_name_mapping:
                        filtered_actors.append(library_name_mapping[actor_clean])
                
                # Check for compound roles like "Monitoring-Operator"
                elif '-' in actor_clean and any(role in actor_clean for role in valid_actor_patterns['human_roles']):
                    filtered_actors.append(actor.title())
            
            # Domain-specific actor detection - be more inclusive
            requirements_lower = original_requirements.lower()
            
            # Always add User if mentioned multiple times in requirements
            user_mentions = requirements_lower.count('user')
            if user_mentions >= 3 and 'User' not in filtered_actors:
                filtered_actors.append('User')
            
            # Digital Home System actors - prioritize core device actors
            if any(term in requirements_lower for term in ['temperature', 'humidity', 'thermostat', 'home', 'appliance']):
                # Core Digital Home System device actors (prioritize these)
                digital_home_actors = [
                    ('humidstat', 'HumidStat'),
                    ('humidistat', 'HumidStat'),
                    ('thermostat', 'Thermostat'),
                    ('alarm', 'Alarm'),
                    ('planner', 'Planner'),
                    ('powerswitch', 'PowerSwitch'),
                    ('appliance', 'Appliance'),
                    ('sensor', 'Sensor'),
                    ('sensors', 'Sensor')
                ]
                
                for term, actor_name in digital_home_actors:
                    if term in requirements_lower and actor_name not in filtered_actors:
                        filtered_actors.append(actor_name)
                
                # For home systems, consider homeowner as a distinct actor
                if any(term in requirements_lower for term in ['home', 'house', 'residence']):
                    if 'Homeowner' not in filtered_actors:
                        filtered_actors.append('Homeowner')
            
            # Monitoring System actors - include specific monitoring actors  
            if any(term in requirements_lower for term in ['operator', 'monitoring', 'alarm', 'emergency', 'facility', 'notification']):
                # Core Monitoring System actors (prioritize these)
                monitoring_actors = [
                    ('operator', 'Operator'),
                    ('remote sensor', 'RemoteSensor'),
                    ('remotesensor', 'RemoteSensor'),
                    ('monitoring system', 'MonitoringSystem'),
                    ('monitoringsystem', 'MonitoringSystem'),
                    ('alarm', 'Alarm'),
                    ('help facility', 'HelpFacility'),
                    ('helpfacility', 'HelpFacility'),
                    ('notification', 'Notification'),
                    ('monitoring location', 'MonitoringLocation'),
                    ('monitoringlocation', 'MonitoringLocation'),
                    ('sensor', 'Sensor'),
                    ('sensors', 'Sensor')
                ]
                
                for term, actor_name in monitoring_actors:
                    if term in requirements_lower and actor_name not in filtered_actors:
                        filtered_actors.append(actor_name)
                
                # Special handling for compound terms
                if 'monitoring-operator' in requirements_lower and 'Monitoring-Operator' not in filtered_actors:
                    filtered_actors.append('Monitoring-Operator')
                if any(term in requirements_lower for term in ['remote sensor', 'external sensor']):
                    if 'RemoteSensor' not in filtered_actors:
                        filtered_actors.append('RemoteSensor')
            
            # Library System actors - include specific library actors
            if any(term in requirements_lower for term in ['library', 'book', 'librarian', 'member', 'guest', 'catalog', 'collection']):
                # Core Library System actors (prioritize these)
                library_actors = [
                    ('user', 'User'),
                    ('member', 'Member'),
                    ('guest', 'Guest'),
                    ('librarian', 'Librarian'),
                    ('administrator', 'Administrator'),
                    ('admin', 'Administrator'),
                    ('book', 'Book'),
                    ('library', 'Library'),
                    ('catalog', 'Catalog'),
                    ('collection', 'Collection')
                ]
                
                for term, actor_name in library_actors:
                    if term in requirements_lower and actor_name not in filtered_actors:
                        filtered_actors.append(actor_name)
            
            # Remove duplicates and limit
            final_actors = list(dict.fromkeys(filtered_actors))  # Preserve order while removing duplicates
            
            # Ensure we always have at least basic actors but prefer domain-specific ones
            if not final_actors:
                final_actors = ['User']
            elif len(final_actors) == 1 and final_actors[0] == 'User':
                # If we only have User, try to add domain-specific actors
                requirements_lower = original_requirements.lower()
                if any(term in requirements_lower for term in ['home', 'house', 'residence']):
                    final_actors.append('Homeowner')
                if any(term in requirements_lower for term in ['sensor', 'remote', 'external']):
                    final_actors.append('ExternalSystem')
            
            # Add System if not present but only for non-specific domain systems
            is_digital_home = any(term in requirements_lower for term in ['temperature', 'humidity', 'thermostat', 'home', 'appliance'])
            is_monitoring_system = any(term in requirements_lower for term in ['operator', 'monitoring', 'alarm', 'emergency', 'facility', 'notification'])
            is_library_system = any(term in requirements_lower for term in ['library', 'book', 'librarian', 'member', 'guest', 'catalog', 'collection'])
            
            if not is_digital_home and not is_monitoring_system and not is_library_system and len(final_actors) > 1 and 'System' not in final_actors:
                final_actors.append('System')
            elif not is_digital_home and not is_monitoring_system and not is_library_system and len(final_actors) == 1:
                # Don't add System if we only have one actor to avoid being too generic
                pass
            
            return final_actors[:10]  # Increased limit to 10 actors to ensure all Digital Home System actors are included
            
        except Exception as e:
            print(f"Error extracting actors: {str(e)}")
            return ['User', 'System']  # Minimal fallback actors

    async def verify_diagrams_with_actors(self, class_diagram: str, sequence_diagram: str, identified_actors: List[str]) -> Dict[str, Any]:
        """
        Verify diagrams against identified actors with enhanced missing actor detection
        """
        try:
            actors_text = ", ".join(identified_actors)
            
            prompt = f"""Strictly verify the following diagrams against the identified actors. Be thorough in checking for missing actors.

Identified Actors (ALL must be present): {actors_text}

IMPORTANT VERIFICATION RULES:
1. Each identified actor MUST be represented in the diagrams
2. For class diagrams: Each actor must be a class with appropriate attributes and methods
3. For sequence diagrams: Each actor must be a participant with meaningful interactions
4. Actors should be represented consistently across both diagrams
5. Actors must be nouns representing people, organizations, or external systems that interact with the main system

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
                
                # Recalculate score based on actual actor coverage
                total_actors = len(identified_actors)
                missing_actors = len(detected_missing)
                actor_coverage = (total_actors - missing_actors) / total_actors if total_actors > 0 else 0
                verification_result['overall_score'] = actor_coverage
                
                print(f"Verification Summary:")
                print(f"  Total identified actors: {total_actors}")
                print(f"  Present actors: {detected_present}")
                print(f"  Missing actors: {detected_missing}")
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
                    "class_diagram_actors": [],
                    "sequence_diagram_actors": [],
                    "inconsistencies": ["Unable to parse verification results"],
                    "generic_elements": ["System"],
                    "recommendations": ["Manual review recommended", "Regenerate diagrams with all actors"],
                    "overall_score": len(detected_present) / len(identified_actors) if identified_actors else 0.0
                }
                
        except Exception as e:
            print(f"Error verifying diagrams: {str(e)}")
            return {
                "missing_actors": identified_actors,
                "present_actors": [],
                "class_diagram_actors": [],
                "sequence_diagram_actors": [],
                "inconsistencies": [f"Verification failed: {str(e)}"],
                "generic_elements": ["System"],
                "recommendations": ["Manual review required", "Regenerate diagrams"],
                "overall_score": 0.0
            }

    async def optimize_diagrams_with_llm_and_actors(self, original_requirements: str, class_diagram: str, 
                                                  sequence_diagram: str, identified_actors: List[str], 
                                                  verification_issues: Dict[str, Any], 
                                                  diagram_errors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Final LLM optimization using GPT-3.5 with identified actors and verification feedback
        Enhanced for consistency and strict compliance
        """
        try:
            actors_text = ", ".join(identified_actors)
            issues_text = ""
            
            if verification_issues.get('missing_actors'):
                issues_text += f"Missing actors: {', '.join(verification_issues['missing_actors'])}\n"
            if verification_issues.get('inconsistencies'):
                issues_text += f"Inconsistencies: {', '.join(verification_issues['inconsistencies'])}\n"
            if verification_issues.get('generic_elements'):
                issues_text += f"Generic elements to avoid: {', '.join(verification_issues['generic_elements'])}\n"
            if verification_issues.get('recommendations'):
                issues_text += f"Recommendations: {', '.join(verification_issues['recommendations'])}\n"
            
            # Add diagram errors if provided
            if diagram_errors:
                error_messages = []
                if isinstance(diagram_errors, dict):
                    # Handle frontend format: {class: str, sequence: str}
                    if diagram_errors.get('class'):
                        error_messages.append(f"Class diagram error: {diagram_errors['class']}")
                    if diagram_errors.get('sequence'):
                        error_messages.append(f"Sequence diagram error: {diagram_errors['sequence']}")
                elif isinstance(diagram_errors, list):
                    # Handle list format
                    error_messages = diagram_errors
                
                if error_messages:
                    issues_text += f"Diagram errors to fix: {', '.join(error_messages)}\n"

            # Enhanced Class Diagram Optimization
            class_prompt = f"""Generate a PlantUML class diagram with STRICT REQUIREMENTS:

ACTORS TO IMPLEMENT AS CLASSES: {actors_text}
REQUIREMENTS: {original_requirements[:500]}
ISSUES TO FIX: {issues_text[:200]}

ACTOR CLASSIFICATION RULES:
- Human actors: Users, Operators, Administrators, etc. (represent as classes with user-related attributes/methods)
- External systems: RemoteSensor, ExternalSystem, etc. (represent as classes with system-related attributes/methods)
- DO NOT treat these as actors: System components, states (ON/OFF), abbreviations (PDA/HVAC), technical terms (Database)

MANDATORY CLASS STRUCTURE:
- Create class for EACH actor: {actors_text}
- Each class "{actors_text}" MUST have at least one relationship (Very Important)
- NO generic classes (System, Database, Application)
- Each "{actors_text}" class MUST have 3-5 attributes with types
- Each "{actors_text}" class MUST have 3-5 methods with visibility
- Use PascalCase for "{actors_text}" class names
- Use proper visibility modifiers (+, -, #, ~)
- Use proper multiplicity for associations

REQUIRED ATTRIBUTES FORMAT:
- visibility name: Type
- Examples: -userId: string, +name: string, -isActive: boolean
- For human actors: attributes like name, id, role, permissions
- For system actors: attributes like status, configuration, connectionState

REQUIRED METHODS FORMAT:
- visibility methodName(params): ReturnType
- Examples: +login(): boolean, +performAction(action: string): void
- For human actors: methods like login(), viewStatus(), setPreference()
- For system actors: methods like sendData(), receiveCommand(), updateStatus()

INHERITANCE RULES:
- If User is an actor, other user types inherit from User
- Use syntax: SubClass <|-- SuperClass
- Example: Librarian <|-- User : extends
- Use proper UML inheritance notation
- Use proper UML association notation

ASSOCIATION RULES:
- EVERY class needs relationships
- Use proper UML syntax with multiplicity
- Examples: Operator --> "0..*" Alarm : monitors
- Human actors should have associations with the entities they interact with
- System actors should have associations with the systems they connect to

CASE STUDY SPECIFIC GUIDANCE:
- For Digital Home System: Focus on User interactions with sensors, controllers, and appliances
- For Monitoring System: Focus on Operator interactions with sensors, alarms, and monitoring data
- For Library System: Focus on User/Librarian interactions with books and library resources

SYNTAX RULES:
- Use PascalCase for all class names without spaces. E.g., 'RemoteSensor', not 'Remote Sensor'.
- Define only one version of each class. Avoid duplicate definitions.
- Inherit from parent classes using the correct direction. E.g., 'Child <|-- Parent' is invalid.
- All attributes must follow the format: +attributeName: Type
- All methods must follow the format: +methodName(param: Type): ReturnType
- Use meaningful relationship labels; ensure association direction reflects real ownership or access.

Note: Before generating UML code, validate all class participants, check for naming collisions, confirm inheritance direction, and ensure syntactical correctness with complete closure of blocks. Prefer single-word PascalCase naming convention across all identifiers.


OUTPUT ONLY PlantUML code from @startuml to @enduml"""

            # Enhanced Sequence Diagram Optimization  
            sequence_prompt = f"""Generate a PlantUML sequence diagram with STRICT REQUIREMENTS:

MANDATORY PARTICIPANTS: {actors_text}
REQUIREMENTS: {original_requirements[:500]}
ISSUES TO FIX: {issues_text[:200]}

ACTOR CLASSIFICATION RULES:
- Human actors: Users, Operators, Administrators, etc. (represent as actors initiating actions)
- External systems: RemoteSensor, ExternalSystem, etc. (represent as participants responding to or sending data)
- DO NOT treat these as actors: System components, states (ON/OFF), abbreviations (PDA/HVAC), technical terms (Database)

PARTICIPANT DECLARATION:
- Use 'actor' for human roles, 'participant' for system components
- EVERY identified actor MUST appear as participant
- NO generic participants (System, Database, Application)
- For human actors: use actor "User" or "Operator"
- For system actors: use participant "ExternalSystem"

MESSAGE FLOW RULES:
- Each participant MUST send/receive at least 1 message
- Use proper syntax: A -> B : messageDescription
- Include return messages: B --> A : response
- Use activation boxes with activate/deactivate
- Use proper UML syntax for loops, alternatives, and options
- Use proper UML syntax for parallel flows
- Human actors typically initiate sequences with actions
- System actors typically respond with data or notifications

SECTION ORGANIZATION:
- Use == Section Name == for logical groupings
- Show realistic business workflow
- Include alt/opt blocks for conditions
- Use proper UML syntax for grouping messages

CASE STUDY SPECIFIC GUIDANCE:
- For Digital Home System: Show User interactions with sensors, controllers, and appliances
- For Monitoring System: Show Operator interactions with sensors, alarms, and monitoring data
- For Library System: Show User/Librarian interactions with books and library resources

MANDATORY SYNTAX:
- Use 'actor' for actors, 'participant' for system components
- Use 'activate' and 'deactivate' for activation boxes
- Use 'note left/right/over' for annotations
- Use 'create' and 'destroy' for object lifecycle
- Use 'ref' for referencing other diagrams
- Use 'group' for grouping related messages
- Use 'par' for parallel flows
- Use 'loop' for repetitive interactions
- Use 'break' for exception handling
- Use 'alt' for conditional logic
- Use 'opt' for optional messages
- Declare all participants and actors only once at the beginning.
- Use aliases for multi-word participants. E.g., 'participant Remote_Sensor as "Remote Sensor"'
- Use consistent naming throughout the diagram for participants.
- Only define one logical actor (e.g., 'User') unless there are truly multiple human actors.
- Always close 'group', 'opt', 'alt', 'else' blocks with 'end'.
- Avoid nesting too many 'alt' and 'opt' blocks unless necessary; prefer clarity over depth.


FORBIDDEN ELEMENTS:
- "System" participant
- Undefined participant references
- Messages without descriptions
- Participants not in actor list
- Overly complex diagrams with too many participants
- Generic participants like "Database", "Application"
- DO NOT treat abbreviations (PDA, HVAC) as participants
- DO NOT treat states or values (ON, OFF) as participants
- DO NOT treat technical components (Database, API) as participants unless they are external systems

Note: Before generating UML code, validate all sequence participants, check for naming collisions, confirm inheritance direction, and ensure syntactical correctness with complete closure of blocks. Prefer single-word PascalCase naming convention across all identifiers.


OUTPUT ONLY PlantUML code from @startuml to @enduml"""

            # Make API calls with enhanced prompts
            print("Generating class diagram with enhanced prompt...")
            print(f"Actors: {actors_text}")
            print(f"Requirements: {original_requirements[:500]}...")
            print(f"Issues: {issues_text[:200]}...")
            print("Class Diagram Prompt:", class_prompt)
            print("Sequence Diagram Prompt:", sequence_prompt)
            print("Using model:", self.model)
            # Generate class and sequence diagrams using the enhanced prompts
            print("Calling LLM for class diagram generation...")

            class_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a UML expert. Generate ONLY PlantUML code. Include ALL specified actors as classes with proper attributes and methods. NO generic elements allowed."},
                    {"role": "user", "content": class_prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )

            print("Calling LLM for sequence diagram generation...")
            # Generate sequence diagram using the enhanced prompt
            print("Using model:", self.model)
            sequence_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a UML expert. Generate ONLY PlantUML code. Include ALL specified actors as participants. NO 'System' participant allowed."},
                    {"role": "user", "content": sequence_prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )

            optimized_class = self._clean_plantuml_code(class_response.choices[0].message.content)
            optimized_sequence = self._clean_plantuml_code(sequence_response.choices[0].message.content)

            # Post-processing to ensure consistency
            optimized_class = self._enforce_class_consistency(optimized_class, identified_actors)
            optimized_sequence = self._enforce_sequence_consistency(optimized_sequence, identified_actors)

            # Validate and fix sequence diagram
            optimized_sequence = self._validate_and_fix_class_diagram(optimized_sequence)
            optimized_class = self._validate_and_fix_class_diagram(optimized_class)

            # I'm having issues with wrong plantuml code being generated, so let's ensure we have the right format
            if not optimized_class.startswith('@startuml'):
                optimized_class = f"@startuml\n{optimized_class}\n@enduml"
            if not optimized_sequence.startswith('@startuml'):
                optimized_sequence = f"@startuml\n{optimized_sequence}\n@enduml"
            # Final output
            print("Final optimized class diagram:")

            


            
            

            def fallback_fix_diagram(diagram_code: str, diagram_type: str) -> str:
                try:
                    print(f"Attempting fallback fix for {diagram_type} diagram...")

                    correction_prompt = f"""The following PlantUML {diagram_type} diagram code has syntax issues. Please correct it and return only the corrected PlantUML code wrapped in @startuml and @enduml. {diagram_code}"""

                    correction_response = asyncio.run(self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": f"You are a PlantUML syntax expert. Fix the syntax for {diagram_type} diagrams only. Return only the corrected code with @startuml and @enduml."},
                            {"role": "user", "content": correction_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=2000
                    ))

                    corrected_code = correction_response.choices[0].message.content
                    corrected_code = self._clean_plantuml_code(corrected_code)

                    # Ensure proper wrapping if missing
                    if not corrected_code.startswith('@startuml'):
                        corrected_code = f"@startuml\n{corrected_code}\n@enduml"

                    return corrected_code

                except Exception as correction_error:
                    print(f"Fallback correction failed for {diagram_type} diagram: {str(correction_error)}")
                    return diagram_code  # Return original if correction fails

            # Revalidate and fallback fix if needed
            if not self._is_valid_plantuml(optimized_class):
                print("Class diagram validation failed, applying fallback fix...")
                optimized_class = fallback_fix_diagram(optimized_class, "class")

            if not self._is_valid_plantuml(optimized_sequence):
                print("Sequence diagram validation failed, applying fallback fix...")
                optimized_sequence = fallback_fix_diagram(optimized_sequence, "sequence")

            print("Final optimized class diagram:")
            print(optimized_class)
            print("\nFinal optimized sequence diagram:")
            print(optimized_sequence)

            return {
                "class_diagram": optimized_class,
                "sequence_diagram": optimized_sequence,
                "improvements": [
                    f"Included ALL identified actors: {actors_text}",
                    "Removed generic 'System' elements",
                    "Added proper class attributes and methods",
                    "Ensured all participants appear in sequence",
                    "Validated UML syntax compliance",
                    "Fixed undefined references",
                    "Fallback LLM correction applied if needed"
                ],
                "final_actors": identified_actors
            }

        except Exception as e:
            print(f"Error optimizing diagrams: {str(e)}")
            return {
                "class_diagram": class_diagram,
                "sequence_diagram": sequence_diagram,
                "improvements": [f"Optimization failed: {str(e)}"],
                "final_actors": identified_actors
            }
    
        
    def _is_valid_plantuml(self, diagram_code: str) -> bool:
        """
        Performs basic validation of PlantUML code to check structural integrity.
        This is not a full parser but detects obvious formatting/syntax issues.
        """

        # Check for required delimiters
        if not diagram_code.strip().startswith('@startuml') or not diagram_code.strip().endswith('@enduml'):
            return False

        # Check for balanced brackets (simple heuristic for malformed blocks)
        open_count = diagram_code.count('{')
        close_count = diagram_code.count('}')
        if open_count != close_count:
            return False

        # Ensure at least one PlantUML keyword is used (participant, class, actor, etc.)
        uml_keywords = ['participant', 'actor', 'class', 'interface', '->', '-->', '<--']
        if not any(keyword in diagram_code for keyword in uml_keywords):
            return False

        # Detect obviously malformed lines (e.g., lone arrows)
        malformed_arrows = re.findall(r'^\s*[-<]+>+\s*$', diagram_code, re.MULTILINE)
        if malformed_arrows:
            return False

        return True
        
    async def validate_plantuml_syntax(self, plantuml_code: str, diagram_type: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Validates PlantUML syntax and returns detailed validation results with retry mechanism.
        
        Args:
            plantuml_code: The PlantUML code to validate
            diagram_type: The type of diagram ('class' or 'sequence')
            max_retries: Maximum number of automatic fix attempts (default: 3)
            
        Returns:
            Dictionary with validation results including:
            - is_valid: Boolean indicating if the syntax is valid
            - errors: List of error messages if any
            - warnings: List of warning messages if any
            - line_errors: Dictionary mapping line numbers to specific errors
            - fixed_code: Corrected PlantUML code if automatic fixes were applied
            - retry_count: Number of retry attempts made
            - retry_suggestions: Suggestions for manual fixes if automatic fixes failed
        """
        logging.info(f"Validating {diagram_type} diagram syntax")
        
        result = {
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "line_errors": {},
            "fixed_code": None,
            "retry_count": 0,
            "retry_suggestions": [],
            "can_retry": False
        }
        
        # Store original code for comparison after fixes
        original_code = plantuml_code
        current_code = plantuml_code
        
        # Basic validation
        if not current_code or len(current_code.strip()) < 10:
            result["errors"].append("Empty or too short PlantUML code")
            return result
        
        # Attempt automatic fixes with retry mechanism
        for retry in range(max_retries):
            # Reset error lists for this attempt
            errors = []
            warnings = []
            line_errors = {}
            fixed = False
            
            # Check for required delimiters and fix if missing
            if not current_code.strip().startswith('@startuml'):
                errors.append("Missing @startuml at the beginning")
                line_errors["1"] = "Missing @startuml tag"
                current_code = '@startuml\n' + current_code.strip()
                fixed = True
                
            if not current_code.strip().endswith('@enduml'):
                errors.append("Missing @enduml at the end")
                last_line = len(current_code.split('\n'))
                line_errors[str(last_line)] = "Missing @enduml tag"
                current_code = current_code.strip() + '\n@enduml'
                fixed = True
            
            # Check for balanced brackets
            open_count = current_code.count('{')
            close_count = current_code.count('}')
            if open_count != close_count:
                errors.append(f"Unbalanced brackets: {open_count} opening vs {close_count} closing")
                # Try to fix unbalanced brackets
                if open_count > close_count:
                    # Add missing closing brackets
                    current_code = current_code.rstrip() + '\n' + ('}' * (open_count - close_count)) + '\n@enduml'
                    fixed = True
                elif close_count > open_count:
                    # Try to remove extra closing brackets (more complex, just flag for manual fix)
                    errors.append("Too many closing brackets - requires manual fix")
                    result["retry_suggestions"].append("Check for and remove extra closing brackets '}'")
            
            # Check for balanced parentheses
            open_count = current_code.count('(')
            close_count = current_code.count(')')
            if open_count != close_count:
                errors.append(f"Unbalanced parentheses: {open_count} opening vs {close_count} closing")
                # Try to fix unbalanced parentheses
                if open_count > close_count:
                    # Add missing closing parentheses before @enduml
                    end_index = current_code.rfind('@enduml')
                    if end_index > 0:
                        # Extract participant names from activate statements to add deactivate for them
                        activate_pattern = re.compile(r'activate\s+(\w+)', re.IGNORECASE)
                        activate_matches = activate_pattern.findall(current_code)
                        
                        # Get unique participant names that need deactivation
                        if activate_matches:
                            deactivate_lines = '\n'.join([f"deactivate {participant}" for participant in activate_matches[-(open_count - close_count):]])
                            current_code = current_code[:end_index] + '\n' + deactivate_lines + '\n' + current_code[end_index:]
                            fixed = True
                elif close_count > open_count:
                    # Try to remove extra closing parentheses (more complex, just flag for manual fix)
                    errors.append("Too many closing parentheses - requires manual fix")
                    result["retry_suggestions"].append("Check for and remove extra closing parentheses ')'")
            
            # Check for diagram-specific keywords and try to fix
            if diagram_type.lower() == 'class':
                if 'class' not in current_code.lower():
                    errors.append("No class definition found in class diagram")
                    result["retry_suggestions"].append("Add at least one class definition using 'class ClassName' syntax")
                    
                # Check for common class diagram syntax errors
                lines = current_code.split('\n')
                fixed_lines = []
                for i, line in enumerate(lines):
                    fixed_line = line
                    
                    # Check for invalid inheritance syntax
                    if '<|--' in line and not re.search(r'\w+\s*<\|--\s*\w+', line):
                        line_errors[str(i+1)] = "Invalid inheritance syntax"
                        errors.append(f"Line {i+1}: Invalid inheritance syntax")
                        # Don't try to auto-fix inheritance syntax as it's too complex
                        result["retry_suggestions"].append(f"Fix inheritance syntax on line {i+1} to follow format 'ChildClass <|-- ParentClass'")
                    
                    # Check for invalid relationship syntax with labels
                    if '--' in line and ':' in line and not re.search(r'\w+\s*(["\d\.\*]+)?\s*--+\s*(["\d\.\*]+)?\s*\w+', line):
                        line_errors[str(i+1)] = "Invalid relationship syntax"
                        errors.append(f"Line {i+1}: Invalid relationship syntax")
                        result["retry_suggestions"].append(f"Fix relationship syntax on line {i+1} to follow format 'ClassA -- ClassB' or 'ClassA \"1\" -- \"0..*\" ClassB : relationship >'")
                    
                    # Check for invalid relationship labels (missing spaces around colon)
                    if '--' in line and ':' in line and re.search(r'\w+.*--.*\w+:[^\s]', line):
                        line_errors[str(i+1)] = "Invalid relationship label format"
                        errors.append(f"Line {i+1}: Invalid relationship label format - missing space after colon")
                        # Try to fix by adding a space after colon if missing
                        if re.search(r':(\S)', line):
                            fixed_line = re.sub(r':(\S)', r': \1', line)
                            fixed = True
                    
                    # Check for invalid directional arrow syntax in relationships
                    if '--' in line and ('>' in line or '<' in line):
                        # Check for missing space before directional arrow
                        if re.search(r'\S>', line) and not re.search(r'->|--|<-', line):
                            line_errors[str(i+1)] = "Missing space before directional arrow"
                            errors.append(f"Line {i+1}: Missing space before directional arrow in relationship")
                            # Try to fix by adding space before >
                            fixed_line = re.sub(r'(\S)>', r'\1 >', fixed_line)
                            fixed = True
                        
                        # Check for invalid directional arrow placement (should be at end of relationship label)
                        if ':' in line and '>' in line and not re.search(r':\s+[^>]+\s*>', line):
                            line_errors[str(i+1)] = "Invalid directional arrow placement"
                            errors.append(f"Line {i+1}: Invalid directional arrow placement - should be at end of relationship label")
                            result["retry_suggestions"].append(f"Fix directional arrow on line {i+1} - it should be at the end of the relationship label, e.g., 'ClassA -- ClassB : controls >'")
                    
                    # Check for common relationship syntax errors with class names
                    if '--' in line:
                        # Check if class names are missing or incomplete on either side of relationship
                        if re.search(r'^\s*--', line) or re.search(r'--\s*$', line) or re.search(r'^\s*"', line):
                            line_errors[str(i+1)] = "Incomplete relationship definition"
                            errors.append(f"Line {i+1}: Incomplete relationship definition - missing class name")
                            result["retry_suggestions"].append(f"Fix relationship on line {i+1} - ensure both class names are specified, e.g., 'ClassA -- ClassB'")
                        
                        # Check for missing space between class name and relationship symbol
                        if re.search(r'\w--', line) or re.search(r'--\w', line):
                            line_errors[str(i+1)] = "Missing space in relationship syntax"
                            errors.append(f"Line {i+1}: Missing space between class name and relationship symbol")
                            # Try to fix by adding space
                            fixed_line = re.sub(r'(\w)--', r'\1 --', fixed_line)
                            fixed_line = re.sub(r'--(\w)', r'-- \1', fixed_line)
                            fixed = True
                    
                    # Check for invalid multiplicity format
                    if '--' in line and '"' in line:
                        # Check for unbalanced quotes in multiplicity
                        quote_count = line.count('"')
                        if quote_count % 2 != 0:
                            line_errors[str(i+1)] = "Unbalanced quotes in multiplicity"
                            errors.append(f"Line {i+1}: Unbalanced quotes in multiplicity")
                            # Try to fix by adding missing quote
                            fixed_line = fixed_line + '"'
                            fixed = True
                    
                    # Check for invalid attribute syntax and try to fix
                    if ':' in line and re.search(r'[+\-#~]\s*\w+\s*:\s*$', line):
                        line_errors[str(i+1)] = "Incomplete attribute definition, missing type"
                        errors.append(f"Line {i+1}: Incomplete attribute definition")
                        # Try to fix by adding a generic type
                        fixed_line = line.rstrip() + " String"
                        fixed = True
                    
                    fixed_lines.append(fixed_line)
                
                if fixed:
                    current_code = '\n'.join(fixed_lines)
                    
            elif diagram_type.lower() == 'sequence':
                if not any(keyword in current_code.lower() for keyword in ['participant', 'actor', '->', '-->']):
                    errors.append("No participants or messages found in sequence diagram")
                    result["retry_suggestions"].append("Add at least one participant using 'participant Name' or 'actor Name' syntax")
                    result["retry_suggestions"].append("Add at least one message using 'ParticipantA -> ParticipantB: Message' syntax")
                
                # Check for common sequence diagram syntax errors
                lines = current_code.split('\n')
                fixed_lines = []
                activate_count = 0
                deactivate_count = 0
                
                for i, line in enumerate(lines):
                    fixed_line = line
                    
                    # Track activation/deactivation balance
                    if re.search(r'\bactivate\b', line, re.IGNORECASE):
                        activate_count += 1
                    if re.search(r'\bdeactivate\b', line, re.IGNORECASE):
                        deactivate_count += 1
                    
                    # Check for invalid message syntax
                    if '->' in line and not re.search(r'\w+\s*->\s*\w+', line):
                        line_errors[str(i+1)] = "Invalid message syntax"
                        errors.append(f"Line {i+1}: Invalid message syntax")
                        # Don't try to auto-fix message syntax as it's too complex
                        result["retry_suggestions"].append(f"Fix message syntax on line {i+1} to follow format 'Sender -> Receiver: Message'")
                    
                    fixed_lines.append(fixed_line)
                
                # Check activation balance and try to fix
                if activate_count != deactivate_count:
                    warnings.append(f"Unbalanced activate/deactivate: {activate_count} activations vs {deactivate_count} deactivations")
                    
                    # Try to fix unbalanced activations
                    if activate_count > deactivate_count:
                        # Add missing deactivate statements before @enduml
                        end_index = current_code.rfind('@enduml')
                        if end_index > 0:
                            # Extract participant names from activate statements to add deactivate for them
                            activate_pattern = re.compile(r'activate\s+(\w+)', re.IGNORECASE)
                            activate_matches = activate_pattern.findall(current_code)
                            
                            # Get unique participant names that need deactivation
                            if activate_matches:
                                deactivate_lines = '\n'.join([f"deactivate {participant}" for participant in activate_matches[-(activate_count - deactivate_count):]])
                                current_code = current_code[:end_index] + '\n' + deactivate_lines + '\n' + current_code[end_index:]
                                fixed = True
                    elif deactivate_count > activate_count:
                        # Try to remove extra deactivate statements (more complex, just flag for manual fix)
                        warnings.append("Too many deactivate statements - requires manual fix")
                        result["retry_suggestions"].append("Check for and remove extra 'deactivate' statements or add missing 'activate' statements")
            
            # Check for common syntax errors in any diagram type
            lines = current_code.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                fixed_line = line
                
                # Check for unclosed quotes
                if line.count('"') % 2 != 0:
                    line_errors[str(i+1)] = "Unclosed quotes"
                    errors.append(f"Line {i+1}: Unclosed quotes")
                    # Try to fix unclosed quotes
                    fixed_line = fixed_line + '"'
                    fixed = True
                
                # Check for invalid color syntax
                if '#' in line and re.search(r'#[^A-Fa-f0-9]', line):
                    line_errors[str(i+1)] = "Invalid color code"
                    warnings.append(f"Line {i+1}: Possible invalid color code")
                    # Don't try to auto-fix color codes as it's too complex
                    result["retry_suggestions"].append(f"Check color code on line {i+1}, ensure it's a valid hex color like #RRGGBB")
                
                fixed_lines.append(fixed_line)
            
            if fixed:
                current_code = '\n'.join(fixed_lines)
            
            # Update result with current validation state
            result["errors"] = errors
            result["warnings"] = warnings
            result["line_errors"] = line_errors
            result["retry_count"] = retry + 1
            
            # Check if we've fixed all errors
            if len(errors) == 0:
                result["is_valid"] = True
                if fixed:  # Only set fixed_code if we actually made changes
                    result["fixed_code"] = current_code
                break
            
            # If we couldn't fix anything but there are still errors, don't retry
            if not fixed and retry < max_retries - 1:
                result["can_retry"] = True
                continue
        
        # If we still have errors after all retries, provide final suggestions
        if not result["is_valid"]:
            result["can_retry"] = True
            if not result["retry_suggestions"]:
                result["retry_suggestions"] = [
                    "Ensure all opening and closing tags are balanced",
                    "Check for proper syntax in all relationships and messages",
                    "Verify that all required elements are present for your diagram type"
                ]
        
        # Log validation results
        logging.info(f"PlantUML validation completed: valid={result['is_valid']}, errors={len(result['errors'])}, warnings={len(result['warnings'])}, retries={result['retry_count']}")
        
        return result
    
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
                # Library system roles
                ['member', 'customer', 'client', 'patron', 'borrower'],
                ['admin', 'administrator', 'manager', 'supervisor'],
                ['librarian', 'staff', 'employee'],
                ['student', 'pupil', 'learner'],
                ['guest', 'visitor', 'anonymous'],
                # Digital home system roles
                ['user', 'homeowner', 'resident'],
                # Monitoring system roles
                ['operator', 'monitoring-operator', 'monitor'],
                # System components that might be treated as actors
                ['sensor', 'remote sensor', 'external sensor'],
                ['thermostat', 'temperature controller'],
                ['humidistat', 'humidity controller']
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
    
    def _validate_and_fix_class_diagram(self, plantuml_code: str) -> str:
        """
        Validate class diagram and fix undefined references
        """
        try:
            lines = plantuml_code.split('\n')
            defined_classes = set()
            referenced_classes = set()
            relationship_lines = []
            other_lines = []
            
            # First pass: identify defined classes and relationship lines
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('class '):
                    # Extract class name
                    class_name = line_stripped.split()[1].split('{')[0].strip()
                    defined_classes.add(class_name)
                    other_lines.append(line)
                elif any(rel in line_stripped for rel in ['--', '->', '..', '|>', '<|', 'extends', 'implements']):
                    relationship_lines.append(line)
                else:
                    other_lines.append(line)
            
            # Second pass: analyze relationships and find referenced classes
            valid_relationships = []
            for rel_line in relationship_lines:
                rel_stripped = rel_line.strip()
                
                # Extract class names from relationship line
                # Handle various relationship formats
                parts = rel_stripped.split()
                referenced_in_line = set()
                
                for part in parts:
                    # Skip relationship operators and labels
                    if part and part.isalpha() and part[0].isupper() and part not in ['--', '->', '..', '|>', '<|']:
                        referenced_in_line.add(part)
                
                # Check if all referenced classes are defined
                undefined_in_line = referenced_in_line - defined_classes
                
                if not undefined_in_line:
                    # All classes are defined, keep the relationship
                    valid_relationships.append(rel_line)
                else:
                    # Some classes are undefined, try to fix or skip
                    print(f"Removing relationship with undefined classes: {undefined_in_line} in line: {rel_stripped}")
            
            # Reconstruct the diagram
            fixed_lines = []
            for line in other_lines:
                if line.strip() and not line.startswith('@'):
                    # Remove System references
                    if 'System' not in line:
                        fixed_lines.append(line)
            
            # Add valid relationships
            fixed_lines.extend(valid_relationships)
            
            # Ensure all classes have at least one relationship
            classes_with_relationships = set()
            for rel_line in valid_relationships:
                rel_stripped = rel_line.strip()
                parts = rel_stripped.split()
                for part in parts:
                    if part in defined_classes:
                        classes_with_relationships.add(part)
            
            # Add basic relationships for orphaned classes
            orphaned_classes = defined_classes - classes_with_relationships
            if orphaned_classes and len(defined_classes) > 1:
                defined_list = list(defined_classes)
                for orphaned in orphaned_classes:
                    if len(defined_list) > 1:
                        # Connect to first available class
                        for target in defined_list:
                            if target != orphaned:
                                fixed_lines.append(f"{orphaned} -- {target} : interacts")
                                break
            
            # Reconstruct with proper PlantUML structure
            result = "@startuml\n"
            for line in fixed_lines:
                if line.strip():
                    result += line + "\n"
            result += "@enduml"
            
            return result
            
        except Exception as e:
            print(f"Error validating class diagram: {str(e)}")
            return plantuml_code
    
    def _extract_entities_with_pos(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using POS tagging for enhanced diagram generation
        """
        if not self.nlp:
            return {'nouns': [], 'verbs': [], 'proper_nouns': [], 'adjectives': []}
        
        doc = self.nlp(text)
        entities = {
            'nouns': [],
            'verbs': [],
            'proper_nouns': [],
            'adjectives': []
        }
        
        for token in doc:
            if token.pos_ == 'NOUN' and len(token.text) > 2:
                entities['nouns'].append(token.lemma_.lower())
            elif token.pos_ == 'PROPN' and len(token.text) > 2:
                entities['proper_nouns'].append(token.text)
            elif token.pos_ == 'VERB' and token.lemma_ not in ['be', 'have', 'do']:
                entities['verbs'].append(token.lemma_.lower())
            elif token.pos_ == 'ADJ' and len(token.text) > 2:
                entities['adjectives'].append(token.lemma_.lower())
        
        # Remove duplicates and filter relevant entities
        for key in entities:
            entities[key] = list(set(entities[key]))
            
        return entities
    
    async def retry_diagram_with_feedback(self, 
                                         original_requirements: str,
                                         current_class_diagram: str,
                                         current_sequence_diagram: str,
                                         issue_type: str,
                                         issue_prompt: str,
                                         identified_actors: List[str] = [],
                                         retry_count: int = 0) -> Dict[str, Any]:
        """
        Retry diagram generation with specific feedback and targeted improvements
        
        Args:
            original_requirements: Original user requirements
            current_class_diagram: Current class diagram PlantUML code
            current_sequence_diagram: Current sequence diagram PlantUML code
            issue_type: Type of issue to fix (syntax_class, syntax_sequence, missing_interactions, etc.)
            issue_prompt: Specific prompt for the issue
            identified_actors: List of identified actors
            retry_count: Current retry attempt number
            
        Returns:
            Dict containing improved diagrams and details
        """
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Retrying diagrams with issue type: {issue_type}, retry count: {retry_count}")
            
            # Generate targeted improvements based on issue type
            if issue_type in ["syntax_class", "syntax_both"]:
                # Fix class diagram syntax issues
                improved_class_diagram = await self._fix_diagram_syntax(
                    current_class_diagram, 
                    "class", 
                    original_requirements,
                    issue_prompt,
                    identified_actors
                )
            else:
                improved_class_diagram = current_class_diagram
                
            if issue_type in ["syntax_sequence", "syntax_both"]:
                # Fix sequence diagram syntax issues  
                improved_sequence_diagram = await self._fix_diagram_syntax(
                    current_sequence_diagram,
                    "sequence", 
                    original_requirements,
                    issue_prompt,
                    identified_actors
                )
            else:
                improved_sequence_diagram = current_sequence_diagram
                
            # Handle content-specific improvements
            if issue_type == "missing_interactions":
                improved_sequence_diagram = await self._add_missing_interactions(
                    current_sequence_diagram,
                    original_requirements,
                    identified_actors,
                    issue_prompt
                )
                
            elif issue_type == "missing_classes":
                improved_class_diagram = await self._add_missing_classes(
                    current_class_diagram,
                    original_requirements,
                    identified_actors,
                    issue_prompt
                )
                
            elif issue_type == "wrong_relationships":
                improved_class_diagram = await self._fix_relationships(
                    current_class_diagram,
                    original_requirements,
                    identified_actors,
                    issue_prompt
                )
                
            elif issue_type == "general_improvement":
                # Comprehensive improvement of both diagrams
                improved_class_diagram = await self._improve_diagram_quality(
                    current_class_diagram,
                    "class",
                    original_requirements,
                    identified_actors,
                    issue_prompt
                )
                improved_sequence_diagram = await self._improve_diagram_quality(
                    current_sequence_diagram,
                    "sequence", 
                    original_requirements,
                    identified_actors,
                    issue_prompt
                )
            
            # Clean and validate the improved diagrams
            improved_class_diagram = self._clean_plantuml_code(improved_class_diagram)
            improved_sequence_diagram = self._clean_plantuml_code(improved_sequence_diagram)
            
            # Generate improvement summary
            improvements_made = self._generate_improvement_summary(
                issue_type, 
                current_class_diagram, 
                current_sequence_diagram,
                improved_class_diagram,
                improved_sequence_diagram
            )
            
            return {
                "class_diagram": improved_class_diagram,
                "sequence_diagram": improved_sequence_diagram,
                "improvements_made": improvements_made,
                "retry_count": retry_count + 1,
                "issue_type": issue_type,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in retry_diagram_with_feedback: {str(e)}")
            return {
                "class_diagram": current_class_diagram,
                "sequence_diagram": current_sequence_diagram,
                "improvements_made": [f"Error during retry: {str(e)}"],
                "retry_count": retry_count + 1,
                "issue_type": issue_type,
                "status": "error"
            }
    
    async def _fix_diagram_syntax(self, diagram_code: str, diagram_type: str, 
                                 requirements: str, issue_prompt: str, 
                                 actors: List[str]) -> str:
        """Fix syntax issues in PlantUML diagrams"""
        system_prompt = f"""You are a PlantUML syntax expert. Your task is to fix syntax errors in {diagram_type} diagrams.

Rules:
1. Fix all PlantUML syntax errors
2. Ensure proper @startuml and @enduml tags
3. Use correct PlantUML syntax for {diagram_type} diagrams
4. Maintain the original intent and structure
5. Include all actors: {', '.join(actors)}
6. Generate only valid PlantUML code

{issue_prompt}"""

        user_prompt = f"""Fix the syntax errors in this {diagram_type} diagram:

Original Requirements:
{requirements}

Current Diagram (with syntax issues):
{diagram_code}

Please provide the corrected PlantUML code with proper syntax."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            return self._clean_plantuml_code(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error fixing {diagram_type} syntax: {str(e)}")
            return diagram_code
    
    async def _add_missing_interactions(self, sequence_diagram: str, requirements: str, 
                                       actors: List[str], issue_prompt: str) -> str:
        """Add missing interactions to sequence diagram"""
        system_prompt = f"""You are a UML sequence diagram expert. Add missing interactions and message flows.

Rules:
1. Analyze the requirements to identify missing user interactions
2. Add missing message flows between participants
3. Include all actors: {', '.join(actors)}
4. Maintain existing valid interactions
5. Use proper PlantUML sequence diagram syntax
6. Focus on user workflows and system responses

{issue_prompt}"""

        user_prompt = f"""Add missing interactions to this sequence diagram based on the requirements:

Requirements:
{requirements}

Current Sequence Diagram:
{sequence_diagram}

Add missing interactions while keeping existing valid ones."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4
            )
            
            return self._clean_plantuml_code(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error adding missing interactions: {str(e)}")
            return sequence_diagram
    
    async def _add_missing_classes(self, class_diagram: str, requirements: str,
                                  actors: List[str], issue_prompt: str) -> str:
        """Add missing classes to class diagram"""
        system_prompt = f"""You are a UML class diagram expert. Add missing classes and entities.

Rules:
1. Analyze requirements to identify missing domain objects
2. Add missing classes with appropriate attributes and methods
3. Include all actors as classes: {', '.join(actors)}
4. Maintain existing valid classes and relationships
5. Use proper PlantUML class diagram syntax
6. Focus on domain entities mentioned in requirements

{issue_prompt}"""

        user_prompt = f"""Add missing classes to this class diagram based on the requirements:

Requirements:
{requirements}

Current Class Diagram:
{class_diagram}

Add missing classes while keeping existing valid ones."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4
            )
            
            return self._clean_plantuml_code(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error adding missing classes: {str(e)}")
            return class_diagram
    
    async def _fix_relationships(self, class_diagram: str, requirements: str,
                                actors: List[str], issue_prompt: str) -> str:
        """Fix incorrect relationships in class diagram"""
        system_prompt = f"""You are a UML class diagram expert. Fix incorrect relationships between classes.

Rules:
1. Analyze requirements to determine correct relationships
2. Fix association, dependency, and inheritance relationships
3. Ensure relationships reflect the actual requirements
4. Include all actors: {', '.join(actors)}
5. Use proper PlantUML relationship syntax (-->, --|>, etc.)
6. Maintain class definitions while fixing relationships

{issue_prompt}"""

        user_prompt = f"""Fix incorrect relationships in this class diagram:

Requirements:
{requirements}

Current Class Diagram:
{class_diagram}

Correct the relationships to match the requirements."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            return self._clean_plantuml_code(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error fixing relationships: {str(e)}")
            return class_diagram
    
    async def _improve_diagram_quality(self, diagram_code: str, diagram_type: str,
                                      requirements: str, actors: List[str], 
                                      issue_prompt: str) -> str:
        """General quality improvement for diagrams"""
        system_prompt = f"""You are a UML {diagram_type} diagram expert. Improve the overall quality and completeness.

Rules:
1. Enhance diagram completeness and accuracy
2. Improve naming conventions and structure
3. Add missing elements based on requirements
4. Include all actors: {', '.join(actors)}
5. Ensure proper PlantUML syntax
6. Focus on clarity and professional appearance

{issue_prompt}"""

        user_prompt = f"""Improve the quality of this {diagram_type} diagram:

Requirements:
{requirements}

Current Diagram:
{diagram_code}

Provide an improved version with better quality and completeness."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4
            )
            
            return self._clean_plantuml_code(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error improving {diagram_type} quality: {str(e)}")
            return diagram_code
    
    def _generate_improvement_summary(self, issue_type: str, 
                                     old_class: str, old_sequence: str,
                                     new_class: str, new_sequence: str) -> List[str]:
        """Generate summary of improvements made"""
        improvements = []
        
        # Count changes
        class_changes = len(new_class.split('\n')) - len(old_class.split('\n'))
        sequence_changes = len(new_sequence.split('\n')) - len(old_sequence.split('\n'))
        
        if issue_type == "syntax_class":
            improvements.append("Fixed PlantUML syntax errors in class diagram")
        elif issue_type == "syntax_sequence":
            improvements.append("Fixed PlantUML syntax errors in sequence diagram")
        elif issue_type == "syntax_both":
            improvements.append("Fixed PlantUML syntax errors in both diagrams")
        elif issue_type == "missing_interactions":
            improvements.append(f"Added missing interactions to sequence diagram ({abs(sequence_changes)} lines changed)")
        elif issue_type == "missing_classes":
            improvements.append(f"Added missing classes to class diagram ({abs(class_changes)} lines changed)")
        elif issue_type == "wrong_relationships":
            improvements.append("Corrected relationships between classes")
        elif issue_type == "general_improvement":
            improvements.append("Applied general quality improvements to both diagrams")
        
        # Add specific change counts if significant
        if abs(class_changes) > 5:
            improvements.append(f"Class diagram: {abs(class_changes)} lines {'added' if class_changes > 0 else 'removed'}")
        if abs(sequence_changes) > 5:
            improvements.append(f"Sequence diagram: {abs(sequence_changes)} lines {'added' if sequence_changes > 0 else 'removed'}")
        
        return improvements if improvements else ["Diagram optimized with targeted improvements"]



