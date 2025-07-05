"""
AI Service for generating SNL using OpenAI GPT models
"""

import openai
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    async def generate_ai_snl(self, requirements_text: str) -> Dict[str, Any]:
        """
        Generate SNL using OpenAI GPT model
        """
        try:
            prompt = self._create_snl_prompt(requirements_text)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            ai_snl_text = response.choices[0].message.content
            
            # Parse the response to extract individual requirements
            snl_requirements = self._parse_ai_response(ai_snl_text)
            
            return {
                'snl_text': ai_snl_text,
                'requirements': snl_requirements,
                'model_used': self.model,
                'sentences_count': len(snl_requirements),
                'raw_response': ai_snl_text
            }
        
        except Exception as e:
            raise Exception(f"AI SNL generation failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """
    Get the system prompt for SNL generation
    """
        return """You are an expert software requirements analyst. Your task is to convert natural language case study descriptions into DETAILED Structured Natural Language (SNL) requirements following these guidelines:

1. Use the format: "The system shall provide [ACTOR] with the ability to [ACTION]" for user actions
2. Use the format: "The system shall be able to [ACTION]" for system actions
3. Use conditional format: "If [CONDITION] then the system shall be able to [ACTION]" for conditional requirements
4. Identify all actors (users, roles) in the text
5. Extract ALL functional requirements at the most granular level possible
6. Ensure each requirement is atomic and testable
7. Break down complex features into multiple atomic requirements
8. Capture ALL data validation, error handling, and edge cases as separate requirements
9. Include system responses, notifications, and feedback mechanisms as separate requirements
10. Maintain traceability to the original case study
11. Generate a MINIMUM of 70 requirements for comprehensive coverage

Generate clear, unambiguous, highly detailed requirements that follow software engineering best practices."""
    
    def _create_snl_prompt(self, requirements_text: str) -> str:
        """
        Create the prompt for SNL generation
        """
        return f"""Convert the following case study into Structured Natural Language (SNL) requirements:

Case Study:
{requirements_text}

Please generate SNL requirements that:
1. Capture all functional requirements from the case study
2. Use proper SNL formatting
3. Identify and consistently use actor names
4. Create atomic, testable requirements
5. Handle conditional logic appropriately

Output each requirement on a separate line, numbered sequentially."""
    
    def _parse_ai_response(self, response_text: str) -> List[str]:
        """
        Parse AI response into individual requirements
        """
        try:
            # Split by lines and clean up
            lines = response_text.strip().split('\n')
            requirements = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove numbering if present
                    if line[0].isdigit() and '.' in line:
                        line = line.split('.', 1)[1].strip()
                    
                    # Clean up formatting
                    line = line.strip('- *')
                    
                    if line:
                        requirements.append(line)
            
            return requirements
        
        except Exception as e:
            # Fallback: return the entire text as one requirement
            return [response_text]
    
    async def improve_requirement(self, requirement: str, context: str = "") -> str:
        """
        Improve a single requirement using AI
        """
        try:
            prompt = f"""Improve the following requirement to make it clearer, more specific, and better formatted:

Original Requirement: {requirement}

Context: {context}

Please provide an improved version that:
1. Uses proper SNL format
2. Is more specific and measurable
3. Removes ambiguity
4. Follows software engineering best practices

Return only the improved requirement text."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a requirements engineering expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Requirement improvement failed: {str(e)}")
    
    async def extract_actors_ai(self, requirements_text: str) -> List[str]:
        """
        Extract actors from text using AI
        """
        try:
            prompt = f"""Extract all actors (users, roles, external systems) from the following requirements text:

Text: {requirements_text}

Return only a comma-separated list of actor names. For example: "Member, Librarian, System Administrator, Guest User"
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying actors in software requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            actors_text = response.choices[0].message.content.strip()
            actors = [actor.strip() for actor in actors_text.split(',')]
            
            return [actor for actor in actors if actor]
        
        except Exception as e:
            raise Exception(f"AI actor extraction failed: {str(e)}")
    
    async def validate_requirement(self, requirement: str) -> Dict[str, float]:
        """
        Validate a single requirement using AI
        """
        try:
            prompt = self._create_validation_prompt(requirement)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_validation_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            # Parse validation results
            try:
                import json
                validation_result = json.loads(response.choices[0].message.content)
                return validation_result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'clarity': 7.0,
                    'completeness': 7.0,
                    'atomicity': 7.0
                }
        
        except Exception as e:
            raise Exception(f"Requirement validation failed: {str(e)}")
    
    def _get_validation_system_prompt(self) -> str:
        """
        System prompt for requirement validation
        """
        return """You are an expert requirements analyst. Your task is to validate software requirements for clarity, completeness, and atomicity.

Guidelines:
1. Clarity: Evaluate if the requirement is clear and unambiguous
2. Completeness: Check if all necessary details are included
3. Atomicity: Verify that the requirement describes a single feature/function

Score each aspect from 0.0 to 10.0 and return results in JSON format:
{
    "clarity": float,
    "completeness": float,
    "atomicity": float
}"""
    
    def _create_validation_prompt(self, requirement: str) -> str:
        """
        Create prompt for requirement validation
        """
        return f"""Please validate the following software requirement:

{requirement}

Analyze the requirement for:
1. Clarity: Is it clear and unambiguous?
2. Completeness: Are all necessary details included?
3. Atomicity: Does it describe a single feature/function?

Return your analysis in the specified JSON format with scores from 0.0 to 10.0."""
    
    
    

