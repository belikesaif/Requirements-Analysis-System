"""
Memory Storage for research data management
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

class MemoryStorage:
    def __init__(self):
        self.case_studies = {}
        self.comparisons = {}
        self.diagrams = {}
        self.statistics = {
            'total_processed': 0,
            'average_accuracy': 0.0,
            'processing_history': []
        }
        
        # Create research data directory if it doesn't exist
        self.research_dir = "D:/SRS Artifacts Gen Tool/nlp-requirements-system/research_data"
        os.makedirs(self.research_dir, exist_ok=True)
    
    def store_case_study(self, case_study_data: Dict[str, Any]) -> str:
        """
        Store a processed case study and return unique ID
        """
        try:
            case_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            case_study_record = {
                'id': case_id,
                'timestamp': timestamp,
                'title': case_study_data.get('title', 'Untitled'),
                'original_text': case_study_data.get('original_text', ''),
                'rupp_result': case_study_data.get('rupp_result', {}),
                'ai_result': case_study_data.get('ai_result', {}),
                'comparison': case_study_data.get('comparison', {}),
                'processed_date': timestamp
            }
            
            self.case_studies[case_id] = case_study_record
            
            # Update statistics
            self._update_statistics(case_study_record)
            
            # Auto-save to file for persistence
            self._save_to_file('case_studies.json', self.case_studies)
            
            return case_id
        
        except Exception as e:
            raise Exception(f"Failed to store case study: {str(e)}")
    
    def store_diagram(self, diagram_data: Dict[str, Any]) -> str:
        """
        Store diagram data and return unique ID
        """
        try:
            diagram_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            diagram_record = {
                'id': diagram_id,
                'timestamp': timestamp,
                'type': diagram_data.get('type', 'unknown'),
                'plantuml_code': diagram_data.get('plantuml_code', ''),
                'snl_data': diagram_data.get('snl_data', {}),
                'created_date': timestamp
            }
            
            self.diagrams[diagram_id] = diagram_record
            
            # Auto-save to file
            self._save_to_file('diagrams.json', self.diagrams)
            
            return diagram_id
        
        except Exception as e:
            raise Exception(f"Failed to store diagram: {str(e)}")
    
    def get_case_study(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific case study by ID
        """
        return self.case_studies.get(case_id)
    
    def get_all_case_studies(self) -> List[Dict[str, Any]]:
        """
        Get all stored case studies
        """
        return list(self.case_studies.values())
    
    def get_diagram(self, diagram_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific diagram by ID
        """
        return self.diagrams.get(diagram_id)
    
    def get_comparison_statistics(self) -> Dict[str, Any]:
        """
        Calculate and return comparison statistics
        """
        try:
            if not self.case_studies:
                return {
                    'total_case_studies': 0,
                    'average_accuracy': 0.0,
                    'average_precision': 0.0,
                    'average_recall': 0.0,
                    'average_f1_score': 0.0,
                    'total_missing': 0,
                    'total_overspecified': 0,
                    'total_out_of_scope': 0,
                    'quality_distribution': {},
                    'processing_timeline': []
                }
            
            # Calculate aggregate statistics
            total_cases = len(self.case_studies)
            accuracies = []
            precisions = []
            recalls = []
            f1_scores = []
            missing_counts = []
            overspecified_counts = []
            out_of_scope_counts = []
            quality_assessments = []
            
            for case_study in self.case_studies.values():
                comparison = case_study.get('comparison', {})
                metrics = comparison.get('metrics', {})
                categorization = comparison.get('categorization', {})
                summary = comparison.get('summary', {})
                
                # Collect metrics
                if metrics:
                    accuracies.append(metrics.get('accuracy', 0))
                    precisions.append(metrics.get('precision', 0))
                    recalls.append(metrics.get('recall', 0))
                    f1_scores.append(metrics.get('f1_score', 0))
                
                # Collect categorization counts
                missing_counts.append(len(categorization.get('missing', [])))
                overspecified_counts.append(len(categorization.get('overspecified', [])))
                out_of_scope_counts.append(len(categorization.get('out_of_scope', [])))
                
                # Collect quality assessments
                quality = summary.get('quality_assessment', 'Unknown')
                quality_assessments.append(quality)
            
            # Calculate averages
            avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            avg_precision = sum(precisions) / len(precisions) if precisions else 0
            avg_recall = sum(recalls) / len(recalls) if recalls else 0
            avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
            
            # Quality distribution
            quality_dist = {}
            for quality in quality_assessments:
                quality_dist[quality] = quality_dist.get(quality, 0) + 1
            
            # Processing timeline
            timeline = []
            for case_study in sorted(self.case_studies.values(), key=lambda x: x['timestamp']):
                timeline.append({
                    'date': case_study['timestamp'][:10],  # Extract date part
                    'title': case_study['title'],
                    'accuracy': case_study.get('comparison', {}).get('metrics', {}).get('accuracy', 0)
                })
            
            return {
                'total_case_studies': total_cases,
                'average_accuracy': round(avg_accuracy, 3),
                'average_precision': round(avg_precision, 3),
                'average_recall': round(avg_recall, 3),
                'average_f1_score': round(avg_f1, 3),
                'total_missing': sum(missing_counts),
                'total_overspecified': sum(overspecified_counts),
                'total_out_of_scope': sum(out_of_scope_counts),
                'quality_distribution': quality_dist,
                'processing_timeline': timeline[-10:],  # Last 10 entries
                'last_updated': datetime.now().isoformat()
            }
        
        except Exception as e:
            raise Exception(f"Failed to calculate statistics: {str(e)}")
    
    def export_all_data(self) -> Dict[str, Any]:
        """
        Export all stored data for research analysis
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'case_studies': self.case_studies,
                'diagrams': self.diagrams,
                'statistics': self.get_comparison_statistics(),
                'metadata': {
                    'total_case_studies': len(self.case_studies),
                    'total_diagrams': len(self.diagrams),
                    'export_version': '1.0.0'
                }
            }
            
            # Save export to file
            export_filename = f"research_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self._save_to_file(export_filename, export_data)
            
            return export_data
        
        except Exception as e:
            raise Exception(f"Failed to export data: {str(e)}")
    
    def clear_all_data(self):
        """
        Clear all stored data (for research purposes)
        """
        try:
            self.case_studies.clear()
            self.diagrams.clear()
            self.statistics = {
                'total_processed': 0,
                'average_accuracy': 0.0,
                'processing_history': []
            }
            
            # Clear saved files
            self._save_to_file('case_studies.json', {})
            self._save_to_file('diagrams.json', {})
            
        except Exception as e:
            raise Exception(f"Failed to clear data: {str(e)}")
    
    def _update_statistics(self, case_study_record: Dict[str, Any]):
        """
        Update running statistics with new case study
        """
        try:
            self.statistics['total_processed'] += 1
            
            # Add to processing history
            comparison = case_study_record.get('comparison', {})
            metrics = comparison.get('metrics', {})
            
            history_entry = {
                'timestamp': case_study_record['timestamp'],
                'case_id': case_study_record['id'],
                'title': case_study_record['title'],
                'accuracy': metrics.get('accuracy', 0),
                'f1_score': metrics.get('f1_score', 0)
            }
            
            self.statistics['processing_history'].append(history_entry)
            
            # Keep only last 100 entries
            if len(self.statistics['processing_history']) > 100:
                self.statistics['processing_history'] = self.statistics['processing_history'][-100:]
            
            # Update average accuracy
            accuracies = [entry['accuracy'] for entry in self.statistics['processing_history']]
            self.statistics['average_accuracy'] = sum(accuracies) / len(accuracies) if accuracies else 0
        
        except Exception as e:
            # Don't fail the main operation if statistics update fails
            print(f"Warning: Failed to update statistics: {str(e)}")
    
    def _save_to_file(self, filename: str, data: Any):
        """
        Save data to JSON file in research directory
        """
        try:
            filepath = os.path.join(self.research_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Warning: Failed to save to file {filename}: {str(e)}")
    
    def load_from_files(self):
        """
        Load existing data from files on startup
        """
        try:
            # Load case studies
            case_studies_file = os.path.join(self.research_dir, 'case_studies.json')
            if os.path.exists(case_studies_file):
                with open(case_studies_file, 'r', encoding='utf-8') as f:
                    self.case_studies = json.load(f)
            
            # Load diagrams
            diagrams_file = os.path.join(self.research_dir, 'diagrams.json')
            if os.path.exists(diagrams_file):
                with open(diagrams_file, 'r', encoding='utf-8') as f:
                    self.diagrams = json.load(f)
            
            print(f"Loaded {len(self.case_studies)} case studies and {len(self.diagrams)} diagrams from storage")
        
        except Exception as e:
            print(f"Warning: Failed to load from files: {str(e)}")
    
    def search_case_studies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search case studies by title or content
        """
        try:
            query_lower = query.lower()
            results = []
            
            for case_study in self.case_studies.values():
                title = case_study.get('title', '').lower()
                original_text = case_study.get('original_text', '').lower()
                
                if query_lower in title or query_lower in original_text:
                    results.append(case_study)
                
                if len(results) >= limit:
                    break
            
            return results
        
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
