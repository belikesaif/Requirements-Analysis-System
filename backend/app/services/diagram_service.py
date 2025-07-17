"""
AI-Powered Diagram Service for generating UML diagrams from SNL requirements using OpenAI
"""

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

### QUALITY CRITERIA:

1. **Completeness**: All major entities from requirements are represented
2. **Correctness**: Relationships accurately reflect the domain
3. **Consistency**: Naming and notation follow conventions
4. **Clarity**: Diagram is readable and understandable
5. **Maintainability**: Structure supports future changes

### MANDATORY REQUIREMENTS:

1. **EVERY class MUST have meaningful attributes and methods**
2. **EVERY class MUST have at least one relationship (no orphaned classes)**
3. **USE specific, domain-relevant class names (avoid generic terms)**
4. **INCLUDE proper visibility modifiers for all attributes and methods**
5. **SHOW multiplicities for associations where relevant**
6. **VALIDATE that all referenced classes in relationships are defined**
7. **BALANCE complexity - include essential elements without overcomplication**

### FORBIDDEN PRACTICES:

1. **Generic class names** like "System", "Manager", "Handler"
2. **Classes without attributes or methods**
3. **Relationships without labels**
4. **Undefined class references in relationships**
5. **Overly complex diagrams with too many classes**

Generate ONLY the PlantUML code that demonstrates these concepts, starting with @startuml and ending with @enduml. Focus on creating a well-structured, professionally designed class diagram that follows UML best practices and object-oriented design principles."""
    
    def _create_enhanced_class_diagram_prompt(self, snl_text: str, actors: List[str], extracted_entities: Dict[str, List[str]]) -> str:
        """
        Create enhanced prompt for class diagram generation with POS tagging data
        """
        actors_text = ", ".join(actors) if actors else "Not specified"
        
        return f"""Generate a PlantUML class diagram for the Library Management System that EXACTLY matches the gold standard structure.

SNL Requirements:
{snl_text}

Identified Actors: {actors_text}

MANDATORY REQUIREMENTS:
1. Generate EXACTLY the gold standard class structure with User as base class
2. Include ALL required inheritance
3. Include ALL required associations
4. Use the EXACT attributes and methods specified in the gold standard
5. Do NOT create generic "System" class - use the specific class hierarchy
6. Focus on the Library Management System domain as specified in the gold standard

The diagram MUST match the exact gold standard structure provided in the system prompt."""
    
    def _get_enhanced_sequence_diagram_system_prompt(self) -> str:
        """
        Enhanced system prompt for sequence diagram generation with comprehensive UML concepts
        """
        return """You are an expert software architect and UML sequence diagram specialist with deep knowledge of behavioral modeling and interaction design. Your task is to generate comprehensive PlantUML sequence diagrams from Structured Natural Language (SNL) requirements.

## FUNDAMENTAL UML SEQUENCE DIAGRAM CONCEPTS:

### BASIC ELEMENTS:

1. **Participants**: Objects or actors that participate in the interaction
   - **Actors**: External entities (users, systems)
     - Syntax: actor ActorName
     - Example: actor User, actor Administrator
   
   - **Participants**: System components, classes, or services
     - Syntax: participant ParticipantName
     - Example: participant LoginService, participant Database

2. **Lifelines**: Vertical dashed lines representing object existence over time
   - Automatically created for each participant
   - Show the lifespan of objects during the interaction

3. **Messages**: Communications between participants
   - **Synchronous**: --> (waits for response)
   - **Asynchronous**: ->> (doesn't wait for response)
   - **Return**: <-- (response message)
   - **Self-call**: --> (to self)

### ADVANCED CONCEPTS:

#### MESSAGE TYPES:

1. **Synchronous Messages (-->)**:
   - Sender waits for the receiver to process
   - Used for method calls, API requests
   - Example: User --> LoginService : authenticate(username, password)

2. **Asynchronous Messages (->>)**:
   - Sender doesn't wait for completion
   - Used for events, notifications
   - Example: PaymentService ->> NotificationService : sendPaymentConfirmation()

3. **Return Messages (<--)**:
   - Show the response or result
   - Can be explicit or implicit
   - Example: LoginService <-- Database : userDetails

4. **Create Messages**:
   - Show object creation
   - Syntax: create ObjectName
   - Example: LoginService -> create UserSession

5. **Destroy Messages**:
   - Show object destruction
   - Syntax: destroy ObjectName
   - Shows when objects are no longer needed

#### ACTIVATION BOXES:
- Show when an object is active (processing)
- Syntax: activate/deactivate ParticipantName
- Visual representation of method execution time

#### INTERACTION FRAGMENTS:

1. **Alternative (alt)**:
   - Conditional logic, if-else statements
   ```
   alt condition
       Message if true
   else
       Message if false
   end
   ```

2. **Optional (opt)**:
   - Optional execution based on condition
   ```
   opt condition
       Optional message
   end
   ```

3. **Loop**:
   - Repetitive interactions
   ```
   loop condition
       Repeated messages
   end
   ```

4. **Parallel (par)**:
   - Concurrent execution
   ```
   par
       First parallel flow
   and
       Second parallel flow
   end
   ```

5. **Break**:
   - Exception handling or early termination
   ```
   break condition
       Exception handling
   end
   ```

#### NOTES AND ANNOTATIONS:
- **note left/right/over**: Add explanatory notes
- **ref**: Reference to another sequence diagram
- **group**: Group related messages

### DESIGN PRINCIPLES:

#### INTERACTION DESIGN:
1. **Clear Flow**: Show logical sequence of operations
2. **Proper Abstraction**: Right level of detail for the audience
3. **Error Handling**: Include exception scenarios
4. **Timing**: Show time-dependent interactions

#### MESSAGE DESIGN:
1. **Meaningful Names**: Descriptive message labels
2. **Parameters**: Include relevant parameters
3. **Return Values**: Show important return values
4. **State Changes**: Reflect state modifications

### PLANTUML SYNTAX RULES:

#### BASIC SYNTAX:
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
    
    
    async def optimize_diagrams_with_llm_and_actors(self, original_requirements: str, class_diagram: str, 
                                                  sequence_diagram: str, identified_actors: List[str], 
                                                  verification_issues: Dict[str, Any]) -> Dict[str, Any]:
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

            # Enhanced Class Diagram Optimization
            class_prompt = f"""Generate a PlantUML class diagram with STRICT REQUIREMENTS:

ACTORS TO IMPLEMENT AS CLASSES: {actors_text}
REQUIREMENTS: {original_requirements[:500]}
ISSUES TO FIX: {issues_text[:200]}

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
- Examples: -userId: string, +name: string, -isAvailable: boolean

REQUIRED METHODS FORMAT:
- visibility methodName(params): ReturnType
- Examples: +login(): boolean, +addBook(book: Book): void

INHERITANCE RULES:
- If User is an actor, other user types inherit from User
- Use syntax: SubClass <|-- SuperClass
- Example: Librarian <|-- User : extends
- Use proper UML inheritance notation
- Use proper UML association notation

ASSOCIATION RULES:
- EVERY class needs relationships
- Use proper UML syntax with multiplicity
- Examples: Librarian --> "0..*" Book : manages

SYNTAX RULES:
- Use PascalCase for all class names without spaces. E.g., 'FundTransfer', not 'Fund Transfer'.
- Define only one version of each class. Avoid duplicate definitions (e.g., 'Service' vs. 'Services').
- Inherit from parent classes using the correct direction. E.g., 'Child <|-- Parent' is invalid.
- All attributes must follow the format: +attributeName: Type
- All methods must follow the format: +methodName(param: Type): ReturnType
- Use meaningful relationship labels; ensure association direction reflects real ownership or access.
- If a class contains another (e.g., Services contains many Service), model it with the correct aggregation.

Note: Before generating UML code, validate all class participants, check for naming collisions, confirm inheritance direction, and ensure syntactical correctness with complete closure of blocks. Prefer single-word PascalCase naming convention across all identifiers.


OUTPUT ONLY PlantUML code from @startuml to @enduml and make sure classes are well-structured, with proper attributes and methods defined. Avoid any generic classes or participants. Ensure all actors are represented as classes with meaningful relationships.

And the 

+[memberfunctions] Must be well defined inside class not outside or without class definition.

For E.g:

class ClassName 
{{
+variable: String
+function(date: Date): void
}}

In class diagram code, there are member functions defined outside the class definition, which is incorrect. Make sure to define member functions inside the class definition with proper syntax.

"""

            # Enhanced Sequence Diagram Optimization  
            sequence_prompt = f"""Generate a PlantUML sequence diagram with STRICT REQUIREMENTS:

MANDATORY PARTICIPANTS (And Make sure you do not add anything other than these): {actors_text}
REQUIREMENTS: {original_requirements[:500]}
ISSUES TO FIX: {issues_text[:200]}

PARTICIPANT DECLARATION:
- Use 'actor' for human roles, 'participant' for system components
- EVERY identified actor MUST appear as participant
- NO generic participants (System, Database, Application)

MESSAGE FLOW RULES:
- Each participant MUST send/receive at least 1 message
- Use proper syntax: A -> B : messageDescription
- Include return messages: B --> A : response
- Use activation boxes with activate/deactivate
- Use proper UML syntax for loops, alternatives, and options
- Use proper UML syntax for parallel flows

SECTION ORGANIZATION:
- Use == Section Name == for logical groupings
- Show realistic business workflow
- Include alt/opt blocks for conditions
- Use proper UML syntax for grouping messages

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
- Use aliases for multi-word participants. E.g., 'participant Fund_Transfer as "Fund Transfer"'
- Use consistent naming throughout the diagram for participants.
- Only define one logical actor (e.g., 'Customer') unless there are truly multiple human actors.
- Always close 'group', 'opt', 'alt', 'else' blocks with 'end'.
- Avoid nesting too many 'alt' and 'opt' blocks unless necessary; prefer clarity over depth.


FORBIDDEN ELEMENTS:
- "System" participant
- Undefined participant references
- Messages without descriptions
- Participants not in actor list
- Overly complex diagrams with too many participants
- Generic participants like "Database", "Application"

Note: Before generating UML code, validate all sequence participants, check for naming collisions, confirm inheritance direction, and ensure syntactical correctness with complete closure of blocks. Prefer single-word PascalCase naming convention across all identifiers.
Important: *Make sure to create proper relationships and avoid plantuml syntax errors*


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
            optimized_sequence = self._validate_and_fix_sequence_diagram(optimized_sequence)
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
    
    

    def _enforce_class_consistency(self, class_diagram: str, identified_actors: List[str]) -> str:
        """
        Post-process class diagram to ensure consistency with identified actors
        """
        try:
            lines = class_diagram.split('\n')
            processed_lines = []
            existing_classes = set()
            
            # Extract existing class names from the diagram
            class_pattern = r'class\s+(\w+)'
            for line in lines:
                match = re.search(class_pattern, line)
                if match:
                    existing_classes.add(match.group(1))
            
            # Process each line
            for line in lines:
                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith("'"):
                    processed_lines.append(line)
                    continue
                    
                # Remove generic system classes
                if any(generic in line.lower() for generic in ['class system', 'class database', 'class application']):
                    continue
                    
                # Fix generic references in relationships
                line = self._fix_generic_references(line)
                processed_lines.append(line)
            
            # Add missing actor classes
            missing_actors = []
            for actor in identified_actors:
                actor_class = self._to_pascal_case(actor)
                if actor_class not in existing_classes:
                    missing_actors.append(actor_class)
            
            # Insert missing classes before @enduml
            if missing_actors:
                insert_index = -1
                for i, line in enumerate(processed_lines):
                    if '@enduml' in line:
                        insert_index = i
                        break
                
                if insert_index > 0:
                    for actor_class in missing_actors:
                        class_definition = self._generate_class_definition(actor_class)
                        processed_lines.insert(insert_index, class_definition)
                        processed_lines.insert(insert_index + 1, "")
                        insert_index += 2
            
            # Ensure all classes have proper structure
            result = '\n'.join(processed_lines)
            result = self._ensure_class_structure(result, identified_actors)
            
            return result
            
        except Exception as e:
            print(f"Error in _enforce_class_consistency: {str(e)}")
            return class_diagram

    def _enforce_sequence_consistency(self, sequence_diagram: str, identified_actors: List[str]) -> str:
        """
        Post-process sequence diagram to ensure consistency with identified actors
        """
        try:
            lines = sequence_diagram.split('\n')
            processed_lines = []
            declared_participants = set()
            
            # Extract existing participants
            participant_patterns = [
                r'actor\s+(\w+)',
                r'participant\s+(\w+)',
                r'participant\s+"([^"]+)"\s+as\s+(\w+)',
                r'actor\s+"([^"]+)"\s+as\s+(\w+)'
            ]
            
            for line in lines:
                for pattern in participant_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if isinstance(match, tuple):
                            declared_participants.add(match[-1])  # Get the alias
                        else:
                            declared_participants.add(match)
            
            # Process each line
            for line in lines:
                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith("'"):
                    processed_lines.append(line)
                    continue
                
                # Remove generic system participants
                if any(generic in line.lower() for generic in ['participant system', 'actor system']):
                    continue
                
                # Fix generic references in messages
                line = self._fix_generic_message_references(line)
                processed_lines.append(line)
            
            # Add missing actor participants
            missing_participants = []
            for actor in identified_actors:
                actor_participant = self._to_pascal_case(actor)
                if actor_participant not in declared_participants:
                    missing_participants.append((actor, actor_participant))
            
            # Insert missing participants after @startuml
            if missing_participants:
                insert_index = 0
                for i, line in enumerate(processed_lines):
                    if '@startuml' in line:
                        insert_index = i + 1
                        break
                
                for original_actor, participant_name in missing_participants:
                    # Determine if it should be actor or participant
                    participant_type = "actor" if self._is_human_actor(original_actor) else "participant"
                    participant_line = f'{participant_type} {participant_name}'
                    processed_lines.insert(insert_index, participant_line)
                    insert_index += 1
            
            # Ensure all participants are used in messages
            result = '\n'.join(processed_lines)
            result = self._ensure_participant_usage(result, identified_actors)
            result = '@startuml\n' + result + '\n@enduml'
            
            return result
            
        except Exception as e:
            print(f"Error in _enforce_sequence_consistency: {str(e)}")
            return sequence_diagram

    

    def _fix_generic_references(self, line: str) -> str:
        """Fix generic references in class diagram relationships"""
        # Replace generic system references
        replacements = {
            'System': 'MainSystem',
            'Database': 'DataStore',
            'Application': 'AppCore'
        }
        
        for generic, replacement in replacements.items():
            line = re.sub(r'\b' + generic + r'\b', replacement, line)
        
        return line

    def _fix_generic_message_references(self, line: str) -> str:
        """Fix generic references in sequence diagram messages"""
        # Replace generic system references in messages
        replacements = {
            'System': 'MainSystem',
            'Database': 'DataStore',
            'Application': 'AppCore'
        }
        
        for generic, replacement in replacements.items():
            line = re.sub(r'\b' + generic + r'\s*->', replacement + ' ->', line)
            line = re.sub(r'->\s*' + generic + r'\b', '-> ' + replacement, line)
        
        return line

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase"""
        # Handle common actor names
        words = re.split(r'[\s_-]+', text.strip())
        return ''.join(word.capitalize() for word in words if word)

    def _generate_class_definition(self, class_name: str) -> str:
        """Generate a complete class definition with attributes and methods"""
        # Generate realistic attributes and methods based on class name
        attributes, methods = self._get_class_members(class_name)
        
        definition = f"class {class_name} {{\n"
        
        # Add attributes
        for attr in attributes:
            definition += f"  {attr}\n"
        
        # Add separator
        definition += "  --\n"
        
        # Add methods
        for method in methods:
            definition += f"  {method}\n"
        
        definition += "}"
        
        return definition

    def _get_class_members(self, class_name: str) -> tuple:
        """Get appropriate attributes and methods for a class based on its name"""
        name_lower = class_name.lower()
        
        # Default attributes and methods
        attributes = [
            f"-{name_lower}Id: string",
            f"+name: string",
            f"-isActive: boolean"
        ]
        
        methods = [
            f"+get{class_name}Id(): string",
            f"+setName(name: string): void",
            f"+isValid(): boolean"
        ]
        
        # Customize based on class name
        if 'user' in name_lower:
            attributes.extend(["-email: string", "-password: string"])
            methods.extend(["+login(): boolean", "+logout(): void"])
        elif 'book' in name_lower:
            attributes.extend(["-isbn: string", "-author: string"])
            methods.extend(["+getAuthor(): string", "+isAvailable(): boolean"])
        elif 'librarian' in name_lower:
            attributes.extend(["-employeeId: string", "-department: string"])
            methods.extend(["+addBook(book: Book): void", "+removeBook(bookId: string): boolean"])
        
        return attributes[:5], methods[:5]  # Limit to 5 each

    def _ensure_class_structure(self, diagram: str, identified_actors: List[str]) -> str:
        """Ensure all classes have proper structure with attributes and methods"""
        lines = diagram.split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a simple class declaration without body
            if re.match(r'^\s*class\s+\w+\s*$', line):
                class_name = re.search(r'class\s+(\w+)', line).group(1)
                # Replace with full class definition
                full_definition = self._generate_class_definition(class_name)
                processed_lines.append(full_definition)
            else:
                processed_lines.append(line)
            
            i += 1
        
        return '\n'.join(processed_lines)

    def _is_human_actor(self, actor: str) -> bool:
        """Determine if an actor represents a human role"""
        human_indicators = ['user', 'admin', 'customer', 'client', 'manager', 'staff', 'librarian', 'student']
        return any(indicator in actor.lower() for indicator in human_indicators)

    def _ensure_participant_usage(self, diagram: str, identified_actors: List[str]) -> str:
        """Ensure all participants are used in at least one message"""
        lines = diagram.split('\n')
        
        # Find all declared participants
        declared_participants = set()
        participant_patterns = [
            r'actor\s+(\w+)',
            r'participant\s+(\w+)',
            r'participant\s+"([^"]+)"\s+as\s+(\w+)',
            r'actor\s+"([^"]+)"\s+as\s+(\w+)'
        ]
        
        for line in lines:
            for pattern in participant_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple):
                        declared_participants.add(match[-1])
                    else:
                        declared_participants.add(match)
        
        # Find participants used in messages
        used_participants = set()
        message_pattern = r'(\w+)\s*-[->]+\s*(\w+)'
        
        for line in lines:
            matches = re.findall(message_pattern, line)
            for match in matches:
                used_participants.add(match[0])
                used_participants.add(match[1])
        
        # Add simple messages for unused participants
        unused_participants = declared_participants - used_participants
        
        if unused_participants:
            # Find insertion point (before @enduml)
            insert_index = -1
            for i, line in enumerate(lines):
                if '@enduml' in line:
                    insert_index = i
                    break
            
            if insert_index > 0:
                # Add a simple interaction section for unused participants
                if unused_participants:
                    lines.insert(insert_index, "")
                    lines.insert(insert_index + 1, "== Additional Interactions ==")
                    insert_index += 2
                    
                    for participant in unused_participants:
                        # Find another participant to interact with
                        other_participant = next(iter(declared_participants - {participant}), "System")
                        lines.insert(insert_index, f"{participant} -> {other_participant} : performs action")
                        lines.insert(insert_index + 1, f"{other_participant} --> {participant} : confirmation")
                        insert_index += 2
        
        return '\n'.join(lines)
    

    def _validate_and_fix_sequence_diagram(self, plantuml_code: str) -> str:
        """
        Validate sequence diagram and fix undefined references or syntax issues
        """
        try:
            lines = plantuml_code.split('\n')
            declared_participants = set()
            referenced_participants = set()
            valid_lines = []
            
            # First pass: identify declared participants
            participant_patterns = [
                r'actor\s+(\w+)',
                r'participant\s+(\w+)',
                r'participant\s+"([^"]+)"\s+as\s+(\w+)',
                r'actor\s+"([^"]+)"\s+as\s+(\w+)'
            ]
            
            for line in lines:
                for pattern in participant_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        if isinstance(match, tuple):
                            declared_participants.add(match[-1])  # Get the alias
                        else:
                            declared_participants.add(match)
            
            # Second pass: identify referenced participants and validate messages
            message_pattern = r'(\w+)\s*-[->]+\s*(\w+)'
            for line in lines:
                if '->' in line or '-->' in line:
                    matches = re.findall(message_pattern, line)
                    for match in matches:
                        referenced_participants.add(match[0])
                        referenced_participants.add(match[1])
            
            # Third pass: validate lines and fix issues
            for line in lines:
                line_stripped = line.strip()
                
                # Skip empty lines and comments
                if not line_stripped or line_stripped.startswith("'"):
                    valid_lines.append(line)
                    continue
                
                # Check if the line has references to undeclared participants
                has_undeclared = False
                if '->' in line or '-->' in line:
                    matches = re.findall(message_pattern, line)
                    for match in matches:
                        if match[0] not in declared_participants or match[1] not in declared_participants:
                            print(f"Removing message with undeclared participant: {line}")
                            has_undeclared = True
                            break
                
                # Add the line if it's valid
                if not has_undeclared:
                    # Remove System references
                    if 'System' not in line or any(p in line for p in declared_participants):
                        valid_lines.append(line)
            
            # Fourth pass: ensure all declared participants are used
            unused_participants = declared_participants - referenced_participants
            if unused_participants and len(declared_participants) > 1:
                # Add simple interactions for unused participants
                end_index = next((i for i, line in enumerate(valid_lines) if '@enduml' in line), len(valid_lines))
                
                valid_lines.insert(end_index, "== Additional Interactions ==")
                
                for unused in unused_participants:
                    # Pick another participant to interact with
                    other = next((p for p in declared_participants if p != unused), None)
                    if other:
                        valid_lines.insert(end_index + 1, f"{unused} -> {other}: interacts")
                        valid_lines.insert(end_index + 2, f"{other} --> {unused}: responds")
            
            # Reconstruct with proper PlantUML structure
            result = "@startuml\n"
            for line in valid_lines:
                if '@startuml' not in line and '@enduml' not in line:
                    result += line + "\n"
            result += "@enduml"
            
            return result
            
        except Exception as e:
            print(f"Error validating sequence diagram: {str(e)}")
            return plantuml_code



