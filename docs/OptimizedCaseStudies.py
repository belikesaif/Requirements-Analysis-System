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
  +retrieveDetails():
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