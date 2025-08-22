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

    def _identify_case_study_type(self, requirements: str) -> str:
        """
        Identify which case study type based on key terms in requirements
        MUST use the same naming convention as diagram_service.py
        """
        requirements_lower = requirements.lower()
        
        # Use the EXACT same logic as diagram_service.py _identify_case_study_pattern
        # 1. Library Management System - FIRST check for very specific library terms
        if ('member' in requirements_lower and 'librarian' in requirements_lower and 
            any(word in requirements_lower for word in ['book', 'library']) and
            any(word in requirements_lower for word in ['issue', 'borrow', 'return', 'reserve'])):
            return "Library Management System"
            
        # 2. Railway Reservation System - MUST check BEFORE Zoom Car (shares similar patterns)
        if (('customer' in requirements_lower and 'admin' in requirements_lower) and
            ('train' in requirements_lower or 'railway' in requirements_lower) and
            'reservation' in requirements_lower and
            'source station' in requirements_lower and 'destination station' in requirements_lower):
            return "Railway Reservation System"
            
        # 3. Online Bus Reservation System - MUST check BEFORE Zoom Car (shares similar patterns)
        if (('customer' in requirements_lower and 'admin' in requirements_lower) and
            'bus' in requirements_lower and 'reservation' in requirements_lower and
            'source station' in requirements_lower and 'destination station' in requirements_lower):
            return "Online Bus Reservation System"
            
        # 4. Zoom Car Booking System - car booking with customer and admin (check AFTER train/bus)
        if (('customer' in requirements_lower and 'admin' in requirements_lower) and
            ('car' in requirements_lower or 'vehicle' in requirements_lower) and
            any(word in requirements_lower for word in ['booking', 'book', 'zoom']) and
            'source station' in requirements_lower and 'destination station' in requirements_lower):
            return "Zoom Car Booking System"
            
        # 5. Monitoring Operating System - operator with monitoring and alarms
        if ('operator' in requirements_lower and 
            any(word in requirements_lower for word in ['monitoring', 'sensor', 'alarm']) and
            any(word in requirements_lower for word in ['emergency', 'outstanding alarm', 'monitoring status'])):
            return "Monitoring Operator System"
            
        # 6. Digital Home System - temperature, humidity, thermostat
        if (any(word in requirements_lower for word in ['temperature', 'humidity', 'thermostat', 'humidistat']) and
            any(word in requirements_lower for word in ['home', 'appliance', 'sensor']) and
            'control' in requirements_lower):
            return "Digital Home System"
            
        # 7. Online Pet Store - customer, supplier, catalog with pets
        if (('customer' in requirements_lower and 'supplier' in requirements_lower) and
            any(word in requirements_lower for word in ['pet', 'catalog']) and
            any(word in requirements_lower for word in ['dog', 'cat', 'bird']) and
            'shopping cart' in requirements_lower):
            return "Pet Store System"
            
        # 8. College Registration System - student, administrator, paper, report
        if (('student' in requirements_lower and 'administrator' in requirements_lower) and
            any(word in requirements_lower for word in ['paper', 'exam', 'report']) and
            any(word in requirements_lower for word in ['register', 'registration', 'college'])):
            return "College Registration System"
            
        # 9. Online Discussion Group - leader, student, presentation, comment
        if (('leader' in requirements_lower and 'student' in requirements_lower) and
            any(word in requirements_lower for word in ['discussion group', 'presentation', 'comment']) and
            'authenticate' in requirements_lower):
            return "Discussion Group System"
            
        # 10. Online Bookstore System - customer with shopping cart and book
        if ('customer' in requirements_lower and 
            'shopping cart' in requirements_lower and
            any(word in requirements_lower for word in ['book', 'bookstore']) and
            'register' in requirements_lower and 'login' in requirements_lower):
            return "Online Bookstore"
            
        # 11. LIS (Library Information System) - staff, administrator, report, item
        if (('staff' in requirements_lower and 'administrator' in requirements_lower) and
            any(word in requirements_lower for word in ['report', 'item', 'patron']) and
            any(word in requirements_lower for word in ['branch', 'template']) and
            'query' in requirements_lower):
            return "LIS"
            
        # 12. EStore System - user, profile, configuration, product
        if ('user' in requirements_lower and
            any(word in requirements_lower for word in ['product', 'configuration', 'profile']) and
            any(word in requirements_lower for word in ['component', 'support', 'financing']) and
            'shopping cart' in requirements_lower):
            return "E-Store"
            
        # 13. iCoot System/Car Rental - customer, member, carmodel, assistant
        if (('customer' in requirements_lower and 'member' in requirements_lower) and
            any(word in requirements_lower for word in ['carmodel', 'car model', 'icoot']) and
            'assistant' in requirements_lower and 'reservation' in requirements_lower):
            return "Car Rental System"
            
        # 14. Puget/E-Learning System - students, administrator, voiceclip, wiki
        if (('students' in requirements_lower and 'administrator' in requirements_lower) and
            any(word in requirements_lower for word in ['voice clip', 'wiki', 'blog', 'file']) and
            any(word in requirements_lower for word in ['grade', 'course', 'moodle'])):
            return "E-Learning"
            
        # 15. CCTNS System - interface, data, access, security
        if (any(word in requirements_lower for word in ['interface', 'data', 'access', 'security']) and
            any(word in requirements_lower for word in ['multilingual', 'ssl', 'authentication']) and
            any(word in requirements_lower for word in ['architecture', 'network', 'scalability'])):
            return "CCTNS"
        
        # Fallback patterns with exact actor matching
        # Only use fallbacks if no specific pattern was matched above
        
        # Fallback for any remaining operator patterns
        if 'operator' in requirements_lower:
            return "Monitoring Operator System"
            
        # Fallback for library-related terms
        if any(word in requirements_lower for word in ['librarian', 'member']) and 'book' in requirements_lower:
            return "Library Management System"
            
        # Fallback for customer/admin with car-related terms  
        if ('customer' in requirements_lower and 'admin' in requirements_lower and 'car' in requirements_lower):
            return "Zoom Car Booking System"
            
        # Fallback for user with home automation terms
        if 'user' in requirements_lower and any(word in requirements_lower for word in ['temperature', 'humidity', 'control']):
            return "Digital Home System"
            
        # More specific fallbacks for remaining patterns
        if 'customer' in requirements_lower and 'supplier' in requirements_lower:
            return "Pet Store System"
            
        if 'student' in requirements_lower and 'administrator' in requirements_lower:
            if 'paper' in requirements_lower or 'report' in requirements_lower:
                return "College Registration System"
            elif 'voice clip' in requirements_lower or 'wiki' in requirements_lower:
                return "E-Learning"
                
        if 'leader' in requirements_lower and 'student' in requirements_lower:
            return "Discussion Group System"
            
        if 'staff' in requirements_lower and 'administrator' in requirements_lower:
            return "LIS"
            
        if any(word in requirements_lower for word in ['interface', 'data']):
            return "CCTNS"
        
        return "Unknown Pattern"

    def _get_expected_actors_for_case_study(self, case_study_type: str) -> List[str]:
        """
        Return the expected actors for each case study type
        MUST use the same naming convention as diagram_service.py
        """
        expected_actors = {
            "Library Management System": ['User', 'Member', 'Guest', 'Administrator', 'Book', 'Librarian'],
            "Zoom Car Booking System": ['User', 'Customer', 'Admin', 'Booking', 'Car', 'PaymentSystem', 'HelpFacility'],
            "Monitoring Operator System": ['Operator', 'RemoteSensor', 'MonitoringSystem', 'Alarm', 'HelpFacility', 'Notification', 'MonitoringLocation', 'Sensor'],
            "Digital Home System": ['User', 'Humidistat', 'Thermostat', 'Alarm', 'Sensor', 'Planner', 'PowerSwitch', 'Appliance'],
            "CCTNS": ['Interface', 'Data', 'Access', 'Architecture', 'CommunicationNetwork', 'Security'],
            "College Registration System": ['Student', 'Administrator', 'Paper', 'Report'],
            "E-Store": ['User', 'Profile', 'Support', 'Promotion', 'Financing', 'Order', 'Configuration', 'ShoppingCart', 'Payment', 'Invoice', 'Product'],
            "Car Rental System": ['Customer', 'Member', 'CarModel', 'Assistant', 'Reservation'],
            "LIS": ['Staff', 'Branch', 'Adminstrator', 'Report', 'Item', 'Patron', 'ReportTemplate', 'Transaction'],
            "Online Bookstore": ['Customer', 'Order', 'ShoppingCart', 'Book'],
            "Online Bus Reservation System": ['HelpFacility', 'User', 'Customer', 'Admin', 'Payment', 'Reservation', 'Bus'],
            "Discussion Group System": ['User', 'Leader', 'DiscussionGroup', 'Student', 'Presentation', 'Comment'],
            "Pet Store System": ['Customer', 'Supplier', 'Authentication', 'Catalog', 'Shopping Cart', 'Order', 'Inventory', 'Item', 'PaymentMethod'],
            "Railway Reservation System": ['Customer', 'Reservation', 'HelpFacility', 'Admin', 'Train'],
            "E-Learning": ['Students', 'Administrator', 'VoiceClip', 'Wiki', 'Blog', 'File', 'Grade']
        }
        return expected_actors.get(case_study_type, [])

    async def extract_actors_from_requirements(self, original_requirements: str, class_diagram: str, sequence_diagram: str) -> List[str]:
        """
        Extract actors from original requirements with case study specific logic
        """
        try:
            print(f"Starting actor extraction from requirements...")
            print(f"Requirements length: {len(original_requirements)} characters")
            
            # Step 1: Identify case study type
            case_study_type = self._identify_case_study_type(original_requirements)
            print(f"Identified case study type: {case_study_type}")
            
            # Step 2: Get expected actors for this case study
            expected_actors = self._get_expected_actors_for_case_study(case_study_type)
            print(f"Expected actors for {case_study_type}: {expected_actors}")
            
            # Return the expected actors directly
            return expected_actors
            
        except Exception as e:
            print(f"Error in actor extraction: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback to basic actor extraction
            return ['User', 'Administrator', 'System']

    async def verify_diagrams_with_actors(self, class_diagram: str, sequence_diagram: str, identified_actors: List[str], original_requirements: str = "") -> Dict[str, Any]:
        """
        Verify generated diagrams against identified actors with detailed analysis
        """
        try:
            print(f"Starting detailed diagram verification...")
            print(f"Identified actors: {identified_actors}")
            
            # Extract actors from class diagram
            class_diagram_actors = self._extract_actors_from_class_diagram(class_diagram)
            print(f"Actors found in class diagram: {class_diagram_actors}")
            
            # Extract actors from sequence diagram  
            sequence_diagram_actors = self._extract_actors_from_sequence_diagram(sequence_diagram)
            print(f"Actors found in sequence diagram: {sequence_diagram_actors}")
            
            # Extract ALL classes from class diagram to detect overspecified ones
            all_diagram_classes = self._extract_all_classes_from_diagram(class_diagram)
            print(f"All classes in diagram: {all_diagram_classes}")
            
            # Find missing actors
            missing_from_class = [actor for actor in identified_actors if actor not in class_diagram_actors]
            missing_from_sequence = [actor for actor in identified_actors if actor not in sequence_diagram_actors]
            overall_missing = list(set(missing_from_class + missing_from_sequence))
            
            # Find present actors
            present_in_class = [actor for actor in identified_actors if actor in class_diagram_actors]
            present_in_sequence = [actor for actor in identified_actors if actor in sequence_diagram_actors]
            overall_present = [actor for actor in identified_actors if actor in class_diagram_actors and actor in sequence_diagram_actors]
            
            # Categorize overspecified/extra classes
            overspecified_classes = []
            incorrect_classes = []
            extra_classes = []
            
            for class_name in all_diagram_classes:
                if class_name not in identified_actors:
                    if self._is_incorrect_actor(class_name):
                        incorrect_classes.append(class_name)
                    elif self._exists_in_requirements(class_name, original_requirements):
                        overspecified_classes.append(class_name)
                    else:
                        extra_classes.append(class_name)
            
            # Calculate coverage
            total_actors = len(identified_actors)
            present_count = len(overall_present)
            coverage_percentage = (present_count / total_actors * 100) if total_actors > 0 else 0
            
            # Calculate consistency score
            class_consistency = len(present_in_class) / total_actors if total_actors > 0 else 0
            sequence_consistency = len(present_in_sequence) / total_actors if total_actors > 0 else 0
            consistency_score = (class_consistency + sequence_consistency) / 2
            
            verification_results = {
                "missing_actors": overall_missing,
                "present_actors": overall_present,
                "overspecified_classes": overspecified_classes,
                "incorrect_classes": incorrect_classes,
                "extra_classes": extra_classes,
                "class_diagram_actors": class_diagram_actors,
                "sequence_diagram_actors": sequence_diagram_actors,
                "actor_coverage": {
                    "identified_actors": identified_actors,
                    "actors_in_class_diagram": class_diagram_actors,
                    "actors_in_sequence_diagram": sequence_diagram_actors,
                    "missing_from_class": missing_from_class,
                    "missing_from_sequence": missing_from_sequence,
                    "coverage_percentage": coverage_percentage
                },
                "diagram_consistency": {
                    "class_sequence_alignment": len(present_in_class) == len(present_in_sequence),
                    "actor_representation": "good" if coverage_percentage > 80 else "needs_improvement",
                    "consistency_score": consistency_score
                },
                "quality_metrics": {
                    "completeness": coverage_percentage / 100,
                    "accuracy": 1.0 - (len(incorrect_classes) / max(len(all_diagram_classes), 1)),
                    "consistency": consistency_score
                },
                "statistics": {
                    'total_identified_actors': total_actors,
                    'present_count': present_count,
                    'missing_count': len(overall_missing),
                    'overspecified_count': len(overspecified_classes),
                    'incorrect_count': len(incorrect_classes),
                    'extra_count': len(extra_classes),
                    'coverage_percentage': coverage_percentage
                },
                "recommendations": self._generate_recommendations(overall_missing, overspecified_classes, incorrect_classes, coverage_percentage),
                "overall_score": coverage_percentage / 100
            }
            
            print(f"Verification completed. Coverage: {coverage_percentage:.1f}%")
            return verification_results
            
        except Exception as e:
            print(f"Error in diagram verification: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "missing_actors": identified_actors,
                "present_actors": [],
                "overspecified_classes": [],
                "incorrect_classes": [],
                "extra_classes": [],
                "actor_coverage": {"coverage_percentage": 0},
                "diagram_consistency": {"consistency_score": 0},
                "quality_metrics": {"completeness": 0, "accuracy": 0, "consistency": 0},
                "statistics": {
                    'total_identified_actors': len(identified_actors),
                    'present_count': 0,
                    'missing_count': len(identified_actors),
                    'overspecified_count': 0,
                    'incorrect_count': 0,
                    'extra_count': 0,
                    'coverage_percentage': 0
                },
                "recommendations": ["Manual review required", "Regenerate diagrams"],
                "overall_score": 0.0
            }

    def _extract_actors_from_class_diagram(self, class_diagram: str) -> List[str]:
        """
        Extract actor-like entities from the PlantUML class diagram
        """
        try:
            import re
            # Pattern for extracting class definitions
            class_pattern = re.compile(r'(?:class|participant|actor)\s+("?)([A-Za-z0-9_ ]+)\1')
            matches = class_pattern.findall(class_diagram)
            raw_actors = [match[1].strip() for match in matches]
            
            # Filter for actor-like classes (exclude technical classes)
            actor_patterns = [
                'user', 'admin', 'administrator', 'librarian', 'member', 'customer',
                'client', 'staff', 'employee', 'student', 'guest', 'operator',
                'leader', 'supplier', 'assistant'
            ]
            
            actors = []
            for actor in raw_actors:
                if actor and len(actor) > 1:
                    actor_lower = actor.lower()
                    # Include if it matches actor patterns OR is a capitalized entity
                    if (any(pattern in actor_lower for pattern in actor_patterns) or 
                        (actor[0].isupper() and actor.isalpha() and len(actor) <= 15)):
                        actors.append(actor)
            
            return list(set(actors))
        except Exception as e:
            print(f"Error extracting actors from class diagram: {str(e)}")
            return []

    def _extract_actors_from_sequence_diagram(self, sequence_diagram: str) -> List[str]:
        """
        Extract actors from sequence diagram participant declarations
        """
        try:
            import re
            # Patterns for extracting participants and actors
            patterns = [
                r'actor\s+([A-Za-z0-9_]+)',
                r'participant\s+([A-Za-z0-9_]+)',
                r'participant\s+"([^"]+)"\s+as\s+([A-Za-z0-9_]+)',
                r'actor\s+"([^"]+)"\s+as\s+([A-Za-z0-9_]+)'
            ]
            
            actors = []
            for pattern in patterns:
                matches = re.findall(pattern, sequence_diagram)
                for match in matches:
                    if isinstance(match, tuple):
                        actors.extend([m for m in match if m])
                    else:
                        actors.append(match)
            
            return list(set([actor for actor in actors if actor and len(actor) > 1]))
        except Exception as e:
            print(f"Error extracting actors from sequence diagram: {str(e)}")
            return []

    def _extract_all_classes_from_diagram(self, class_diagram: str) -> List[str]:
        """
        Extract ALL classes from the PlantUML class diagram
        """
        try:
            import re
            class_pattern = re.compile(r'(?:class|participant|actor)\s+("?)([A-Za-z0-9_ ]+)\1')
            matches = class_pattern.findall(class_diagram)
            return list(set([match[1].strip() for match in matches if match[1].strip()]))
        except Exception as e:
            print(f"Error extracting all classes: {str(e)}")
            return []

    def _is_incorrect_actor(self, actor_name: str) -> bool:
        """
        Check if an actor is technically incorrect (UI, system components, etc.)
        """
        actor_lower = actor_name.lower()
        incorrect_patterns = [
            'system', 'database', 'service', 'page', 'record', 'interface',
            'controller', 'handler', 'manager', 'api', 'factory', 'builder',
            'view', 'form', 'dialog', 'window', 'screen', 'panel', 'button',
            'home', 'login', 'details', 'validation', 'category'
        ]
        return any(pattern in actor_lower for pattern in incorrect_patterns)

    def _exists_in_requirements(self, actor_name: str, requirements_text: str) -> bool:
        """
        Check if an actor exists in the original requirements text
        """
        if not requirements_text or not actor_name:
            return False
        
        import re
        requirements_lower = requirements_text.lower()
        actor_lower = actor_name.lower()
        
        # Check for word boundary matches
        pattern = r'\b' + re.escape(actor_lower) + r'\b'
        return bool(re.search(pattern, requirements_lower))

    def _generate_recommendations(self, missing_actors: List[str], overspecified_classes: List[str], 
                                incorrect_classes: List[str], coverage_percentage: float) -> List[str]:
        """
        Generate specific recommendations based on verification results
        """
        recommendations = []
        
        if missing_actors:
            recommendations.append(f"Add missing actors to diagrams: {', '.join(missing_actors)}")
        
        if incorrect_classes:
            recommendations.append(f"Remove incorrect technical classes: {', '.join(incorrect_classes)}")
        
        if overspecified_classes:
            recommendations.append(f"Consider removing overspecified classes: {', '.join(overspecified_classes[:3])}")
        
        if coverage_percentage < 50:
            recommendations.append("Low actor coverage - regenerate diagrams with all identified actors")
        elif coverage_percentage < 80:
            recommendations.append("Good actor coverage - minor adjustments needed")
        else:
            recommendations.append("Excellent actor coverage - diagrams align well with requirements")
        
        return recommendations if recommendations else ["Diagrams are well-structured"]
