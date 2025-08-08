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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ Warning: OPENAI_API_KEY not set, AI features will be disabled")
            self.client = None
        else:
            try:
                self.client = openai.AsyncOpenAI(
                    api_key=api_key
                )
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"⚠️ Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    async def generate_ai_snl(self, requirements_text: str) -> Dict[str, Any]:
        """
        Generate SNL using OpenAI GPT model
        """
        if not self.client:
            return {
                "status": "error",
                "message": "OpenAI client not available - check API key configuration"
            }
            
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
3. Create atomic, testable requirements
4. Handle conditional logic appropriately

Note: Please do not include identified actors in the snl requirements text.

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
        if not self.client:
            return requirement  # Return original if no AI available
            
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
        if not self.client:
            return []  # Return empty list if no AI available
            
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
    
    async def analyze_ai_vs_original_case_study(self, ai_requirements: List[str], original_text: str) -> Dict[str, Any]:
        """
        Analyze AI-generated SNL against original case study to identify missing, overspecified, and incorrect instances
        """
        try:
            prompt = self._create_comparison_analysis_prompt(ai_requirements, original_text)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_comparison_analysis_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            # Parse the analysis result
            try:
                import json
                analysis_result = json.loads(response.choices[0].message.content)
                
                # Ensure all required fields are present
                required_fields = ['missing_in_ai', 'overspecified_in_ai', 'incorrect_in_ai', 'analysis_summary']
                for field in required_fields:
                    if field not in analysis_result:
                        analysis_result[field] = []
                
                return analysis_result
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'missing_in_ai': [],
                    'overspecified_in_ai': [],
                    'incorrect_in_ai': [],
                    'analysis_summary': "Analysis completed but unable to parse detailed results",
                    'raw_response': response.choices[0].message.content
                }
        
        except Exception as e:
            raise Exception(f"AI accuracy analysis failed: {str(e)}")
    
    async def analyze_ai_vs_rupp_snl(self, ai_requirements: List[str], rupp_requirements: List[str]) -> Dict[str, Any]:
        """
        Analyze AI-generated SNL against RUPP-generated SNL to identify missing, overspecified, and incorrect instances
        """
        if not self.client:
            return {
                "status": "error",
                "message": "OpenAI client not available - check API key configuration"
            }
            
        try:
            # Check if we need to chunk the analysis due to size
            total_chars = sum(len(req) for req in ai_requirements + rupp_requirements)
            chunk_size = 50  # Requirements per chunk
            
            if len(ai_requirements) > chunk_size or len(rupp_requirements) > chunk_size or total_chars > 15000:
                print(f"DEBUG - Large dataset detected, using chunked analysis: AI={len(ai_requirements)}, RUPP={len(rupp_requirements)}, chars={total_chars}")
                return await self._chunked_analysis(ai_requirements, rupp_requirements)
            else:
                print(f"DEBUG - Using direct analysis: AI={len(ai_requirements)}, RUPP={len(rupp_requirements)}")
                return await self._direct_analysis(ai_requirements, rupp_requirements)
                
        except Exception as e:
            raise Exception(f"AI vs RUPP analysis failed: {str(e)}")

    async def _direct_analysis(self, ai_requirements: List[str], rupp_requirements: List[str]) -> Dict[str, Any]:
        """
        Perform direct analysis of all requirements
        """
        prompt = self._create_ai_vs_rupp_comparison_prompt(ai_requirements, rupp_requirements)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_ai_vs_rupp_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        
        return self._parse_analysis_response(response)

    async def _chunked_analysis(self, ai_requirements: List[str], rupp_requirements: List[str]) -> Dict[str, Any]:
        """
        Break down analysis into chunks and combine results
        """
        all_missing = []
        all_overspecified = []
        all_incorrect = []
        
        # Analyze in chunks of 30 requirements at a time
        chunk_size = 30
        
        for i in range(0, len(ai_requirements), chunk_size):
            ai_chunk = ai_requirements[i:i+chunk_size]
            # Use all RUPP requirements for each chunk to ensure nothing is missed
            
            print(f"DEBUG - Analyzing chunk {i//chunk_size + 1}: AI requirements {i+1}-{min(i+chunk_size, len(ai_requirements))}")
            
            prompt = self._create_ai_vs_rupp_comparison_prompt(ai_chunk, rupp_requirements)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_ai_vs_rupp_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            chunk_result = self._parse_analysis_response(response)
            
            # Combine results, adjusting indices for AI requirements
            for item in chunk_result.get('missing_in_ai', []):
                all_missing.append(item)
            
            for item in chunk_result.get('overspecified_in_ai', []):
                # Adjust AI index to account for chunk offset
                if 'ai_index' in item:
                    item['ai_index'] += i
                all_overspecified.append(item)
            
            for item in chunk_result.get('incorrect_in_ai', []):
                # Adjust AI index to account for chunk offset
                if 'ai_index' in item:
                    item['ai_index'] += i
                all_incorrect.append(item)
        
        return {
            'missing_in_ai': all_missing,
            'overspecified_in_ai': all_overspecified,
            'incorrect_in_ai': all_incorrect,
            'analysis_summary': f"Comprehensive chunked analysis completed. Found {len(all_missing)} missing, {len(all_overspecified)} overspecified, and {len(all_incorrect)} incorrect requirements."
        }

    def _parse_analysis_response(self, response) -> Dict[str, Any]:
        """
        Parse and clean the AI response
        """
        try:
            import json
            raw_content = response.choices[0].message.content
            print(f"DEBUG - Raw AI response: {raw_content[:500]}...")
            
            # Clean the response to extract JSON
            cleaned_content = raw_content.strip()
            
            # Look for JSON object boundaries
            start_idx = cleaned_content.find('{')
            end_idx = cleaned_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_content = cleaned_content[start_idx:end_idx]
                print(f"DEBUG - Extracted JSON: {json_content[:200]}...")
            else:
                json_content = cleaned_content
                print(f"DEBUG - Using full content as JSON")
            
            analysis_result = json.loads(json_content)
            print(f"DEBUG - Parsed analysis result keys: {analysis_result.keys()}")
            
            # Ensure all required fields are present
            required_fields = ['missing_in_ai', 'overspecified_in_ai', 'incorrect_in_ai', 'analysis_summary']
            for field in required_fields:
                if field not in analysis_result:
                    analysis_result[field] = []
            
            return analysis_result
            
        except json.JSONDecodeError as e:
            print(f"DEBUG - JSON parsing failed: {e}")
            print(f"DEBUG - Full raw response: {response.choices[0].message.content}")
            # Fallback if JSON parsing fails
            return {
                'missing_in_ai': [],
                'overspecified_in_ai': [],
                'incorrect_in_ai': [],
                'analysis_summary': f"Analysis completed but JSON parsing failed: {str(e)}",
                'raw_response': response.choices[0].message.content
            }

        except Exception as e:
            raise Exception(f"AI vs RUPP analysis failed: {str(e)}")
    
    def _get_ai_vs_rupp_system_prompt(self) -> str:
        """
        System prompt for AI vs RUPP SNL comparison analysis
        """
        return """You are an expert requirements analyst comparing two sets of software requirements. 

**CONTEXT:**
- RUPP requirements: Generated by a rule-based algorithm (consistent, structured)
- AI requirements: Generated by an AI system (may have variations, additions, or errors)
- Both sets describe the same software system functionality

**YOUR TASK:**
Perform a detailed line-by-line comparison to categorize AI requirements into exactly 3 categories:

**1. MISSING in AI (Requirements in RUPP that AI completely missed):**
- Look for RUPP requirements that have NO equivalent functionality in AI
- Don't mark as missing if AI expresses the same concept differently
- Focus on completely absent functional requirements

**2. OVERSPECIFIED in AI (AI added unnecessary detail/assumptions):**
- Requirements where AI went beyond RUPP's level of detail
- AI added implementation specifics not in RUPP
- AI made assumptions or added features not in RUPP scope
- AI broke down simple RUPP requirements into excessive detail

**3. INCORRECT in AI (AI made actual mistakes):**
- Factual errors about system behavior
- Logic inconsistencies compared to RUPP
- Wrong actor assignments or permissions
- Contradictions with RUPP's intent

**CRITICAL INSTRUCTIONS:**
- Be VERY selective - not every difference is a problem
- Equivalent functionality with different wording is NOT an issue
- Only flag actual problems, not stylistic differences
- Provide specific, detailed reasoning for each issue
- If AI and RUPP express the same thing differently, that's NORMAL

**OUTPUT FORMAT:**
Return ONLY valid JSON with specific examples and clear reasoning for each category. Do not include any text before or after the JSON.

{
    "missing_in_ai": [
        {
            "requirement": "exact RUPP requirement text that has no AI equivalent",
            "rupp_index": number,
            "reason": "detailed explanation of what functionality is completely missing"
        }
    ],
    "overspecified_in_ai": [
        {
            "requirement": "exact AI requirement text that adds unnecessary detail", 
            "ai_index": number,
            "reason": "specific explanation of why this exceeds RUPP's scope"
        }
    ],
    "incorrect_in_ai": [
        {
            "requirement": "exact AI requirement text with errors",
            "ai_index": number,
            "issue_type": "factual|logic|interpretation|security",
            "reason": "specific explanation of the error compared to RUPP"
        }
    ],
    "analysis_summary": "overall assessment focusing on the most significant differences"
}

IMPORTANT: Return ONLY the JSON object above, nothing else."""
    
    def _create_ai_vs_rupp_comparison_prompt(self, ai_requirements: List[str], rupp_requirements: List[str]) -> str:
        """
        Create prompt for AI vs RUPP SNL comparison analysis
        """
        # Use ALL requirements for complete analysis
        ai_text = "\n".join([f"{i+1}. {req}" for i, req in enumerate(ai_requirements)])
        rupp_text = "\n".join([f"{i+1}. {req}" for i, req in enumerate(rupp_requirements)])
        
        return f"""Compare ALL software requirements from both sets:

**RUPP-GENERATED REQUIREMENTS** ({len(rupp_requirements)} total):
{rupp_text}

**AI-GENERATED REQUIREMENTS** ({len(ai_requirements)} total):
{ai_text}

**Analysis Task:**
Perform a COMPLETE comparison of all requirements to identify:

1. **MISSING**: RUPP requirements with no AI equivalent (completely absent functionality)
2. **OVERSPECIFIED**: AI requirements that go beyond RUPP's scope (excessive detail/assumptions)  
3. **INCORRECT**: AI requirements with factual errors vs RUPP

Analyze EVERY requirement thoroughly. Be comprehensive in your analysis."""

    def _get_comparison_analysis_system_prompt(self) -> str:
        """
        System prompt for AI vs Initial Case study comparison analysis
        """
        return """You are a requirements analyst comparing two sets of software requirements. One set was Initial Case Study, and another was generated by AI.

Compare these two sets and identify:

1. MISSING: Requirements from the Initial Case Study that the AI didn't capture
2. OVERSPECIFIED: Requirements where the AI was too detailed or specific 
3. INCORRECT: Requirements where the AI made mistakes or errors

For each issue, explain why it's problematic in simple terms.

Return your analysis in JSON format:
{
    "missing_in_ai": [
        {
            "requirement": "the requirement text",
            "rupp_index": number,
            "reason": "why this is missing"
        }
    ],
    "overspecified_in_ai": [
        {
            "requirement": "the requirement text", 
            "ai_index": number,
            "reason": "why this is too detailed"
        }
    ],
    "incorrect_in_ai": [
        {
            "requirement": "the requirement text",
            "ai_index": number,
            "issue_type": "factual|security|logic",
            "reason": "what's wrong with this"
        }
    ],
    "analysis_summary": "brief overall assessment"
}"""
    
    def _create_comparison_analysis_prompt(self, ai_requirements: List[str], original_text: str) -> str:
        """
        Create prompt for AI vs Initial Case Study comparison analysis
        """
        ai_text = "\n".join([f"{i+1}. {req}" for i, req in enumerate(ai_requirements)])
        
        # Don't try to split and enumerate the original text, just use it as is
        original_case_study = original_text[:1500] + "..." if len(original_text) > 1500 else original_text
        
        return f"""Here are requirements from a software project:

ORIGINAL CASE STUDY:
{original_case_study}

AI-GENERATED REQUIREMENTS:
{ai_text}

Please compare these two sets and find where the AI-generated requirements have issues compared to the initial case study. Look for missing requirements, overly detailed specifications, and factual errors."""




