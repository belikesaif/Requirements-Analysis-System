"""
Simple test to verify actor identification fixes
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app.rupp_integration.enhanced_rupp_processor import EnhancedRUPPProcessor

def test_actor_identification():
    processor = EnhancedRUPPProcessor()
    
    test_text = """
    The Member clicks the log-in button. The system displays the page. 
    The book should be stored in database. The user selects books.
    The librarian checks the database. The administrator manages the system.
    """
    
    actors = processor.identify_actors_enhanced(test_text)
    print(f"Identified actors: {actors}")
    
    expected_actors = ['administrator', 'guest', 'librarian', 'member', 'system', 'user']
    unwanted_actors = ['book', 'books', 'database']
    
    print(f"Expected actors present: {[a for a in expected_actors if a in actors]}")
    print(f"Unwanted actors found: {[a for a in unwanted_actors if a in actors]}")
    
    # Test sentence extraction
    sentences = processor.extract_sentences_comprehensive(test_text)
    print(f"\nExtracted {len(sentences)} sentences:")
    for i, sent in enumerate(sentences[:5], 1):
        print(f"{i}. {sent}")

if __name__ == "__main__":
    test_actor_identification()
