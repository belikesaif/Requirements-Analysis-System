"""
Comparison Service for analyzing differences between RUPP and AI-generated SNL
"""

import difflib
from typing import Dict, Any, List, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score
import re

class ComparisonService:
    def __init__(self):
        self.similarity_threshold = 0.3  # Lowered from 0.5 to 0.3 for better categorization
    def compare_snl(self, rupp_snl: str, ai_snl: str, original_text: str) -> Dict[str, Any]:
        """
        Compare RUPP and AI-generated SNL and categorize differences
        """
        try:
            import time
            start_time = time.time()
            
            # Parse SNL into individual requirements
            rupp_requirements = self._parse_snl_requirements(rupp_snl)
            ai_requirements = self._parse_snl_requirements(ai_snl)
            
            # Calculate similarities
            similarities = self._calculate_similarities(rupp_requirements, ai_requirements)
            
            # Categorize differences
            categorization = self._categorize_differences(
                rupp_requirements, 
                ai_requirements, 
                original_text
            )
            
            # Calculate metrics
            metrics = self._calculate_metrics(rupp_requirements, ai_requirements)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Extract actors from RUPP requirements for stats
            actors_detected = len(set(word.lower() for req in rupp_requirements 
                                   for word in req.split() 
                                   if word.lower() in ['user', 'admin', 'system', 'librarian', 'member', 'guest']))
            
            return {
                'rupp_requirements': rupp_requirements,
                'ai_requirements': ai_requirements,
                'similarities': similarities,
                'categorization': categorization,
                'metrics': metrics,
                'summary': self._generate_summary(categorization, metrics),
                'rupp_metrics': {
                    'processing_time': round(processing_time, 2),
                    'requirements_count': len(rupp_requirements),
                    'actors_detected': actors_detected,
                    'accuracy_score': round(metrics.get('accuracy', 0) * 100, 1)
                },
                'ai_metrics': {
                    'processing_time': round(processing_time * 1.2, 2),  # Simulate AI processing time
                    'requirements_count': len(ai_requirements),
                    'actors_detected': actors_detected,
                    'accuracy_score': round(metrics.get('precision', 0) * 100, 1)
                },
                'comparison': {
                    'winner': 'RUPP' if len(rupp_requirements) >= len(ai_requirements) else 'AI',
                    'summary': f'RUPP generated {len(rupp_requirements)} requirements vs AI generated {len(ai_requirements)} requirements'
                }
            }
        
        except Exception as e:
            raise Exception(f"SNL comparison failed: {str(e)}")
    
    def _parse_snl_requirements(self, snl_text: str) -> List[str]:
        """
        Parse SNL text into individual requirements
        """
        try:
            # Split by sentences and clean up
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', snl_text)
            
            requirements = []
            for sentence in sentences:
                sentence = sentence.strip()
                
                # Remove numbering if present
                sentence = re.sub(r'^\d+\.\s*', '', sentence)
                
                # Clean up and filter
                if sentence and len(sentence) > 10:  # Filter out very short sentences
                    requirements.append(sentence)
            
            return requirements
        
        except Exception as e:
            return [snl_text]  # Fallback
    
    def _calculate_similarities(self, rupp_requirements: List[str], ai_requirements: List[str]) -> List[Dict[str, Any]]:
        """
        Calculate similarity scores between requirements
        """
        similarities = []
        
        for i, rupp_req in enumerate(rupp_requirements):
            best_match = None
            best_similarity = 0
            
            for j, ai_req in enumerate(ai_requirements):
                similarity = self._calculate_similarity(rupp_req, ai_req)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {
                        'ai_index': j,
                        'ai_requirement': ai_req,
                        'similarity': similarity
                    }
            
            similarities.append({
                'rupp_index': i,
                'rupp_requirement': rupp_req,
                'best_match': best_match,
                'similarity_score': best_similarity
            })
        
        return similarities
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using multiple methods
        """
        try:
            # Basic sequence matcher
            matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
            seq_similarity = matcher.ratio()
            
            # Word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if len(words1) == 0 and len(words2) == 0:
                return 1.0
            if len(words1) == 0 or len(words2) == 0:
                return 0.0
                
            word_similarity = len(words1.intersection(words2)) / len(words1.union(words2))
              # Combine similarities (weighted average)
            combined_similarity = (seq_similarity * 0.7) + (word_similarity * 0.3)
            
            return combined_similarity
        except Exception:
            return 0.0
    
    def _categorize_differences(self, rupp_requirements: List[str], ai_requirements: List[str], original_text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize differences between RUPP and AI requirements
        """
        try:
            missing = []  # In RUPP but not in AI (Red)
            overspecified = []  # In AI but not in RUPP (Yellow)
            out_of_scope = []  # Not in original case study (Blue)
            matched = []  # Similar requirements (unique pairs)
            
            # Track which AI requirements have been matched to avoid double counting
            ai_matched_indices = set()
            
            # Find missing requirements (RUPP -> AI)
            for i, rupp_req in enumerate(rupp_requirements):
                best_similarity = 0
                best_ai_index = -1
                
                for j, ai_req in enumerate(ai_requirements):
                    similarity = self._calculate_similarity(rupp_req, ai_req)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_ai_index = j
                
                if best_similarity >= self.similarity_threshold and best_ai_index not in ai_matched_indices:
                    # This is a match
                    matched.append({
                        'rupp_index': i,
                        'rupp_requirement': rupp_req,
                        'ai_index': best_ai_index,
                        'ai_requirement': ai_requirements[best_ai_index],
                        'similarity': best_similarity,
                        'category': 'matched'
                    })
                    ai_matched_indices.add(best_ai_index)
                else:
                    # This RUPP requirement has no good match in AI
                    missing.append({
                        'index': i,
                        'requirement': rupp_req,
                        'best_similarity': best_similarity,
                        'category': 'missing'
                    })
            
            # Find overspecified requirements (AI requirements not matched)
            for i, ai_req in enumerate(ai_requirements):
                if i not in ai_matched_indices:
                    # This AI requirement wasn't matched to any RUPP requirement
                    # Check if it's related to original text
                    original_similarity = self._calculate_similarity(ai_req, original_text)
                    
                    if original_similarity < 0.3:  # Threshold for out-of-scope
                        out_of_scope.append({
                            'index': i,
                            'requirement': ai_req,
                            'original_similarity': original_similarity,
                            'category': 'out_of_scope'
                        })
                    else:
                        overspecified.append({
                            'index': i,
                            'requirement': ai_req,
                            'category': 'overspecified'
                        })
            
            return {
                'missing': missing,
                'overspecified': overspecified,
                'out_of_scope': out_of_scope,
                'matched': matched
            }
        
        except Exception as e:
            return {
                'missing': [],
                'overspecified': [],
                'out_of_scope': [],
                'matched': [],
                'error': str(e)
            }
    def _calculate_metrics(self, rupp_requirements: List[str], ai_requirements: List[str]) -> Dict[str, float]:
        """
        Calculate precision, recall, F1 score, and other metrics based on matched pairs
        """
        try:
            # Get categorization to use matched pairs
            categorization = self._categorize_differences(rupp_requirements, ai_requirements, "")
            
            matched_pairs = len(categorization.get('matched', []))
            missing_count = len(categorization.get('missing', []))
            overspecified_count = len(categorization.get('overspecified', []))
            out_of_scope_count = len(categorization.get('out_of_scope', []))
            
            total_rupp = len(rupp_requirements)
            total_ai = len(ai_requirements)
            
            # Correct calculation of metrics:
            # Precision = True Positives / (True Positives + False Positives)
            # False Positives = overspecified + out_of_scope
            false_positives = overspecified_count + out_of_scope_count
            precision = matched_pairs / (matched_pairs + false_positives) if (matched_pairs + false_positives) > 0 else 0
            
            # Recall = True Positives / (True Positives + False Negatives)
            # False Negatives = missing
            recall = matched_pairs / (matched_pairs + missing_count) if (matched_pairs + missing_count) > 0 else 0
            
            # F1 Score
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Accuracy = (True Positives) / (Total Ground Truth)
            # Using RUPP as ground truth
            accuracy = matched_pairs / total_rupp if total_rupp > 0 else 0
            
            return {
                'precision': round(min(precision, 1.0), 3),  # Ensure max 1.0
                'recall': round(min(recall, 1.0), 3),       # Ensure max 1.0
                'f1_score': round(min(f1, 1.0), 3),         # Ensure max 1.0
                'accuracy': round(min(accuracy, 1.0), 3),    # Ensure max 1.0
                'matched_pairs': matched_pairs,
                'missing_count': missing_count,
                'overspecified_count': overspecified_count,
                'out_of_scope_count': out_of_scope_count,
                'total_rupp_requirements': total_rupp,
                'total_ai_requirements': total_ai,
                'similarity_threshold': self.similarity_threshold
            }
        
        except Exception as e:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'accuracy': 0.0,
                'overspecification': 0,
                'error': str(e)
            }
    
    def _generate_summary(self, categorization: Dict[str, List], metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate a summary of the comparison results
        """
        try:
            return {
                'total_rupp_requirements': metrics.get('total_rupp_requirements', 0),
                'total_ai_requirements': metrics.get('total_ai_requirements', 0),
                'missing_count': len(categorization.get('missing', [])),
                'overspecified_count': len(categorization.get('overspecified', [])),
                'out_of_scope_count': len(categorization.get('out_of_scope', [])),
                'matched_count': len(categorization.get('matched', [])),
                'overall_similarity': metrics.get('f1_score', 0),
                'quality_assessment': self._assess_quality(metrics),
                'recommendations': self._generate_recommendations(categorization, metrics)
            }
        
        except Exception as e:
            return {'error': str(e)}
    
    def _assess_quality(self, metrics: Dict[str, float]) -> str:
        """
        Assess the overall quality of AI-generated SNL
        """
        f1_score = metrics.get('f1_score', 0)
        
        if f1_score >= 0.9:
            return "Excellent"
        elif f1_score >= 0.8:
            return "Good"
        elif f1_score >= 0.7:
            return "Fair"
        elif f1_score >= 0.6:
            return "Poor"
        else:
            return "Very Poor"
    
    def _generate_recommendations(self, categorization: Dict[str, List], metrics: Dict[str, float]) -> List[str]:
        """
        Generate recommendations based on comparison results
        """
        recommendations = []
        
        missing_count = len(categorization.get('missing', []))
        overspecified_count = len(categorization.get('overspecified', []))
        out_of_scope_count = len(categorization.get('out_of_scope', []))
        
        if missing_count > 0:
            recommendations.append(f"Consider adding {missing_count} missing requirements to AI-generated SNL")
        
        if overspecified_count > 0:
            recommendations.append(f"Review {overspecified_count} potentially overspecified requirements")
        
        if out_of_scope_count > 0:
            recommendations.append(f"Remove {out_of_scope_count} out-of-scope requirements")
        
        if metrics.get('precision', 0) < 0.8:
            recommendations.append("Improve requirement precision by reducing overspecification")
        
        if metrics.get('recall', 0) < 0.8:
            recommendations.append("Improve requirement coverage by capturing more functional requirements")
        
        return recommendations
    
    async def analyze_ai_snl_detailed(self, ai_snl, original_text: str, ai_service) -> Dict[str, Any]:
        """
        Enhanced comparison analysis using AI service for detailed categorization
        Compare AI-generated SNL against original case study text
        """
        try:
            # Handle list input for AI SNL
            if isinstance(ai_snl, list):
                ai_requirements = ai_snl
            else:
                ai_requirements = self._parse_snl_requirements(ai_snl)
            
            # Get AI-powered detailed analysis comparing against original case study
            ai_analysis = await ai_service.analyze_ai_vs_original_case_study(
                ai_requirements, original_text
            )
            
            # Create detailed stats
            detailed_stats = {
                'missing_in_ai': {
                    'count': len(ai_analysis.get('missing_in_ai', [])),
                    'items': ai_analysis.get('missing_in_ai', []),
                    'description': 'Requirements from original case study that AI failed to capture'
                },
                'overspecified_in_ai': {
                    'count': len(ai_analysis.get('overspecified_in_ai', [])),
                    'items': ai_analysis.get('overspecified_in_ai', []),
                    'description': 'Requirements where AI was too detailed or specific beyond case study scope'
                },
                'incorrect_in_ai': {
                    'count': len(ai_analysis.get('incorrect_in_ai', [])),
                    'items': ai_analysis.get('incorrect_in_ai', []),
                    'description': 'Requirements where AI made factual errors or misinterpretations'
                },
                'total_issues': (
                    len(ai_analysis.get('missing_in_ai', [])) + 
                    len(ai_analysis.get('overspecified_in_ai', [])) + 
                    len(ai_analysis.get('incorrect_in_ai', []))
                ),
                'analysis_summary': ai_analysis.get('analysis_summary', ''),
                'accuracy_percentage': self._calculate_accuracy_percentage(
                    len(ai_requirements),
                    len(ai_analysis.get('missing_in_ai', [])) + 
                    len(ai_analysis.get('overspecified_in_ai', [])) + 
                    len(ai_analysis.get('incorrect_in_ai', []))
                )
            }
            
            # Return the detailed analysis
            return {
                'ai_requirements': ai_requirements,
                'detailed_ai_analysis': detailed_stats,
                'comparison_method': 'ai_vs_original_case_study'
            }
            
        except Exception as e:
            # Fallback on error
            return {
                'ai_requirements': ai_requirements if 'ai_requirements' in locals() else [],
                'detailed_ai_analysis': {
                    'error': f"AI analysis failed: {str(e)}",
                    'fallback_used': True,
                    'missing_in_ai': {'count': 0, 'items': [], 'description': 'Analysis unavailable'},
                    'overspecified_in_ai': {'count': 0, 'items': [], 'description': 'Analysis unavailable'},
                    'incorrect_in_ai': {'count': 0, 'items': [], 'description': 'Analysis unavailable'},
                    'total_issues': 0,
                    'accuracy_percentage': 0,
                    'analysis_summary': 'Analysis failed due to technical issues'
                }
            }
    
    def _calculate_accuracy_percentage(self, total_requirements: int, total_issues: int) -> float:
        """
        Calculate accuracy percentage based on total requirements and issues found
        """
        if total_requirements == 0:
            return 0.0
        
        accurate_requirements = max(0, total_requirements - total_issues)
        accuracy = (accurate_requirements / total_requirements) * 100
        return round(accuracy, 1)
