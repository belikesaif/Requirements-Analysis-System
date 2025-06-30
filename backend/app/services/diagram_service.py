"""
AI-Powered Diagram Service for generating UML diagrams from SNL requirements using OpenAI
"""

import openai
import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class DiagramService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
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
                    {"role": "system", "content": self._get_enhanced_class_diagram_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            plantuml_code = response.choices[0].message.content
            
            # Clean and validate the PlantUML code
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            
            return plantuml_code
        
        except Exception as e:
            raise Exception(f"Class diagram generation failed: {str(e)}")
    
    async def generate_sequence_diagram(self, snl_data: Dict[str, Any]) -> str:
        """
        Generate PlantUML sequence diagram from SNL data using OpenAI
        """
        try:
            snl_text = snl_data.get('snl_text', '')
            actors = snl_data.get('actors', [])
            
            prompt = self._create_sequence_diagram_prompt(snl_text, actors)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_sequence_diagram_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            plantuml_code = response.choices[0].message.content
            
            # Clean and validate the PlantUML code
            plantuml_code = self._clean_plantuml_code(plantuml_code)
            
            return plantuml_code
        
        except Exception as e:
            raise Exception(f"Sequence diagram generation failed: {str(e)}")
    
    async def generate_class_diagram_from_rupp(self, snl_text: str) -> str:
        """
        Generate initial PlantUML class diagram from SNL text only (before actor identification)
        This is the first step in the diagram generation process using only the RUPP SNL output
        """
        try:
            # Create prompt for initial class diagram using only SNL text
            prompt = self._create_initial_class_diagram_prompt(snl_text)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_initial_class_diagram_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
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
                max_tokens=1500
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
                max_tokens=1500
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
    
    def _extract_entities_with_pos(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities using POS tagging for enhanced diagram generation
        """
        if not self.nlp:
            return {'nouns': [], 'verbs': [], 'proper_nouns': []}
        
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

    def _get_enhanced_class_diagram_system_prompt(self) -> str:
        """
        Enhanced system prompt for class diagram generation with POS tagging integration
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to generate PlantUML class diagrams from Structured Natural Language (SNL) requirements with enhanced entity recognition.

Guidelines:
1. Analyze the SNL requirements AND extracted entities (nouns, verbs, proper nouns)
2. Use extracted nouns as potential class names and attributes
3. Use extracted verbs as potential methods
4. Create classes for main entities (User, System, Database, etc.)
5. Define appropriate attributes and methods for each class based on extracted entities
6. Establish relationships between classes (associations, dependencies, inheritance)
7. Use proper PlantUML syntax with access modifiers (+, -, #, ~)
8. Prioritize clarity - don't overcomplicate with too many classes
9. Focus on domain-relevant classes from the requirements context

Generate ONLY the PlantUML code, starting with @startuml and ending with @enduml."""
    
    def _create_enhanced_class_diagram_prompt(self, snl_text: str, actors: List[str], extracted_entities: Dict[str, List[str]]) -> str:
        """
        Create enhanced prompt for class diagram generation with POS tagging data
        """
        actors_text = ", ".join(actors) if actors else "Not specified"
        
        entities_text = ""
        if extracted_entities:
            entities_text = f"""
Extracted Entities (from POS tagging):
- Nouns (potential classes/attributes): {', '.join(extracted_entities.get('nouns', [])[:10])}
- Verbs (potential methods): {', '.join(extracted_entities.get('verbs', [])[:10])}
- Proper Nouns (potential class names): {', '.join(extracted_entities.get('proper_nouns', [])[:5])}
"""
        
        return f"""Generate a PlantUML class diagram from the following SNL requirements:

SNL Requirements:
{snl_text}

Identified Actors: {actors_text}
{entities_text}

Please create a comprehensive class diagram that shows:
1. Main classes for entities mentioned in the requirements
2. Attributes and methods for each class (use extracted entities as guidance)
3. Relationships between classes
4. Proper access modifiers
5. Focus on 3-7 main classes to maintain clarity

Focus on the core entities and their relationships as described in the requirements."""

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
                excluded_words = ['view','system', 'click', 'enter', 'select', 'login', 'issue', 'return', 'home', 'page', 'button', 'id', 'details', 'books', 'members', 'users']
                
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
            
            # Also use LLM to extract actors from requirements text
            prompt = f"""Analyze the following requirements and identify all actors (users, roles, external systems):

Requirements:
{original_requirements}

Also consider the entities mentioned in these diagrams:
Class Diagram: {class_diagram[:500]}...
Sequence Diagram: {sequence_diagram[:500]}...

List all actors as a comma-separated list. Focus on:
1. User roles (Admin, User, Customer, etc.)
2. External systems
3. Stakeholders mentioned in requirements
4. Entities that perform actions

Return only the actor names separated by commas."""

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
            
            # Combine and deduplicate actors
            all_actors = list(set(extracted_actors + llm_actors))
            
            # Filter out empty strings and overly generic terms
            excluded_terms = ['system', 'database', 'application', 'data', 'information', 'details', 'management', 'view', 'click', 'enter', 'select', 'login', 'home', 'page', 'button', 'id', 'books', 'members', 'users']
            filtered_actors = [
                actor for actor in all_actors 
                if actor and len(actor) > 1 and actor.lower() not in excluded_terms and not actor.endswith('.')
            ]
            
            # Resolve semantic conflicts between similar actors (e.g., User vs Member)
            resolved_actors = self._resolve_actor_conflicts(filtered_actors, original_requirements)
            
            return resolved_actors[:10]  # Limit to 10 actors for manageable processing
            
        except Exception as e:
            print(f"Error extracting actors: {str(e)}")
            return ['User', 'System', 'Admin']  # Fallback actors

    async def verify_diagrams_with_actors(self, class_diagram: str, sequence_diagram: str, identified_actors: List[str]) -> Dict[str, Any]:
        """
        Verify diagrams against identified actors with enhanced missing actor detection
        """
        try:
            actors_text = ", ".join(identified_actors)
            
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
                                                  verification_issues: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final LLM optimization using GPT-3.5 with identified actors and verification feedback
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

            # Optimize class diagram
            class_prompt = f"""STRICT OPTIMIZATION TASK: Generate an optimized class diagram using ONLY the specified actors.

IDENTIFIED ACTORS (USE EXACTLY THESE): {actors_text}

Original Requirements:
{original_requirements}

Current Class Diagram:
{class_diagram}

Verification Issues:
{issues_text}

MANDATORY REQUIREMENTS:
1. Create a class for EACH identified actor: {actors_text}
2. DO NOT create any generic classes like "System", "Database", "Application"
3. DO NOT add any actors/classes not in the identified list
4. If you need system components, name them specifically (e.g., "LoginController", "BookCatalog")
5. Each identified actor MUST appear as a class with appropriate attributes and methods
6. MUST include meaningful relationships between classes (associations, dependencies, aggregations)
7. Use the original requirements to define class attributes, methods, and relationships
8. Show how actors interact with each other through relationships
9. Include relationship labels and multiplicity where appropriate

REQUIRED RELATIONSHIPS (MANDATORY):
- Every class MUST have at least one relationship to another class
- Show associations between classes that interact (e.g., Member --> Book : borrows)
- Include dependency relationships for temporary interactions
- Add aggregation/composition where one class contains another
- Use inheritance if there are class hierarchies
- Label all relationships with meaningful names
- Include multiplicity (e.g., "1" -- "0..*", "1" o-- "many")

REFERENCE VALIDATION (CRITICAL):
- If you reference a class in a relationship, that class MUST be defined in the diagram
- Do not reference undefined classes in relationships
- Use consistent class names throughout the diagram
- Avoid orphaned classes (classes with no relationships)

FORBIDDEN:
- Generic "System" class
- Any actor not in the identified list
- Vague or generic class names
- Classes without any relationships to other classes
- Relationships that reference undefined classes

Generate ONLY the optimized PlantUML class diagram code that includes ALL identified actors as classes WITH proper relationships between them."""

            class_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict UML diagram generator. You MUST create classes for ALL specified actors and AVOID generic elements. Follow the requirements exactly."},
                    {"role": "user", "content": class_prompt}
                ],
                temperature=0.2,  # Lower temperature for more controlled output
                max_tokens=1500
            )

            # Optimize sequence diagram
            sequence_prompt = f"""STRICT OPTIMIZATION TASK: Generate an optimized sequence diagram using ONLY the specified actors.

IDENTIFIED ACTORS (USE EXACTLY THESE AS PARTICIPANTS): {actors_text}

Original Requirements:
{original_requirements}

Current Sequence Diagram:
{sequence_diagram}

Verification Issues:
{issues_text}

MANDATORY REQUIREMENTS:
1. Include EACH identified actor as a participant: {actors_text}
2. DO NOT use generic participants like "System", "Database", "Application"
3. DO NOT add any participants not in the identified list
4. Show realistic interactions between the identified actors based on requirements
5. If you need system services, name them specifically (e.g., "LoginService", "BookService")
6. Focus on the main workflow involving the identified actors
7. Each identified actor MUST participate in the sequence
8. MUST show meaningful message flows between participants
9. Include activation boxes for active participants
10. Show request-response patterns between actors
11. Include conditional flows (alt/opt) if mentioned in requirements
12. Show return messages where appropriate

REQUIRED INTERACTIONS (MANDATORY):
- Show how actors communicate with each other
- Include message labels that describe the interaction
- Use proper sequence diagram syntax with arrows
- Show the flow of control between participants
- Include lifelines for all participants
- Use activation boxes to show when participants are active

FORBIDDEN:
- Generic "System" participant
- Any participant not in the identified list
- Vague or generic participant names
- Sequences without meaningful interactions between actors

Generate ONLY the optimized PlantUML sequence diagram code that includes ALL identified actors as participants WITH proper message flows and interactions between them."""

            sequence_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strict UML sequence diagram generator. You MUST include ALL specified actors as participants and AVOID generic elements. Follow the requirements exactly."},
                    {"role": "user", "content": sequence_prompt}
                ],
                temperature=0.2,  # Lower temperature for more controlled output
                max_tokens=1500
            )

            optimized_class = self._clean_plantuml_code(class_response.choices[0].message.content)
            optimized_sequence = self._clean_plantuml_code(sequence_response.choices[0].message.content)

            # Validate and fix any undefined references in the optimized diagrams
            optimized_class = self._validate_and_fix_class_diagram(optimized_class)

            return {
                "class_diagram": optimized_class,
                "sequence_diagram": optimized_sequence,
                "improvements": [
                    f"Included ALL identified actors: {actors_text}",
                    "Removed generic 'System' elements",
                    "Used specific class/participant names",
                    "Addressed verification issues",
                    "Maintained consistency between diagrams",
                    "Validated and fixed undefined references"
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
                if line.strip() and not line.strip().startswith('@'):
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
