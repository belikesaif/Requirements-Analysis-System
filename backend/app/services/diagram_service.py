"""
AI-Powered Diagram Service for generating UML diagrams from SNL requirements using OpenAI
"""

import openai
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class DiagramService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    async def generate_class_diagram(self, snl_data: Dict[str, Any]) -> str:
        """
        Generate PlantUML class diagram from SNL data using OpenAI
        """
        try:
            snl_text = snl_data.get('snl_text', '')
            actors = snl_data.get('actors', [])
            
            prompt = self._create_class_diagram_prompt(snl_text, actors)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_class_diagram_system_prompt()},
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
    
    def _get_class_diagram_system_prompt(self) -> str:
        """
        System prompt for class diagram generation
        """
        return """You are an expert software architect and UML diagram specialist. Your task is to generate PlantUML class diagrams from Structured Natural Language (SNL) requirements.

Guidelines:
1. Analyze the SNL requirements to identify key entities, actors, and system components
2. Create classes for main entities (User, System, Database, etc.)
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
            raise Exception(f"Sequence diagram generation failed: {str(e)}")
    
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
