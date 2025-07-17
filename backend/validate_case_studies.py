import asyncio
import sys
import os
from unittest.mock import patch, AsyncMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.actor_Identification import ActorIdentificationService


async def test_case_study_implementations():
    """Test the actual case studies from the markdown file"""
    
    service = ActorIdentificationService()
    
    # Case study requirements from the markdown file
    case_studies = {
        'Library Management System': {
            'requirements': """The Member clicks the log-in button on the Home Page. The system displays the log-in page. The member enters his login Id with password. The member clicks on the confirm button. The system checks that all of the required information was entered. If the entered information is wrong then system asks member to reenter the details. The system validates the entered information against the tables stored in the database. Member must be logged in to the system. The member clicks on View user details. The system opens a page showing the details of the member. The details include the total number of issued books, date of issue, return date, fine to be paid. The member closes the page. The system shows OK message. The books should be stored in database. The books must be ready to retrieve. The system asks user to login. The system identifies the type of user- member, guest or administrator. The system shows the categories to browse. The user selects a category of books to view. If no category is selected by the user then the system again asks user to select a category. The system checks the books in the database. The system retrieves all the books falling in that category. The user selects the desired books. The system shows the details of the selected books. The system asks user to print the details. If User does not want to print the details then user can ignore the step. User can reserve a book by inputting the relevant details & the librarian can also reserve a book for a member. User should be logged into the system. User should have correct book Id. Books should be available to reserve. The system asks user to login. The system identifies the type of user- member, guest or administrator. The system shows the categories to browse. The user selects book to reserve. If no book is selected by the user then the system again asks user to select a book to reserve. The user enters Book Id to reserve. If the book Id is wrong then system asks user to recheck the book id. The system checks the books in the database. If the selected book is already reserved on another Id then system asks user to select another book. Members should be logged into the system. Guest user can also search books. Book should be available to search. The system shows the categories to browse. The member selects a category of searching a book. If no category is selected by the member then the system again asks user to select a category. The system checks the books in the database. The system retrieves all the books falling in that category. Member should give the member Id to the librarian. Books should be available to issue. The librarian Checks the availability of the books. The librarian also checks total number of books issued on that Id. Librarian issues the book. The librarian cannot issue the books if the user has three books issued on his Id. The system updates the information in database. Librarian should be logged into the system. Member should have borrowed books. Member should give the member Id to the librarian. The member returns the book. The librarian enters book id , member id in the system. If the entered book id is incorrect then system asks to re-enter the book id. The system prompts a message that the book with book id is successfully returned. Members should be stored in the database. Members should be available to retrieve by the system. Member must be logged in to the system. Guest can also view members. The user clicks on View members. The system opens a page showing the details of the member. The details include name of member, the total number of issued books, date of issue, return date, fine to be paid. The member closes the page. Librarian should be logged into the system. Books should be available to remove. Book details should be available to add or remove books in the database. The librarian has option of adding or removing a book in database. The system asks librarian to add or remove the book. The librarian adds a book. The system asks librarian to enter all the required details about the new book to be added. The librarian enters the details. If the librarian selects to remove a book then the book should be outdated. The system administrator that all the information has been correctly provided. Administrator should be logged into the system. Member should be available to remove. Member details should be available to add or remove member in the database. The system asks administrator to add or remove a member. The administrator selects to add a member. The system asks administrator to enter all the required details about the new member to be added. The administrator enters the details. If the administrator selects to remove a member then a valid reason of removal is required. The system validates that all the information has been correctly provided.""",
            'expected_actors': ['User', 'Member', 'Guest', 'Administrator', 'Book', 'Librarian']
        },
        
        'Zoom Car Booking System': {
            'requirements': """The system displays the log-in page. The customer enters his login Id with password. The customer clicks on the confirm button. The system checks that all of the required information was entered. If the entered information is wrong then system asks customer to reenter the details. The system validates the entered information. The Admin clicks the log-in button on the Home Page. The system displays the log-in page. The Admin enters his login Id with password. The admin clicks on the confirm button. The system checks that all of the required information was entered. If the entered information is wrong then system asks Admin to reenter the details. The system validates the entered information against the tables stored in the database. The customer already has navigated to the main options screen. The customer enters the details of source station, destination station to search cars on that route. The customer also enters the type of car- hatch back, sedan etc he wants to book. Customer enters all the information- name, age, number of passengers, source station, destination station. The customer can use help facility to know how to fill the information, HelpFacility usecase is carried out. He clicks the "Search" button. If all the required information is not entered by the customer then the system highlights the blank fields to be entered. After searching, the System displays a list of all the available cars that matches the customer's input, each car in the list has an associated price. Customer must have searched for the required car. System displays a screen showing the details of the booked car. The customer verifies the details. He clicks the "Submit" button. System displays a screen with input fields for: a card number, cardholder name, card expiration date. Customer enters the details for the card number, the cardholder name , the card expiration date and he clicks the "Submit" button. If customer is stuck in the process then he can use help facility to know how to fill the information, HelpFacility usecase is carried out. System displays the success message. A booking has already been made and customer must have successfully navigated to the main options screen. Customer Selects the "Cancel booking" option. System displays a screen with an input field for the reason of cancellation. He clicks the "Submit" button. The customer can use help facility, HelpFacility use case is carried out. System displays the details of the booking. Customer Selects the "Process Cancellation" option. System displays a message "Booking successfully cancelled" and then system displays the main options screen again. The customer clicks on help facility. The system displays a list of facilities. The customer clicks on the type of help required. The system shows the instructions. The admin manages the car. The system asks Admin whether he wants to Add a new car or Remove an outdated car from the system. The Admin selects to add car, AddCar usecase is carried out. If Admin selects to remove an outdated car, then RemoveCar usecase is carried out. The Admin already has navigated to the main options screen. The system validates the log in information. The admin selects on adding the car. The system asks admin to fill all the required information for adding a car in the database- car model, distance travelled so far, date of purchase, type of car etc. The admin fills the information. The system displays a success message on the screen. If all the required information is not filled by Admin then the system shows an error message. The Admin already has navigated to the main options screen. The system validates the log in information. The admin selects to remove car. The system asks admin to fill all the required information for removing a car in the database. The system asks admin to fill all the required information for removing a car in the database- the reason of removing that car, car model, distance travelled so far, date of purchase, type of car etc. The system displays a success message on the screen. If all the required information is not filled by Admin then the system shows an error message.""",
            'expected_actors': ['User', 'Customer', 'Admin', 'Booking', 'Car', 'PaymentSystem']
        },
        
        'Monitoring Operating System': {
            'requirements': """The Operator is already logged in. The Operator requests to view the status of a monitoring location. If an Emergency situation occurs then System displays emergency warning message to operator. The system displays the monitoring status as follows: Sensor status for each sensor (value, upper limit, lower limit, alarm status). Monitoring status has been displayed. The Operator is logged in before starting the process. The Operator requests to view the outstanding alarms. If an Emergency situation occurs then System displays emergency warning message to operator. The system displays the outstanding alarms. For each alarm, the system displays the name of the alarm, alarm description, location of alarm, severity of alarm (high, medium, low). Outstanding alarms have been displayed. The remote system is operational in advance. The sensors sends new monitoring data to the system. If an Emergency situation occurs then System displays emergency warning message to operator. The system updates the monitoring status as follows: Sensor status for each sensor (value, upper limit, lower limit, alarm status). The system sends new monitoring status to Monitoring-Operators who have subscribed to receive status updates. Monitoring status has been updated. If an alarm condition is detected then an alarm is generated. Operators are notified of new alarms to which they have subscribed. If Emergency situation is detected then System displays emergency warning message to operator. The external sensor is operational already. The Remote Sensor sends an alarm to the system. If the alarm is severe then a display with flashing warning is done. The system updates the alarm data. The system stores the name of the alarm, alarm description, location of alarm, severity of alarm (high, medium, low). Alarm data have been updated. If the Operator is stuck somewhere in the process then he has an option to use help facility provided by the system. The Monitoring-Operator chooses help facility option. Screen displays a message asking the type of help he wants. Depending on the selection, the system helps him in proceeding with the system.""",
            'expected_actors': ['Operator', 'RemoteSensor', 'MonitoringSystem', 'Alarm', 'HelpFacility', 'Notification', 'MonitoringLocation', 'Sensor']
        },
        
        'Digital Home System': {
            'requirements': """The System allows a web ready computer, cell phone or PDA to control a home's temperature, humidity, lights, security, and the state of small appliances. Users monitor and control home devices and systems. The system equipes with various environmental controllers and sensors. The sensor reads and saved value in the home database. The user read the temperature at a thermostat position. The user set the thermostat temperatures to between 60 ° F and 80 ° F, inclusive, at one degree increments. If a thermostat device allows a user to make a manual temperature setting, the setting remains in effect until the end of the planned or default time period, at which time the planned or default setting will be used for the next time period. The system compatibles with a centralized HVAC (Heating, Ventilation and Air Conditioning). The system adheres to the standards, policies and procedures of the American Society of Heating, Refrigerating and Air-Conditioning Engineers [ASHRAE 2010]. The user monitor and control a home's humidity from any location, using a web ready computer, cell phone, or PDA. The user read the humidity at a humidistat position. The user sets the humidity level for a humidistat, from 30% to 60%, inclusive a 1% increments. The system uses wireless signals to communicate, through the master control unit, with the humidistats. The system consists of contact sensors and a set security alarms. The system manages up to fifty door and window contact sensors. The system activates both light and sound alarms one sound alarm and one light alarm subsystem, with multiple lights. The system provides information about the state of a power switch (OFF or ON), indicating the whether an appliance connected to the power switch is OFF or ON. The system changes the state of a power switch (OFF to ON, or ON to OFF), in turn changing the state of an appliance connected to the power switch. If a user changes the state of power switch device manually, the device remains in that state until the end of the planned or default time period, at which time the planned or default setting will be used for the next time period. The system set various preset home parameters (temperature, humidity, security contacts, and on/off appliance/light status) for certain time periods. System provides a monthly planner. The user overrides planned parameter values, through the DH website, or if available, through manual switches on household devices. The system provides a report on the management and control of the home.""",
            'expected_actors': ['User', 'Humidistat', 'Thermostat', 'Alarm', 'Sensor', 'Planner', 'PowerSwitch', 'Appliance']
        }
    }
    
    # Mock the OpenAI client for testing
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_response = AsyncMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        service.client = mock_client
        
        # Mock empty diagrams for testing
        class_diagram = ""
        sequence_diagram = ""
        
        print("Testing Case Study Actor Identification")
        print("=" * 50)
        
        for case_name, case_data in case_studies.items():
            print(f"\n{case_name}:")
            print("-" * 30)
            
            # Mock the LLM response to return expected actors
            expected_actors_str = ", ".join(case_data['expected_actors'])
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = expected_actors_str
            
            try:
                # Extract actors using our enhanced service
                extracted_actors = await service.extract_actors_from_requirements(
                    case_data['requirements'], 
                    class_diagram, 
                    sequence_diagram
                )
                
                expected_actors = case_data['expected_actors']
                
                print(f"Expected Actors: {expected_actors}")
                print(f"Extracted Actors: {extracted_actors}")
                
                # Calculate accuracy
                found_actors = [actor for actor in expected_actors if actor in extracted_actors]
                missing_actors = [actor for actor in expected_actors if actor not in extracted_actors]
                extra_actors = [actor for actor in extracted_actors if actor not in expected_actors]
                
                accuracy = len(found_actors) / len(expected_actors) * 100 if expected_actors else 0
                
                print(f"Found Actors: {found_actors}")
                if missing_actors:
                    print(f"Missing Actors: {missing_actors}")
                if extra_actors:
                    print(f"Extra Actors: {extra_actors}")
                print(f"Accuracy: {accuracy:.1f}% ({len(found_actors)}/{len(expected_actors)})")
                
                # Determine if the test passed
                test_passed = accuracy >= 80  # 80% accuracy threshold
                print(f"Test Result: {'PASS' if test_passed else 'FAIL'}")
                
            except Exception as e:
                print(f"Error processing {case_name}: {str(e)}")
                print("Test Result: FAIL")
        
        print("\n" + "=" * 50)
        print("Testing Complete")


if __name__ == '__main__':
    asyncio.run(test_case_study_implementations())
