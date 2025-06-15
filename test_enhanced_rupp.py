"""
Test script to verify the enhanced RUPP processor
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from app.rupp_integration.enhanced_rupp_processor import EnhancedRUPPProcessor
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    # Fallback to simple processor
    from app.rupp_integration.simple_rupp_processor import SimpleRUPPProcessor as EnhancedRUPPProcessor

def test_enhanced_rupp():
    # Sample case study with multiple requirements
    case_study = """
    The Member clicks the log-in button on the Home Page. The system displays the log- in page. The member enters his login Id with password. The member clicks on the confirm button. The system checks that all of the required information was entered. If the entered information is wrong then system asks member to reenter the details. The system validates the entered information against the tables stored in the database. Member must be logged in to the system. The member clicks on View user details. The system opens a page showing the details of the member. The details include the total number of issued books, date of issue, return date, fine to be paid. The member closes the page. The system shows OK message. The books should be stored in database. The books must be ready to retrieve. The system asks user to login. The system identifies the type of user- member, guest or administrator. The system shows the categories to browse. The user selects a category of books to view. If no category is selected by the user then the system again asks user to select a category. The system checks the books in the database. The system retrieves all the books falling in that category. The user selects the desired books. The system shows the details of the selected books. The system asks user to print the details. If User does not want to print the details then user can ignore the step. User can reserve a book by inputting the relevant details & the librarian can also reserve a book for a member. User should be logged into the system. User should have correct book Id. Books should be available to reserve. The system asks user to login. The system identifies the type of user- member, guest or administrator. The system shows the categories to browse. The user selects book to reserve. If no book is selected by the user then the system again asks user to select a book to reserve. The user enters Book Id to reserve. If the book Id is wrong then system asks user to recheck the book id. The system checks the books in the database. If the selected book is already reserved on another Id then system asks user to select another book. Members should be logged into the system. Guest user can also search books. Book should be available to search. The system shows the categories to browse. The member selects a category of searching a book. If no category is selected by the member then the system again asks user to select a category. The system checks the books in the database. The system retrieves all the books falling in that category. Member should give the member Id to the librarian. Books should be available to issue. The librarian Checks the availability of the books. The librarian also checks total number of books issued on that Id. Librarian issues the book. The librarian cannot issue the books if the user has three books issued on his Id. The system updates the information in database. Librarian should be logged into the system. Member should have borrowed books. Member should give the member Id to the librarian. The member returns the book. The librarian enters book id , member id in the system. If the entered book id is incorrect then system asks to re-enter the book id. The system prompts a message that the book with book id is successfully returned. Members should be stored in the database. Members should be available to retrieve by the system. Member must be logged in to the system. Guest can also view members. The user clicks on View members. The system opens a page showing the details of the member. The details include name of member, the total number of issued books, date of issue, return date, fine to be paid. The member closes the page. Librarian should be logged into the system. Books should be available to remove. Book details should be
 
    available to add or remove books in the database. The librarian has option of adding or removing a book in database. The system asks librarian to add or remove the book. The librarian adds a book. The system asks librarian to enter all the required details about the new book to be added. The librarian enters the details. If the librarian selects to remove a book then the book should be outdated. The system administrator that all the information has been correctly provided. Administrator should be logged into the system. Member should be available to remove. Member details should be available to add or remove member in the database. The system asks administrator to add or remove a member. The administrator selects to add a member. The system asks administrator to enter all the required details about the new member to be added. The administrator enters the details. If the administrator selects to remove a member then a valid reason of removal is required. The system validates that all the information has been correctly provided.

    """
    
    processor = EnhancedRUPPProcessor()
    result = processor.generate_snl(case_study)
    
    print("=== Enhanced RUPP Processing Results ===")
    print(f"Original text length: {len(case_study)} characters")
    print(f"Preprocessing result length: {len(result['preprocessed_text'])} characters")
    print(f"Actors identified: {result['actors']}")
    print(f"Number of requirements generated: {result['sentences_count']}")
    print(f"Original sentences processed: {result.get('original_sentences_processed', 'N/A')}")
    
    if 'processing_stats' in result:
        stats = result['processing_stats']
        print(f"\nProcessing Statistics:")
        print(f"- Input sentences: {stats['total_input_sentences']}")
        print(f"- Requirements generated: {stats['requirements_generated']}")
        print(f"- Unique requirements: {stats['unique_requirements']}")
        print(f"- Actors identified: {stats['actors_identified']}")
    
    print(f"\n=== Generated Requirements ===")
    for i, req in enumerate(result['requirements'], 1):
        print(f"{i}. {req}")
    
    print(f"\n=== Formatted SNL ===")
    print(result['formatted_sentences'])
    
    return result

if __name__ == "__main__":
    test_enhanced_rupp()
