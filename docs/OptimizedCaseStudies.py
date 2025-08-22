LMS_Class_Diagram = """
@startuml
class User {
  -userId: string
  -password: string
  -name: string
  +login()
  +logout()
  +viewDetails()
  +validateCredentials()
  +identifyUserType(): string
}

class Administrator {
  -adminId: string
  +addMember(member: Member)
  +removeMember(memberId: string, reason: string)
  +manageMemberDetails(memberId: string)
}

class Guest {
  +searchBooks(category: string)
  +viewMembers()
}

class Librarian {
  -employeeId: string
  +issueBook(memberId: string, bookId: string)
  +returnBook(memberId: string, bookId: string)
  +addBook(book: Book)
  +removeBook(bookId: string)
  +checkBookAvailability(bookId: string)
  +checkTotalIssuedBooks(memberId: string)
}

class Member {
  -totalIssuedBooks: int
  -dateOfIssue: Date
  -returnDate: Date
  -fineToBePaid: float
  +reservesBook(bookId: string)
  +searchBooks(category: string)
  +returnBook(bookId: string)
  +viewUserDetails()
}

class Book {
  -bookId: string
  -title: string
  -category: string
  -isAvailable: boolean
  +checkAvailability(): boolean
  +retrieveDetails(): string
  +reserve(memberId: string)
  +cancelReservation(memberId: string)
  +searchByCategory(category: string)
  +searchByBookId(bookId: string)
  +filterBooks(criteria: string)
}

User <|-- Administrator
User <|-- Guest
User <|-- Librarian
User <|-- Member

Administrator "1" --> "0..*" Member : manages
Librarian "1" --> "0..*" Book : manages
Member "0..*" --> "1" Book : reserves/returns

@enduml
"""

LMS_Sequnce_Diagram = """
@startuml
actor User
participant Member
participant Guest
participant Librarian
participant Administrator
participant Book

== User Login ==
User -> User: login()
activate User
User -> User: validateCredentials()
alt success
  User -> User: identifyUserType()
  User --> User: login success
else login failure
  User --> User: login failure
end
deactivate User

== View User Details ==
User -> Member: viewUserDetails()
activate Member
Member -> Member: retrieve details (totalIssuedBooks, dateOfIssue, returnDate, fineToBePaid)
Member --> User: display details
deactivate Member

== Book Search by Member or Guest ==
alt Member
  Member -> Book: searchByCategory(category)
  activate Book
  Book -> Book: filterBooks(criteria)
  Book --> Member: return books list
  deactivate Book
else Guest
  Guest -> Book: searchByCategory(category)
  activate Book
  Book -> Book: filterBooks(criteria)
  Book --> Guest: return books list
  deactivate Book
end

== Book Reservation by Member ==
Member -> Book: checkAvailability(bookId)
activate Book
alt Book available
  Book --> Member: (Book available)
  Member -> Book: reserve(memberId)
  Book --> Member: reservation confirmed
else Book not available
  Book --> Member: (Not available)
  Book --> Member: reservation failed
end
deactivate Book

== Book Issue by Librarian ==
Librarian -> Book: checkAvailability(bookId)
activate Book
alt Can be issued
  Book --> Librarian: (Can be issued)
  Librarian -> Librarian: checkTotalIssuedBooks(memberId)
  alt Limit reached
    Librarian --> Librarian: Issue denied
  else
    Librarian -> Book: issueBook(memberId, bookId)
    Book -> Book: updateBookStatus(issued)
  end
else
  Book --> Librarian: (Not available)
end
deactivate Book

== Book Return by Librarian ==
Librarian -> Book: validateReturn(bookId)
activate Book
alt Valid return
  Book --> Librarian: (Valid return)
  Librarian -> Book: updateBookStatus(available)
  Book --> Librarian: return success
else Invalid return
  Book --> Librarian: (Invalid return)
  Book --> Librarian: return failure
end
deactivate Book

== Book Management by Librarian ==
Librarian -> Book: addBook(bookDetails)
activate Book
deactivate Book
Librarian -> Book: removeBook(bookId)
activate Book
deactivate Book

== Member Management by Administrator ==
Administrator -> Administrator: addMember(memberDetails)
activate Administrator
deactivate Administrator
Administrator -> Administrator: removeMember(memberId, reason)
activate Administrator
deactivate Administrator
@enduml
"""

DH_Class_Diagram = """
@startuml
class User {
  -userID : String
  -device : String
  +readTemperature(position : String) : int
  +setTemperature(value : int) : void
  +readHumidity(position : String) : int
  +setHumidity(value : int) : void
  +overrideParameters(parameter : String, value : Any) : void
}

class Humidistat {
  -currentHumidity : int
  -plannedHumidity : int
  -manualHumidity : int
  +setHumidity(value : int) : void
  +getHumidity() : int
  +rejectToPlanned() : void
}

class Thermostat {
  -currentTemperature : int
  -plannedTemperature : int
  -manualTemperature : int
  +setTemperature(value : int) : void
  +getTemperature() : int
  +rejectToPlanned() : void
}

class Alarm {
  -type : String <<light or sound>>
  -status : String
  +activate() : void
  +deactivate() : void
}

class Appliance {
  -applianceID : String
  -applianceName : String
  +getState() : String
  +changeState(state : String) : void
}

class PowerSwitch {
  -switchState : String
  -plannedState : String
  +getState() : String
  +setState(state : String) : void
  +resetToPlanned() : void
}

class Sensor {
  -sensorID : String
  -sensorType : String
  -savedValue : Any
  +readValue() : Any
  +saveValueToDatabase() : void
}

class Planner {
  -presetParameters : Map<String, Any>
  +setParameters(parameters : Map<String, Any>) : void
  +getParameters() : Map<String, Any>
  +generateMonthlyReport() : void
}

User "1" -- "1" Humidistat : sets humidity
User "1" -- "1" Thermostat : sets temperature
User "1" -- "1" Alarm : activates
User "1" -- "1" Appliance : monitors/controls

Humidistat "1" -- "1" Sensor : reads humidity from
Thermostat "1" -- "1" Sensor : reads temperature from
Sensor "1" -- "1" Alarm : triggered by
Appliance "1" -- "1" PowerSwitch : toggles
PowerSwitch "1" -- "1" Appliance : connected to

Humidistat "1" -- "1" Planner : overrides plan
Thermostat "1" -- "1" Planner : monitors
Sensor "1" -- "1" Planner : logs data to
PowerSwitch "1" -- "1" Planner : resets according to

Sensor "1" -- "1" Humidistat : follows
Sensor "1" -- "1" Thermostat : follows

@enduml
"""

DH_Sequnce_Diagram = """
@startuml
actor User
participant Thermostat
participant Humidistat
participant Sensor
participant Alarm
participant Appliance
participant PowerSwitch
participant Planner

== Temperature Control ==
User -> Thermostat: getTemperature()
Thermostat --> User: return temperature
User -> Thermostat: setTemperature(value)
Thermostat -> Planner: log planned temperature

== Humidity Control ==
User -> Humidistat: getHumidity()
Humidistat --> User: return humidity
User -> Humidistat: setHumidity(value)
Humidistat -> Planner: log planned humidity

== Sensor Interaction ==
Sensor -> Sensor: readValue()
Sensor -> Sensor: saveValueToDatabase()

== Alarm Management ==
Alarm -> Alarm: trigger()
Alarm --> User: notify with light/sound

== Appliance Control ==
User -> Appliance: getState()
Appliance --> User: return state
User -> Appliance: setState('ON'/'OFF')
Appliance -> PowerSwitch: update power state
PowerSwitch -> Planner: log state change

== Planning and Reporting ==
User -> Planner: setParameters()
Planner --> User: confirm set
User -> Planner: generateMonthlyReport()
Planner --> User: report details
@enduml
"""

ZOOM_Class_Diagram = """
@startuml
class User {
  -userId: string
  -loginId: string
  -password: string
  +login()
  +logout()
}

class Customer {
  -name: string
  -age: int
  -numberOfPassengers: int
  +searchCars(sourceStation: string, destinationStation: string, carType: string) : List<Car>
  +bookCar(car: Car)
  +cancelBooking(bookingId: string)
  +requestHelp(topic: string)
}

class Admin {
  -adminId: string
  +addCar(carModel: string, distanceTravelled: float, dateOfPurchase: Date, carType: string)
  +removeCar(carId: string, reason: string)
  +manageCars()
  +requestHelp(topic: string)
}

class Booking {
  -bookingId: string
  -customerId: string
  -carId: string
  -bookingDate: Date
  -status: string
  +createBooking()
  +cancelBooking(reason: string)
  +getBookingDetails() : string
}

class PaymentSystem {
  -cardNumber: string
  -cardHolderName: string
  -expirationDate: Date
  +processPayment() : boolean
  +validatePaymentDetails() : boolean
}

class Car {
  -carId: string
  -model: string
  -type: string
  -distanceTravelled: float
  -dateOfPurchase: Date
  -isAvailable: boolean
  -price: float
  +checkAvailability() : boolean
  +getDetails() : string
}

User <|-- Customer
User <|-- Admin

Customer "1" -- "0..*" Booking : makes
Admin "1" -- "0..*" Car : manages
Booking "1" -- "1" PaymentSystem : processes
Booking "0..*" -- "1" Car : references

@enduml
"""

ZOOM_Sequnce_Diagram = """
@startuml

actor Customer
actor Admin
participant Booking
participant PaymentSystem
participant Car

== Customer Login ==
Customer -> Customer: login(loginId, password)
activate Customer
alt Successful Login
  Customer --> Customer: display MainOptionsScreen()
else Failed Login
  Customer --> Customer: request to reenter details
end
deactivate Customer

== Car Search ==
Customer -> Car: searchCars(sourceStation, destinationStation, carType)
activate Car
loop For each car in search result
  Car -> Car: checkAvailability()
end
Car --> Customer: available cars list
deactivate Car

== Help Facility (Customer) ==
Customer -> Customer: requestHelp(topic)
activate Customer
Customer --> Customer: display help instructions
deactivate Customer

== Car Booking Process ==
Customer -> Booking: createBooking(car)
activate Booking
Booking -> Car: checkAvailability()
activate Car
deactivate Car
alt Car available
  Booking --> Customer: display car details
  Customer -> Customer: confirm booking
  activate Customer
  deactivate Customer
  Customer -> PaymentSystem: enterCardDetails()
  activate PaymentSystem
  PaymentSystem -> PaymentSystem: validatePaymentDetails()
  alt Payment Successful
    PaymentSystem --> Customer: payment confirmed
    PaymentSystem -> Booking: storeBookingInformation()
    Booking --> Customer: display booking success message
  else Payment Error
    PaymentSystem --> Customer: display payment error
  end
  deactivate PaymentSystem
else Car Not Available
  Booking --> Customer: display car unavailable message
end
deactivate Booking

== Booking Cancellation ==
Customer -> Booking: cancelBooking(bookingId)
activate Booking
Booking -> Booking: getBookingDetails()
Booking --> Customer: display booking details
Customer -> Customer: provideCancellation(reason, reason)
activate Customer
deactivate Customer
Booking -> Booking: processCancellation()
Booking --> Customer: display cancellation success message
deactivate Booking

== Admin Login ==
Admin -> Admin: login(loginId, password)
activate Admin
alt Successful Login
  Admin --> Admin: display MainOptionsScreen()
else Login Failed
  Admin --> Admin: request to reenter details
end
deactivate Admin

== Admin Car Management ==
Admin -> Admin: manageCars()
activate Admin
alt Add Car
  Admin -> Car: addCar(model, distanceTravelled, dateOfPurchase, carType)
  activate Car
  Car --> Admin: display success message
  deactivate Car
else Remove Car
  Admin -> Car: removeCar(carId, reason)
  activate Car
  Car --> Admin: display removal success message
  deactivate Car
end
deactivate Admin

== Admin Help Facility ==
Admin -> Admin: requestHelp(topic)
activate Admin
Admin --> Admin: display help instructions
deactivate Admin

@enduml
"""

MOS_Class_Diagram = """

@startuml
class Operator {
  -loginId : String
  -password : String
  -subscribedAlarms : List<Alarm>
  -subscribedLocations : List<MonitoringLocation>
  +login()
  +viewMonitoringStatus()
  +viewOutstandingAlarms()
  +accessHelpFacility()
}

class RemoteSensor {
  -sensorId : String
  -alarmData : Alarm
  +sendAlarm()
  +transmitSensorData()
}

class MonitoringSystem {
  -operatorList : List<Operator>
  -sensorList : List<Sensor>
  -alarmList : List<Alarm>
  -monitoringLocations : List<MonitoringLocation>
  +displayEmergencyWarning()
  +viewMonitoringStatus()
  +sendStatusUpdates()
  +generateAlarm()
  +notifyOperators()
  +provideHelpFacility()
}

class Alarm {
  -alarmName : String
  -alarmDescription : String
  -location : String
  -severity : String
  -timestamp : DateTime
  +updateAlarmData()
  +displayWarning()
}

class HelpFacility {
  -helpOptions : List<String>
  +displayHelpMenu()
  +provideAssistance()
  +guideOperator()
}

class Notification {
  -subscribedOperators : List<Operator>
  +sendStatusUpdate()
  +sendAlarmNotification()
  +manageSubscriptions()
}

class MonitoringLocation {
  -locationId : String
  -locationName : String
  -sensors : List<Sensor>
  -currentStatus : String
  +getLocationStatus()
  +updateLocationStatus()
}

class Sensor {
  -sensorId : String
  -value : Double
  -upperLimit : Double
  -lowerLimit : Double
  -alarmStatus : String
  +sendMonitoringData()
  +checkAlarmCondition()
  +getSensorStatus()
}

Operator "1" -- "1" MonitoringSystem : interacts with
RemoteSensor "1" -- "1" MonitoringSystem : sends data to
MonitoringSystem "1" -- "1" Notification : uses
MonitoringSystem "1" -- "1" HelpFacility : provides
MonitoringSystem "1" -- "0..*" Alarm : manages
MonitoringSystem "1" -- "0..*" MonitoringLocation : contains
MonitoringLocation "0..*" -- "0..*" Sensor : has
Alarm "0..*" -- "1" MonitoringLocation : associated with
Notification "1" -- "0..*" Operator : monitors
MonitoringSystem "1" -- "0..*" Sensor : contains

@enduml
"""

MOS_Sequnce_Diagram = """
@startuml
actor Operator
participant MonitoringSystem
participant Notification
participant MonitoringLocation
participant Sensor
participant RemoteSensor
participant Alarm
participant HelpFacility

== Operator Login ==
Operator -> MonitoringSystem: login()
activate MonitoringSystem
deactivate MonitoringSystem

== View Monitoring Status ==
Operator -> MonitoringSystem: viewMonitoringStatus()
activate MonitoringSystem
MonitoringSystem -> MonitoringLocation: getLocationStatus()
activate MonitoringLocation
MonitoringLocation -> Sensor: getSensorStatus()
activate Sensor
Sensor --> MonitoringLocation: return sensor status
deactivate Sensor
MonitoringLocation --> MonitoringSystem: return location status
deactivate MonitoringLocation
MonitoringSystem --> Operator: display monitoring status
alt Emergency Situation
  MonitoringSystem -> Notification: displayEmergencyWarning()
  activate Notification
  deactivate Notification
end
deactivate MonitoringSystem

== View Outstanding Alarms ==
Operator -> MonitoringSystem: viewOutstandingAlarms()
activate MonitoringSystem
MonitoringSystem -> Alarm: retrieve alarm details
activate Alarm
Alarm --> MonitoringSystem:
deactivate Alarm
MonitoringSystem --> Operator: display outstanding alarms
alt Emergency Situation
  MonitoringSystem -> Notification: displayEmergencyWarning()
  activate Notification
  deactivate Notification
end
deactivate MonitoringSystem

== Sensor Data Update ==
RemoteSensor -> MonitoringSystem: sendMonitoringData()
activate MonitoringSystem
MonitoringSystem -> Sensor: updateSensorData()
activate Sensor
deactivate Sensor
alt Emergency Situation
  MonitoringSystem -> Notification: displayEmergencyWarning()
  activate Notification
  deactivate Notification
end
MonitoringSystem -> Operator: notify status update
MonitoringSystem -> Notification: sendStatusUpdates()
activate Notification
deactivate Notification
deactivate MonitoringSystem

alt Alarm Condition Detected
  Sensor -> MonitoringSystem: generateAlarm()
  activate MonitoringSystem
  MonitoringSystem -> Notification: notifyOperators()
  activate Notification
  deactivate Notification
  deactivate MonitoringSystem
end

== Remote Sensor Alarm ==
RemoteSensor -> RemoteSensor: sendAlarm()
activate RemoteSensor
deactivate RemoteSensor
alt Sensor Alarm
  RemoteSensor -> MonitoringSystem: displayWarning()
  activate MonitoringSystem
  MonitoringSystem -> Alarm: updateAlarmData()
  activate Alarm
  deactivate Alarm
  deactivate MonitoringSystem
end

== Help Facility ==
Operator -> MonitoringSystem: accessHelpFacility()
activate MonitoringSystem
MonitoringSystem -> HelpFacility: displayHelpMenu()
activate HelpFacility
HelpFacility --> Operator: prompt for help type
Operator -> Operator: request help option
HelpFacility -> HelpFacility: guide through steps
HelpFacility --> Operator: provideAssistance()
deactivate HelpFacility
deactivate MonitoringSystem
@enduml
"""


#New Case Studies

CCTNS_Class_Diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Class Diagram

package "System" {

class Interface {
    + supportsMultilingualInterface()
}

class Data {
    + dataNotLostOnFailure()
    + supportsSelectiveEncryption()
    + ensuresSecureTransmission()
    + validateDataClientServer()
    + softTaggingRowDeletion()
}

class Access {
    + commonUserAccessAuthentication()
    + singleSignOn()
    + extensiblePDAccess()
    + browserBasedAccess()
    + minimalClientRequirements()
    + multiTierAuthentication()
    + supportsSSLConnections()
    + usesHTTPS()
    + multipleBrowsers()
}

class Security {
    + preventCrossSiteScripting()
    + validateIncomingData()
    + encodeIncomingData()
    + preventSQLInjection()
    + utilizeParameterizedQueries()
    + sanitizeUserInputs()
}

class CommunicationNetwork {
    + failureOfEquipmentOrNetwork()
    + supportsMultipleCommunicationServices()
    + supportsVPNConnections()
}

class Architecture {
    + worksOfflineMode()
    + satisfactoryPerformanceLowBandwidth()
    + implementsSOA()
    + modularDesign()
    + developsOnOpenStandards()
    + centralizedDeployment()
    + threeTierDatacenterArchitecture()
    + nTierArchitecture()
}

}

Interface -left-> Data : usesData
Interface -down-> Access : requiresAccess
Access -down-> Security : requiresAuthentication
Data -down-> Security : securedBy
Architecture -left-> Security : enforcesSecurity
CommunicationNetwork -down-> Architecture : supportsArchitecture

@enduml
"""

CCTNS_Sequnce_Diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Sequence Diagrams

participant Interface
participant Data
participant CommunicationNetwork
participant Architecture
participant Access
participant Security

== Interface Behavior ==
Interface -> Access: commonUserAccessAuthentication()
Access -> Access: singleSignOn()
Access -> Access: extensiblePDAccess()
Access -> Access: browserBasedAccess()
Access -> Access: minimalClientRequirements()
Access -> Access: multiTierAuthentication()
Access -> Access: supportsSSLConnections()
Access -> Access: usesHTTPS()
Access -> Access: multipleBrowsers()
Interface -> Data: supportsMultilingualInterface()
Data -> Data: dataNotLostOnFailure()
Data -> Data: supportsSelectiveEncryption()
Data -> Data: ensuresSecureTransmission()
Data -> Data: validateDataClientServer()
Data -> Data: softTaggingRowDeletion()

== Security Behavior (Data + Access) ==
Access -> Security: preventCrossSiteScripting()
Security -> Security: validateIncomingData()
Security -> Security: encodeIncomingData()
Security -> Security: preventSQLInjection()
Security -> Security: utilizeParameterizedQueries()
Security -> Security: sanitizeUserInputs()
Data -> Security: preventCrossSiteScripting()
Security -> Security: validateIncomingData()
Security -> Security: encodeIncomingData()
Security -> Security: preventSQLInjection()
Security -> Security: utilizeParameterizedQueries()
Security -> Security: sanitizeUserInputs()

== Communication & Architecture ==
CommunicationNetwork -> Architecture: failureOfEquipmentOrNetwork()
CommunicationNetwork -> Architecture: supportsMultipleCommunicationServices()
CommunicationNetwork -> Architecture: supportsVPNConnections()
Architecture -> Architecture: worksOfflineMode()
Architecture -> Architecture: satisfactoryPerformanceLowBandwidth()
Architecture -> Architecture: implementsSOA()
Architecture -> Architecture: modularDesign()
Architecture -> Architecture: developsOnOpenStandards()
Architecture -> Architecture: centralizedDeployment()
Architecture -> Architecture: threeTierDatacenterArchitecture()
Architecture -> Architecture: nTierArchitecture()

== Security from Architecture ==
Architecture -> Security: preventCrossSiteScripting()
Security -> Security: validateIncomingData()
Security -> Security: encodeIncomingData()
Security -> Security: preventSQLInjection()
Security -> Security: utilizeParameterizedQueries()
Security -> Security: sanitizeUserInputs()

@enduml
"""

College_Registration_System_Class_Diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title College Registration System Class Diagram

class Student {
  - loginId : string
  - password : string
  - name : string
  - rollNumber : string
  + register()
  + enterDetails()
  + validateDetails()
  + reenterDetails()
  + selectSubject()
  + viewPaper()
  + downloadPaper()
  + viewReports()
  + enterRollNumber()
  + downloadReport()
  + tryAgain()
}

class Administrator {
  - loginId : string
  - password : string
  + login()
  + manageExamOptions()
  + addPaper()
  + removePaper()
  + uploadReport()
  + verifyPaper()
  + acknowledgeUpload()
  + acknowledgeRemove()
  + acknowledgeReport()
}

class Paper {
  - subject : string
  - fileName : string
  + upload()
  + verify()
  + remove()
  + show()
}

class Report {
  - name : string
  - rollNumber : string
  - classWise : string
  + upload()
  + verify()
  + show()
}

Student "1" -- "0..*" Paper : views/downloads
Administrator "1" -- "0..*" Paper : manages
Student "1" -- "0..*" Report : views/downloads
Administrator "1" -- "0..*" Report : manages
@enduml
"""

College_Registration_System_Sequence_Diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title College Registration System Sequence Diagram

actor Student as student
actor Administrator as admin
participant Paper as paper
participant Report as report

== Student Registration ==
student -> admin : register()
student -> admin : enterDetails()
alt Validation Successful
  admin --> student : login()
else Validation Failed
  admin --> student : unsuccessful validation message
  student -> student : tryAgain()
end

== Student Login ==
student -> admin : login()
alt Login Successful
  admin --> student : options available
else Login Failed
  admin --> student : "Login Failed" message
  student -> student : tryAgain()
end

== View Exam Papers ==
student -> admin : selectSubject()
admin -> paper : viewPaper()
paper --> student : show()
student -> paper : downloadPaper()

== Administrator - Add Exam Papers ==
admin -> admin : login()
note over admin
Admin Logged In!
end note
admin -> admin : manageExamOptions()
admin -> paper : addPaper()
admin -> paper : verifyPaper()
alt Acknowledge Successful
  admin -> admin : acknowledgeUpload()
else Verification Failed
  admin -> admin : tryAgain()
end
admin -> paper : upload()

== Administrator - Remove Exam Papers ==
admin -> admin : manageExamOptions()
admin -> paper : removePaper()
admin -> admin : acknowledgeRemove()
paper --> paper : remove()

== Administrator - Upload Reports ==
admin -> admin : manageExamOptions()
admin -> report : uploadReport()
admin -> admin : acknowledgeReport()
report --> report : upload()

== Student - View Reports ==
student -> admin : enterRollNumber()
admin -> report : viewReports()
alt Information Verified
  report --> student : show()
  student -> report : downloadReport()
else Verification Failed
  student --> student : tryAgain()
end

@enduml
"""

estore_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title E-Store Class Diagram

class User {
  + email : String
  + credential : String
  + createProfile()
  + updateProfile()
  + authenticate()
}

class Profile {
  - activeOrders
  - completedOrders
  - frequentSearches
  + viewOrders()
  + selectOrder()
  + viewOrderDetails()
  + registerNewsletter()
  + registerSurvey()
}

class Support {
  - customerInfo
  - productInfo
  - type
  - contactNumbers
  + selectType()
  + enterCustomerInfo()
  + enterProductInfo()
  + displayProducts()
  + displayHelp()
  + displayFAQ()
}

class Promotion {
  + select()
}

class Financing {
  + options
  + selectOption()
  + notifyRequest()
}

class Order {
  - orderInfo
  - trackingInfo
  - paymentInfo
  - shippingCharges
  - shippingDuration
  + confirm()
  + cancel()
  + changeShipping()
  + changePayment()
  + track()
}

class Configuration {
  + selectProduct()
  + addComponent()
  + notifyConflict()
  + updateConfig()
  + confirmConfig()
}

class ShoppingCart {
  - products
  + addProduct()
  + removeProduct()
}

class Shipping {
  - method
  - info
  - options
  + selectMethod()
}

class Payment {
  - method
  - info
  - creditCardNo
  + selectMethod()
  + enterInfo()
}

class Invoice {
  + display()
  + print()
}

class Product {
  - image : String
  - categorization : String
  + displayDetails()
  + browse()
  + displayReviews()
  + enterReview()
  + enterRating()
}

User --o Profile
User --o Support
User --o Promotion
User --o Financing
Profile --o Order
Order --o ShoppingCart
Order --o Shipping
Order --o Payment
Order --o Invoice
ShoppingCart --o Configuration
Configuration --o Product
Product --o ShoppingCart

@enduml
"""

estore_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title E-Store System Sequence Diagram (Without User Actor)

participant User as user
participant Profile as profile
participant Order as order
participant Product as product
participant Configuration as config
participant ShoppingCart as cart
participant Shipping as shipping
participant Payment as payment
participant Invoice as invoice
participant Support as support
participant Promotion as promo
participant Financing as financing

== User Profile Management ==
user -> profile : createProfile()
user -> profile : updateProfile()
user -> profile : authenticate()
user -> profile : viewOrders()
user -> profile : selectOrder()
user -> profile : viewOrderDetails()
user -> profile : registerNewsletter()
user -> profile : registerSurvey()

== Product Browsing ==
user -> product : browse()
product -> product : displayDetails()
product -> product : displayReviews()
product -> product : enterReview()
product -> product : enterRating()

== Product Configuration ==
user -> config : selectProduct()
config -> config : addComponent()
config -> config : displayDetails()
config -> config : notifyConflict()
config -> config : updateConfig()
config -> config : confirmConfig()
user -> cart : addProduct()
cart -> cart : displayDetails()

== Order Management ==
order -> order : confirm()
order -> order : cancel()
order -> order : changeShipping()
order -> shipping : selectMethod()
order -> order : changePayment()
order -> payment : selectMethod()
payment -> payment : enterInfo()
order -> invoice : display()
invoice -> invoice : print()
order -> order : track()
cart -> cart : removeProduct()

== Shipping ==
shipping -> shipping : selectMethod()
shipping -> shipping : enterInfo()

== Payment ==
payment -> payment : selectMethod()
payment -> payment : enterInfo()

== Support ==
support -> support : selectType()
support -> support : enterCustomerInfo()
support -> support : enterProductInfo()
support -> support : displayContacts()
support -> support : displayHelp()
support -> support : displayFAQ()

== Promotion ==
promo -> promo : select()

== Financing ==
financing -> financing : selectOption()
financing -> financing : notifyRequest()

@enduml
"""

car_rental_system_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Car Rental Class Diagram

class Customer {
    - membershipNumber: String
    - password: String
    + browseIndex()
    + selectIndexHeading()
    + selectCarModels()
    + viewCars()
    + requestCarModelDetails()
    + initiateSearch()
    + logOn()
    + logOff()
}

class Member {
    - name: String
    - address: String
    - status: String
    - creditCardLastFourDigits: String
    + enterMembershipNumber()
    + enterPassword()
    + logOn()
    + viewMemberDetails()
    + viewRentals()
    + logOff()
    + reserveCarModel()
    + viewRentalsSummary()
    + enterOldPassword()
    + enterNewPassword()
    + reEnterNewPassword()
    + initiatePasswordChange()
    + confirmPasswordChange()
    + cancelReservation()
    + confirmCancellation()
}

class CarModel {
    - modelNumber: String
    - price: Double
    - make: String
    - engineSize: String
    - description: String
    - color: String
    - poster: String
    + displayDetails()
}

class Assistant {
    + logOn()
    + viewReservationsList()
    + takeActionOnReservation()
}

class Reservation {
    - reservationNumber: String
    - date: Date
    - time: Time
    - carModel: CarModel
    + create()
    + confirm()
    + cancel()
    + conclude()
}

Customer <|-- Member
Member --> Reservation: makes
CarModel <-- Reservation: references
Assistant --> Reservation: manages

@enduml
"""

car_rental_system_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Car Rental System Sequence Diagram

participant Customer
participant Member
participant CarModel
participant Reservation
participant Assistant

== Customer Browses and Views Car Models ==
Customer -> Member : browseIndex()
Member -> Member : selectIndexHeading()
Member -> CarModel : selectCarModels()
CarModel --> Customer : viewCars()
Customer -> CarModel : requestCarModelDetails()
CarModel --> Customer : displayDetails()
Customer -> Customer : initiateSearch()

== Customer Authentication ==
Customer -> Member : logOn()
Customer -> Member : logOff()

== Member Authentication ==
Member -> Member : enterMembershipNumber()
Member -> Member : enterPassword()
Member -> Member : logOn()

== Member Views Details ==
Member -> Member : viewMemberDetails()
Member -> Member : viewRentals()
Member -> Member : viewRentalsSummary()

== Member Reservation ==
Member -> Reservation : reserveCarModel()
Reservation -> Reservation : create()
Reservation -> Reservation : confirm()

== Member Password Management ==
Member -> Member : enterOldPassword()
Member -> Member : enterNewPassword()
Member -> Member : reEnterNewPassword()
Member -> Member : initiatePasswordChange()
Member -> Member : confirmPasswordChange()

== Member Reservation Cancellation ==
Member -> Reservation : cancelReservation()
Member -> Reservation : confirmCancellation()
Reservation -> Reservation : cancel()
Reservation -> Reservation : conclude()

== Assistant Manages Reservations ==
Assistant -> Assistant : logOn()
Assistant -> Assistant : viewReservationsList()
Assistant -> Reservation : takeActionOnReservation()

@enduml
"""

LIS_Class_Diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Library Class Diagram

class Staff {
  + designQuery()
  + runReport()
  + modifyReportTemplate()
}

class Branch {
  - name
  - location
  - capacity
  + getCapacity()
  + generateBranchReport()
}

class Administrator {
  + createReportTemplate()
  + limitFiltersAndDisplayFields()
  + controlStaffAccess()
  + createSharedFolder()
}

class Report {
  - reportTemplate
  - filters
  - displayFields
  + generateReport()
  + customizeReport()
  + saveReport()
}

class Item {
  - status
  - type
  - value
  - location
  - inTransit
  + updateStatus()
  + trackTransit()
}

class Patron {
  - transactionHistory
  - checkOuts
  - holdsPlaced
  - activityStatus
  + getCirculationStats()
  + getTransactionDetails()
}

class ReportTemplate {
  - predefinedFilters
  - restrictedFields
  + createTemplate()
  + cloneTemplate()
  + limitTemplateModification()
}

class Transaction {
  - type
  - date
  - item
  - patron
  + recordTransaction()
  + generateTransactionReport()
}

Staff "0..*" -- "1" Report
Branch "1" -- "1" Item
Item "1" -- "0..*" Transaction
Patron "1" -- "0..*" Transaction
Administrator "1" -- "0..*" ReportTemplate
Report "1" -- "1" ReportTemplate

@enduml
"""

LIS_Sequnce_Diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Library System Sequence Diagram

actor Administrator
actor Staff
participant Report
participant ReportTemplate
participant Branch
participant Patron
participant Transaction
participant Item

== Administrator Actions ==
Administrator -> ReportTemplate : createReportTemplate()
Administrator -> ReportTemplate : limitFiltersAndDisplayFields()
Administrator -> Staff : controlStaffAccess()
Administrator -> Administrator : createSharedFolder()

== Staff Actions ==
Staff -> Report : designQuery()
Staff -> Report : runReport()
Staff -> Report : modifyReportTemplate()

== Report Operations ==
Report -> Report : generateReport()
Report -> Report : customizeReport()
Report -> Report : saveReport()

== ReportTemplate Operations ==
ReportTemplate -> ReportTemplate : createTemplate()
ReportTemplate -> ReportTemplate : cloneTemplate()
ReportTemplate -> ReportTemplate : limitTemplateModification()

== Branch Operations ==
Branch -> Branch : getCapacity()
Branch -> Branch : generateBranchReport()

== Patron Operations ==
Patron -> Patron : getCirculationStats()
Patron -> Patron : getTransactionDetails()

== Transaction Operations ==
Transaction -> Transaction : recordTransaction()
Transaction -> Transaction : generateTransactionReport()

== Item Operations ==
Item -> Item : updateStatus()
Item -> Item : trackTransit()

@enduml
"""

online_book_store_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Online Bookstore System Class Diagram

class Customer {
  - loginId : String
  - password : String
  + register()
  + login()
  + searchBook()
  + addToShoppingCart()
  + sellUsedBooks()
  + reviewBook()
  + checkout()
  + downloadReceipt()
}

class Order {
  - bookList : List<Book>
  + checkOrder()
  + proceed()
}

class Book {
  - name : String
  - publication : String
  - type : String
  - overallRating : Double
  + displayBookDetails()
  + updateRating()
}

class ShoppingCart {
  - cartItems : List<Book>
  + addToCart()
}

Customer "1" -- "0..*" Order : places
Customer "1" -- "1" ShoppingCart : has
Order "1" -- "1..*" Book : contains
ShoppingCart "1" -- "0..*" Book : contains
Customer "1" -- "0..*" Book : reviews

@enduml
"""

online_book_store_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Online Bookstore System Sequence Diagram

participant Customer as customer
participant Book as book
participant ShoppingCart as shoppingCart
participant Order as order

== Registration Process ==
customer -> customer : register()

== Login Process ==
customer -> customer : login()

== Book Search Process ==
customer -> book : searchBook()
book --> customer : displayBookDetails()

== Add Book to ShoppingCart ==
customer -> shoppingCart : addToShoppingCart()
shoppingCart -> shoppingCart : addToCart()
shoppingCart -> order : addbook()
note right: addBook() is a placeholder for a more detailed process of adding a book to the order, but it's not present in the diagram

== Sell Used Books Process ==
customer -> customer : sellUsedBooks()

== Book Review Process ==
customer -> book : reviewBook()
book -> book : updateRating()

== Checkout Process ==
customer -> order : checkout()
order -> order : checkOrder()
order -> order : proceed()
customer -> customer : downloadReceipt()

@enduml
"""

online_bus_reserveation_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Online Bus Reservation System Class Diagram

class HelpFacility {
  - facilities : List<String>
  + displayInstructions()
}

class User {
  - loginId : String
  - password : String
  + login()
  + confirm()
}

class Customer {
  - name : String
  - age : Int
  - numberOfPassengers : Int
  - sourceStation : String
  - destinationStation : String
  - date : Date
  - busType : String
  + search()
  + purchaseTicket()
  + cancelReservation()
  + useHelpFacility()
}

class Admin {
  + login()
  + confirm()
  + addBus()
  + removeBus()
}

class Reservation {
  - reservationNumber : String
  - customerName : String
  - sourceStation : String
  - destinationStation : String
  - date : Date
  - numberOfPassengers : Int
  + submit()
  + processCancellation()
  + displayReservationDetails()
}

class Payment {
  - creditCardNumber : String
  - cardholderName : String
  - expirationDate : Date
  + submit()
}

class Bus {
  - busId : String
  - sourceStation : String
  - destinationStation : String
  - busType : String
  - price : Double
}

HelpFacility "1" -- "1" User : supports
User <|-- Customer
User <|-- Admin
Customer "1" -- "1" Reservation : makes
Customer "1" -- "1" Payment : performs
Admin "1" -- "0..*" Bus : manages
Reservation "1" -- "1" Bus : associated with
Payment "1" -- "0..*" Bus

@enduml
"""

online_bus_reserveation_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Online Bus Reservation System Sequence Diagram

actor User as user
actor Customer as customer
actor Admin as admin
participant Bus as bus
participant Reservation as reservation
participant Payment as payment
participant HelpFacility as helpFacility

== Customer Login Process ==
user -> user : login()
user -> user : confirm()
alt Successful Login
  user --> user : Login successful!
else Failed Login
  user --> user : Login failed, retry
end

== Bus Search Process ==
customer -> bus : search()
bus --> customer : Display bus options

== Help Facility ==
alt Customer needs help
  customer -> helpFacility : useHelpFacility()
  helpFacility --> customer : show instructions
  helpFacility --> helpFacility : displayInstructions()
end

== Ticket Reservation Process ==
customer -> reservation : submit()
reservation -> bus : associate with selected bus()
reservation --> customer : displayReservationDetails()
alt Payment Successful
  customer -> payment : submit()
  payment --> customer : Payment confirmed
else Payment Failed
  customer --> customer : Payment failed
end

== Reservation Cancellation ==
customer -> reservation : cancelReservation()
reservation -> reservation : processCancellation()
reservation --> customer : displayReservationDetails()
customer --> customer : Cancellation confirmation

== Admin Bus Management ==
admin -> admin : login()
admin -> admin : confirm()
alt Admin Adds Bus
  admin -> bus : addBus()
  bus --> admin : Add bus details
  admin --> admin : Success message
else Admin Removes Bus
  admin -> bus : removeBus()
  bus --> admin : Remove bus details
  admin --> admin : Success message
end

@enduml
"""

online_discussion_group_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Discussion Group System Class Diagram

class User {
  - loginId : String
  - password : String
  + login()
  + authenticate()
  + retryInput()
  + showErrorMessage()
}

class Leader {
  + createGroup()
  + inviteStudents()
  + deletePresentation()
  + deleteComment()
}

class DiscussionGroup {
  + validateGroup()
}

class Student {
  + joinGroup()
  + leaveGroup()
  + addPresentation()
  + editPresentation()
  + addComment()
  + editComment()
}

class Presentation {
  + create()
  + edit()
  + delete()
  + saveChanges()
}

class Comment {
  + create()
  + edit()
  + delete()
}

User <|-- Leader
User <|-- Student
Leader "0..1" -- "1" DiscussionGroup : manages
DiscussionGroup "1" -- "1..*" Student : members
Student "1" -- "0..*" Presentation : creates
Student "1" -- "1" Comment : writes
Presentation "1" -- "0..*" Comment : contains

@enduml
"""

online_discussion_group_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Discussion Group System Sequence Diagram

actor Leader
actor Student
participant User
participant DiscussionGroup
participant Presentation
participant Comment

== Student Adds Comment ==
Student -> User : login()
User -> User : authenticate()
alt Authentication Fails
  User --> Student : showErrorMessage()
  Student -> User : retryInput()
else Authentication Succeeds
  Student -> DiscussionGroup : validateGroup()
  Student -> Presentation : create()
  note right: Selecting or ensuring presentation exists
  Student -> Comment : create()
  note right: Associate comment with presentation
  alt Comment Add Fails
    Comment --> Student : showErrorMessage()
  else Comment Add Successful
    Comment --> Student : Acknowledge withComment()
  end
end

== Student Edits Comment ==
Student -> User : login()
User -> User : authenticate()
alt Authentication Fails
  User --> Student : showErrorMessage()
else Authentication Succeeds
  Student -> Student : edit()
  alt Save Changes
    Student -> Presentation : saveChanges()
    Student --> Student : edit successful
  else Discard Changes
    Student --> Student : no changes saved
  end
end

== Leader Deletes Comment ==
Leader -> User : login()
User -> User : authenticate()
alt Authentication Fails
  User --> Leader : showErrorMessage()
else Leader Authenticated
  Leader -> DiscussionGroup : validateGroup()
  Leader -> Comment : delete()
  Comment --> Comment : delete()
  Comment --> Leader : delete successful
end

@enduml
"""

online_pet_store_system_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Pet Store System Class Diagram

class Customer {
  - loginId : String
  - password : String
  - emailAddress : String
  - shippingAddress : String
  + login()
  + browseCatalog()
  + selectPetCategory()
  + selectItems()
  + addToCart()
  + checkout()
  + enterShippingAddress()
  + selectShippingOption()
  + selectPaymentMethod()
  + placeOrder()
  + checkOrderStatus()
}

class Supplier {
  - loginId : String
  - password : String
  + login()
  + checkInventory()
  + processDeliveryOrder()
  + confirmItemAvailability()
}

class Authentication {
  + validateLogin()
  + checkRegistration()
  + registerNewUser()
}

class Catalog {
  - categories : List<String>
  + displayCatalog()
}

class Item {
  - itemName : String
  - price : Double
  - petCategory : String
}

class ShoppingCart {
  - selectedItems : List<Item>
  - totalPrice : Double
  + addItem()
  + calculateTotalPrice()
}

class Order {
  - orderNumber : String
  - items : List<Item>
  - totalPrice : Double
  - status : String
  - shippingOption : String
  + generateConfirmationNumber()
  + checkStatus()
}

class Inventory {
  - availableItems : List<Item>
  + checkItemAvailability()
  + reserveItems()
  + updateInventory()
}

class PaymentMethod {
  - cardType : String
  - cardDetails : String
  + validatePayment()
  + processPayment()
}

Customer "1" -- "1" Authentication : authenticates
Customer "1" -- "1" Catalog
Customer "1" -- "1" ShoppingCart : has
Customer "1" -- "1" Order : places
Supplier "1" -- "0..*" Order : processes
Supplier "1" -- "1" Inventory : manages
Catalog "1" -- "1..*" Item : contains
ShoppingCart "1" -- "0..*" Item : holds
Order "1" -- "1..*" Item : includes
Order "1" -- "1" PaymentMethod : uses

@enduml
"""

online_pet_store_system_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Online Bus Reservation System Sequence Diagram

actor Customer
actor Supplier
participant Authentication
participant Catalog
participant Item
participant ShoppingCart
participant Order
participant PaymentMethod
participant Inventory

== Customer Login ==
alt Valid Credentials
  Customer -> Authentication : login()
  Authentication --> Customer : validateLogin()
  alt Login Successful
    Authentication --> Customer : login confirmed
  else Login Failed
    Authentication --> Customer : login failed
  end
else Invalid Credentials
  Customer -> Authentication : login()
  Authentication --> Customer : validateLogin()
  Authentication --> Customer : login failed
end

== Registration ==
alt New User
  Customer -> Authentication : registerNewUser()
  Authentication --> Customer : registration confirmation
end

== Browse Catalog ==
Customer -> Catalog : browseCatalog()
Catalog --> Customer : displayCatalog()
alt Show Categories
  Customer -> Catalog : selectPetCategory()
  Catalog --> Customer : displayCatalog()
end

== Item Selection & Cart ==
Customer -> Item : selectItems()
Item --> Customer : show item details
Customer -> ShoppingCart : addToCart()
ShoppingCart -> ShoppingCart : addItem()
ShoppingCart -> ShoppingCart : calculateTotalPrice()
ShoppingCart --> Customer : display cart contents

== Checkout ==
Customer -> Order : checkout()
Order -> Order : enterShippingAddress()
Order -> Order : selectShippingOption()
Order -> PaymentMethod : selectPaymentMethod()
Order -> Order : placeOrder()

== Payment ==
alt Card
  Customer -> PaymentMethod : validatePayment()
  PaymentMethod --> PaymentMethod : processPayment()
  PaymentMethod --> Customer : Payment confirmed
end

== Place Order ==
Customer -> Inventory : checkItemAvailability()
alt Item Available
  Inventory --> Inventory : reserveItems()
  Order -> Order : generateConfirmationNumber()
  Order --> Customer : Order Confirmation
else Item Unavailable
  Inventory --> Inventory : Item Unavailability
end

== Supplier Processing ==
Supplier -> Authentication : login()
Authentication --> Supplier : validateLogin()
alt Login Successful
  Supplier -> Inventory : checkInventory()
  Inventory --> Supplier : item availability
  Supplier -> Order : processDeliveryOrder()
  alt Order Processed
    Supplier -> Inventory : updateInventory()
    Inventory --> Supplier : success message
  else Alternative Required
    Supplier --> Supplier : alternative required message
  end
end

== Customer Order Status ==
Customer -> Order : checkOrderStatus()
Order --> Customer : checkStatus()
alt Active Orders
  Order --> Customer : show active orders
else No Active Orders
  Order --> Customer : No active orders
end

@enduml
"""

elearning_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title E-Learning System Class Diagram

class Students {
  + preferencesNotifications()
  + notificationSubscriptions()
  + displayWebFeeds()
  + webFeedsOnOff()
  + searchFunctionality()
  + displaySearchBox()
}

class VoiceClip {
  + organizeVoiceClips()
  + organizePortfolio()
  + downloadVoiceClips()
  + storesAudioClips()
  + deleteRecordedClips()
}

class Wiki {
  + providesWiki()
}

class Blog {
  + providesBlogEngine()
}

class File {
  + capturesFiles()
  + manageFiles()
  + multipleFileUpload()
}

class Administrator {
  + gradeAnAssignment()
}

class Grade {
  + postGrades()
  + displayGradeInformation()
  + gradeHistory()
}

Students -- VoiceClip : organize/download/delete
Students -- Wiki : collaborateDocs
Students -- Blog : blogEngine
Students -- File : capture/manage
Students -- Grade : viewGradeInfo
Administrator -- Grade : grade/post

@enduml
"""

elearning_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title E-Learning System Sequence Diagram

participant File
participant VoiceClip
participant Grade
participant Wiki
participant Blog
participant Administrator
participant Students

== File actions ==
Students -> File : capturesFiles()
Students -> File : filesCaptured()
Students -> File : manageFiles()
Students -> File : filesManaged()
Students -> File : multipleFileUpload()
Students -> File : filesUploaded()

== VoiceClip actions ==
Students -> VoiceClip : organizeVoiceClips()
Students -> VoiceClip : voiceClipsOrganized()
Students -> VoiceClip : organizePortfolio()
Students -> VoiceClip : portfolioOrganized()
Students -> VoiceClip : downloadVoiceClips()
Students -> VoiceClip : voiceClipsDownloaded()
Students -> VoiceClip : storesAudioClips()
Students -> VoiceClip : audioClipsStored()
Students -> VoiceClip : deleteRecordedClips()
Students -> VoiceClip : clipsDeleted()

== Grade actions ==
Students -> Grade : postGrades()
Students -> Grade : gradesPosted()
Students -> Grade : displayGradeInformation()
Students -> Grade : gradeInfoDisplayed()
Students -> Grade : gradeHistory()
Students -> Grade : historyMaintained()

== Wiki actions ==
Students -> Wiki : providesWiki()
Students -> Wiki : wikiProvided()

== Blog actions ==
Students -> Blog : providesBlogEngine()
Students -> Blog : blogProvided()

== Administrator actions ==
Administrator -> Grade : gradeAnAssignment()
Administrator -> Grade : assignmentGraded()

== Student actions ==
Students -> Students : preferencesNotifications()
Students -> Students : preferencesSaved()
Students -> Students : notificationSubscriptions()
Students -> Students : subscriptionsManaged()
Students -> Students : displayWebFeeds()
Students -> Students : feedsDisplayed()
Students -> Students : webFeedsOnOff()
Students -> Students : feedsToggled()
Students -> Students : searchFunctionality()
Students -> Students : searchPerformed()
Students -> Students : displaySearchBox()
Students -> Students : searchBoxDisplayed()

@enduml
"""

railway_reservation_system_class_diagram = """
@startuml
skinparam handwritten true
skinparam ClassAttributeFontColor #005000
skinparam ClassAttributeFontSize 12

title Railway Reservation System Class Diagram

class Customer {
  - loginId : String
  - password : String
  - sourceStation : String
  - destinationStation : String
  - date : String
  - typeOfTrain : String
  - reservationNumber : String
  - creditCardNumber : String
  - cardholderName : String
  - creditCardExpirationDate : String
  + clickLoginButton()
  + enterLoginIdAndPassword()
  + clickConfirmButton()
  + enterSourceStation()
  + enterDestinationStation()
  + enterDate()
  + enterTypeOfTrain()
  + clickSearch()
  + selectPurchaseTicket()
  + enterReservationNumber()
  + clickSubmitButton()
  + enterCreditCardDetails()
  + clickCancelReservation()
  + selectProcessCancellation()
  + clickHelpFacility()
}

class HelpFacility {
  - instructionsList : List<String>
  + showInstructions()
  + showHowToFillInformation()
}

class Admin {
  - loginId : String
  - password : String
  + clickLoginButton()
  + enterLoginIdAndPassword()
  + clickConfirmButton()
  + selectAddTrain()
  + selectRemoveTrain()
  + fillRequiredInformation()
}

class Reservation {
  - reservationNumber : String
  - reservationDetails : String
}

class Train {
  - sourceStation : String
  - destinationStation : String
  - typeOfTrain : String
  - price : Double
}

Customer "1" -- "0..*" Reservation : makes
Customer "1" -- "1" HelpFacility : uses
Admin "1" -- "0..*" Train : manages
Reservation "1" -- "1" Train : associated with

@enduml
"""

railway_reservation_system_sequnce_diagram = """
@startuml
skinparam handwritten true
skinparam sequence {
    ParticipantPadding 20
    ActorBorderColor #005000
    LifeLineBorderColor #005000
    ArrowColor #005000
}

title Railway Reservation System Sequence Diagram

actor Customer
actor Admin
participant Train
participant Reservation
participant HelpFacility

== Customer Login Process ==
Customer -> Admin : clickLoginButton()
Customer -> Admin : enterLoginIdAndPasswords()
Customer -> Admin : clickConfirmButton()

== Train Search Process ==
Customer -> Customer : enterSourceStation()
Customer -> Customer : enterDestinationStation()
Customer -> Customer : enterDate()
Customer -> Customer : enterTypeOfTrain()
Customer -> Customer : clickSearch()

== Help Facility ==
Customer -> HelpFacility : clickHelpFacility()
HelpFacility --> Customer : showInstructions()
HelpFacility -> HelpFacility : showHowToFillInformation()

== Ticket Purchase Process ==
Customer -> Customer : selectPurchaseTicket()
Customer -> Customer : enterReservationNumber()
Customer -> Customer : clickSubmitButton()
Customer -> Customer : enterCreditCardDetails()
Customer -> Reservation : associated with Train

== Reservation Cancellation ==
Customer -> Customer : clickCancelReservation()
Customer -> Customer : selectProcessCancellation()

== Admin Train Management ==
Admin -> Admin : clickLoginButton()
Admin -> Admin : enterLoginIdAndPassword()
Admin -> Admin : clickConfirmButton()
alt Add Train
  Admin -> Admin : selectAddTrain()
  Admin -> Admin : fillRequiredInformation()
else Remove Train
  Admin -> Admin : selectRemoveTrain()
end

@enduml
"""