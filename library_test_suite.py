"""
Comprehensive Test Suite for Library Management System RUPP Processing
Based on the provided case study and expected analysis
"""

import sys
import os
import requests
import json
from typing import Dict, Any, List

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

class LibraryManagementTestSuite:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.case_study_text = """
The Member clicks the log-in button on the Home Page. The system displays the log- in page. The member enters his login Id with password. The member clicks on the confirm button. The system checks that all of the required information was entered. If the entered information is wrong then system asks member to reenter the details. The system validates the entered information against the tables stored in the database. Member must be logged in to the system. The member clicks on View user details. The system opens a page showing the details of the member. The details include the total number of issued books, date of issue, return date, fine to be paid. The member closes the page. The system shows OK message. The books should be stored in database. The books must be ready to retrieve. The system asks user to login. The system identifies the type of user- member, guest or administrator. The system shows the categories to browse. The user selects a category of books to view. If no category is selected by the user then the system again asks user to select a category. The system checks the books in the database. The system retrieves all the books falling in that category. The user selects the desired books. The system shows the details of the selected books. The system asks user to print the details. If User does not want to print the details then user can ignore the step. User can reserve a book by inputting the relevant details & the librarian can also reserve a book for a member. User should be logged into the system. User should have correct book Id. Books should be available to reserve. The system asks user to login. The system identifies the type of user- member, guest or administrator. The system shows the categories to browse. The user selects book to reserve. If no book is selected by the user then the system again asks user to select a book to reserve. The user enters Book Id to reserve. If the book Id is wrong then system asks user to recheck the book id. The system checks the books in the database. If the selected book is already reserved on another Id then system asks user to select another book. Members should be logged into the system. Guest user can also search books. Book should be available to search. The system shows the categories to browse. The member selects a category of searching a book. If no category is selected by the member then the system again asks user to select a category. The system checks the books in the database. The system retrieves all the books falling in that category. Member should give the member Id to the librarian. Books should be available to issue. The librarian Checks the availability of the books. The librarian also checks total number of books issued on that Id. Librarian issues the book. The librarian cannot issue the books if the user has three books issued on his Id. The system updates the information in database. Librarian should be logged into the system. Member should have borrowed books. Member should give the member Id to the librarian. The member returns the book. The librarian enters book id , member id in the system. If the entered book id is incorrect then system asks to re-enter the book id. The system prompts a message that the book with book id is successfully returned. Members should be stored in the database. Members should be available to retrieve by the system. Member must be logged in to the system. Guest can also view members. The user clicks on View members. The system opens a page showing the details of the member. The details include name of member, the total number of issued books, date of issue, return date, fine to be paid. The member closes the page. Librarian should be logged into the system. Books should be available to remove. Book details should be available to add or remove books in the database. The librarian has option of adding or removing a book in database. The system asks librarian to add or remove the book. The librarian adds a book. The system asks librarian to enter all the required details about the new book to be added. The librarian enters the details. If the librarian selects to remove a book then the book should be outdated. The system administrator that all the information has been correctly provided. Administrator should be logged into the system. Member should be available to remove. Member details should be available to add or remove member in the database. The system asks administrator to add or remove a member. The administrator selects to add a member. The system asks administrator to enter all the required details about the new member to be added. The administrator enters the details. If the administrator selects to remove a member then a valid reason of removal is required. The system validates that all the information has been correctly provided.
"""
        
        # Expected results based on analysis
        self.expected_actors = ["member", "system", "user", "librarian", "administrator", "guest"]
        self.expected_min_requirements = 89 # Should generate close to 89 requirements
        self.expected_functional_areas = [
            "authentication", "login", "database", "book", "reserve", "issue", "return", "search", "browse"
        ]

    def test_backend_health(self):
        """Test if backend is running and responding"""
        try:
            response = requests.get(f"{self.backend_url}/")
            if response.status_code == 200:
                print("✅ Backend health check passed")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False

    def test_rupp_processing(self):
        """Test RUPP processing with the library management case study"""
        try:
            payload = {
                "text": self.case_study_text,
                "title": "Library Management System Test"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/process-requirements",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                print(f"❌ RUPP processing failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None
            
            result = response.json()
            return result
            
        except Exception as e:
            print(f"❌ RUPP processing exception: {e}")
            return None

    def analyze_actor_identification(self, result):
        """Analyze if correct actors were identified"""
        print("\n=== ACTOR IDENTIFICATION ANALYSIS ===")
        
        rupp_data = result.get('rupp_snl', {})
        identified_actors = rupp_data.get('actors', [])
        
        print(f"Identified Actors: {identified_actors}")
        print(f"Expected Actors: {self.expected_actors}")
        
        # Check for critical actors
        critical_actors = ["member", "system", "librarian", "administrator"]
        missing_critical = [actor for actor in critical_actors if actor not in identified_actors]
        found_critical = [actor for actor in critical_actors if actor in identified_actors]
        
        print(f"✅ Found Critical Actors: {found_critical}")
        if missing_critical:
            print(f"❌ Missing Critical Actors: {missing_critical}")
        
        # Check for unexpected actors
        extra_actors = [actor for actor in identified_actors if actor not in self.expected_actors]
        if extra_actors:
            print(f"⚠️ Additional Actors Found: {extra_actors}")
        
        score = len(found_critical) / len(critical_actors) * 100
        print(f"Actor Identification Score: {score:.1f}%")
        
        return {
            'identified_actors': identified_actors,
            'found_critical': found_critical,
            'missing_critical': missing_critical,
            'extra_actors': extra_actors,
            'score': score
        }

    def analyze_requirements_generation(self, result):
        """Analyze the number and quality of generated requirements"""
        print("\n=== REQUIREMENTS GENERATION ANALYSIS ===")
        
        rupp_data = result.get('rupp_snl', {})
        requirements = rupp_data.get('requirements', [])
        sentences_count = rupp_data.get('sentences_count', 0)
        
        print(f"Generated Requirements Count: {len(requirements)}")
        print(f"Expected Minimum: {self.expected_min_requirements}")
        print(f"Sentences Count: {sentences_count}")
        
        # Check if we're generating enough requirements
        generation_ratio = len(requirements) / self.expected_min_requirements * 100
        print(f"Generation Ratio: {generation_ratio:.1f}%")
        
        # Analyze requirement quality
        quality_score = self.analyze_requirement_quality(requirements)
        
        # Check for functional area coverage
        coverage_score = self.analyze_functional_coverage(requirements)
        
        return {
            'requirements_count': len(requirements),
            'generation_ratio': generation_ratio,
            'quality_score': quality_score,
            'coverage_score': coverage_score,
            'requirements': requirements[:10]  # First 10 for inspection
        }

    def analyze_requirement_quality(self, requirements):
        """Analyze the quality of generated requirements"""
        print("\n--- Requirement Quality Analysis ---")
        
        quality_metrics = {
            'has_shall': 0,
            'proper_format': 0,
            'sufficient_length': 0,
            'contains_actor': 0,
            'contains_action': 0
        }
        
        action_words = ['provide', 'display', 'validate', 'check', 'store', 'retrieve', 'update', 'process']
        actor_words = ['system', 'member', 'user', 'librarian', 'administrator', 'guest']
        
        for req in requirements:
            req_lower = req.lower()
            
            # Check if contains "shall"
            if 'shall' in req_lower:
                quality_metrics['has_shall'] += 1
            
            # Check proper format (starts with "The system" or similar)
            if req_lower.startswith('the system') or req_lower.startswith('if'):
                quality_metrics['proper_format'] += 1
            
            # Check sufficient length
            if len(req) > 20:
                quality_metrics['sufficient_length'] += 1
            
            # Check contains actor
            if any(actor in req_lower for actor in actor_words):
                quality_metrics['contains_actor'] += 1
            
            # Check contains action
            if any(action in req_lower for action in action_words):
                quality_metrics['contains_action'] += 1
        
        total_requirements = len(requirements)
        if total_requirements > 0:
            quality_percentages = {k: (v / total_requirements) * 100 for k, v in quality_metrics.items()}
            
            print(f"Requirements with 'shall': {quality_percentages['has_shall']:.1f}%")
            print(f"Proper format: {quality_percentages['proper_format']:.1f}%")
            print(f"Sufficient length: {quality_percentages['sufficient_length']:.1f}%")
            print(f"Contains actor: {quality_percentages['contains_actor']:.1f}%")
            print(f"Contains action: {quality_percentages['contains_action']:.1f}%")
            
            overall_quality = sum(quality_percentages.values()) / len(quality_percentages)
            print(f"Overall Quality Score: {overall_quality:.1f}%")
            
            return overall_quality
        
        return 0

    def analyze_functional_coverage(self, requirements):
        """Analyze coverage of functional areas"""
        print("\n--- Functional Coverage Analysis ---")
        
        covered_areas = []
        requirements_text = ' '.join(requirements).lower()
        
        for area in self.expected_functional_areas:
            if area in requirements_text:
                covered_areas.append(area)
        
        coverage_ratio = len(covered_areas) / len(self.expected_functional_areas) * 100
        
        print(f"Covered Functional Areas: {covered_areas}")
        print(f"Missing Areas: {[area for area in self.expected_functional_areas if area not in covered_areas]}")
        print(f"Functional Coverage: {coverage_ratio:.1f}%")
        
        return coverage_ratio

    def test_statistics_dashboard_data(self, result):
        """Test if statistics dashboard receives proper data"""
        print("\n=== STATISTICS DASHBOARD DATA ANALYSIS ===")
        
        comparison_data = result.get('comparison', {})
        rupp_metrics = comparison_data.get('rupp_metrics', {})
        ai_metrics = comparison_data.get('ai_metrics', {})
        
        print("RUPP Metrics:")
        for key, value in rupp_metrics.items():
            print(f"  {key}: {value}")
        
        print("AI Metrics:")
        for key, value in ai_metrics.items():
            print(f"  {key}: {value}")
        
        # Check if essential metrics are present
        essential_metrics = ['processing_time', 'requirements_count', 'actors_detected', 'accuracy_score']
        missing_rupp_metrics = [metric for metric in essential_metrics if metric not in rupp_metrics]
        missing_ai_metrics = [metric for metric in essential_metrics if metric not in ai_metrics]
        
        if missing_rupp_metrics:
            print(f"❌ Missing RUPP metrics: {missing_rupp_metrics}")
        if missing_ai_metrics:
            print(f"❌ Missing AI metrics: {missing_ai_metrics}")
        
        if not missing_rupp_metrics and not missing_ai_metrics:
            print("✅ All essential metrics present")
        
        return {
            'rupp_metrics': rupp_metrics,
            'ai_metrics': ai_metrics,
            'missing_rupp_metrics': missing_rupp_metrics,
            'missing_ai_metrics': missing_ai_metrics
        }

    def print_sample_requirements(self, requirements, count=15):
        """Print sample requirements for manual inspection"""
        print(f"\n=== SAMPLE GENERATED REQUIREMENTS (First {count}) ===")
        
        for i, req in enumerate(requirements[:count], 1):
            print(f"{i:2d}. {req}")

    def run_comprehensive_test(self):
        """Run all tests and provide comprehensive analysis"""
        print("🚀 STARTING COMPREHENSIVE LIBRARY MANAGEMENT SYSTEM TEST")
        print("=" * 80)
        
        # Test 1: Backend Health
        if not self.test_backend_health():
            print("❌ Cannot proceed - Backend not available")
            return
        
        # Test 2: Process requirements
        print("\n🔄 Processing case study through RUPP...")
        result = self.test_rupp_processing()
        
        if not result:
            print("❌ Cannot proceed - RUPP processing failed")
            return
        
        # Test 3: Analyze results
        actor_analysis = self.analyze_actor_identification(result)
        requirements_analysis = self.analyze_requirements_generation(result)
        dashboard_analysis = self.test_statistics_dashboard_data(result)
        
        # Test 4: Print samples for manual inspection
        rupp_requirements = result.get('rupp_snl', {}).get('requirements', [])
        self.print_sample_requirements(rupp_requirements)
        
        # Test 5: Overall assessment
        self.provide_overall_assessment(actor_analysis, requirements_analysis, dashboard_analysis)
        
        return result

    def provide_overall_assessment(self, actor_analysis, requirements_analysis, dashboard_analysis):
        """Provide overall assessment of system performance"""
        print("\n" + "=" * 80)
        print("📊 OVERALL ASSESSMENT")
        print("=" * 80)
        
        # Calculate overall score
        actor_score = actor_analysis['score']
        generation_score = min(requirements_analysis['generation_ratio'], 100)
        quality_score = requirements_analysis['quality_score']
        coverage_score = requirements_analysis['coverage_score']
        
        overall_score = (actor_score + generation_score + quality_score + coverage_score) / 4
        
        print(f"Actor Identification Score: {actor_score:.1f}%")
        print(f"Requirements Generation Score: {generation_score:.1f}%")
        print(f"Requirements Quality Score: {quality_score:.1f}%")
        print(f"Functional Coverage Score: {coverage_score:.1f}%")
        print(f"Overall System Score: {overall_score:.1f}%")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        
        if actor_score < 80:
            print("• Improve actor identification algorithm")
            print("• Add more comprehensive actor recognition patterns")
        
        if generation_score < 80:
            print("• Enhance sentence parsing to capture more requirements")
            print("• Improve template matching for complex sentence structures")
        
        if quality_score < 80:
            print("• Improve requirement formatting and structure")
            print("• Add more sophisticated natural language processing")
        
        if coverage_score < 80:
            print("• Ensure all functional areas are covered in template generation")
            print("• Add specialized templates for domain-specific requirements")
        
        # Success criteria
        if overall_score >= 85:
            print("\n✅ EXCELLENT: System performance meets high standards")
        elif overall_score >= 70:
            print("\n✅ GOOD: System performance is acceptable with room for improvement")
        elif overall_score >= 60:
            print("\n⚠️ FAIR: System needs significant improvements")
        else:
            print("\n❌ POOR: System requires major redesign")

if __name__ == "__main__":
    # Run the comprehensive test suite
    test_suite = LibraryManagementTestSuite()
    result = test_suite.run_comprehensive_test()
