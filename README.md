# Epic Events: REST API for Customer Relationship Management (CRM)
Epic Events is a RESTful API designed for Customer Relationship Management (CRM). A CRM system enables a company to manage its relationships and interactions with current and potential customers. In this scenario, Epic Events allows its users to organize events, monitor a portfolio of clients through contracts and edit event details. Access to information and credentials are defined through permissions depending on the level of responsibility of the CRM user.  

# Authentication

* Access is granted to authenticated users via JSON Web Tokens (JWTs).

# Permissions
* CRM users are divided into three categories: Management, Sales, Support.
* The CRM data are manyfold. A user with credentials can access details of users, clients, contracts, events, and event notes.
## Management members
* Management members can read and edit any information of the CRM system.
## CRM Users
* A CRM user can be created, read and edited (updated or deleted) only by Management members.
## CRM Clients
* A client can be created by Management and Sales members.
* By default, a Sales member who creates a clients becomes the sales contact of this client.
* Once created, a client can be read by Management members, the sales contact and the support contacts in charge of the events of this client.
* A client can be edited (updated or deleted) by Management members and the sales contact.
## CRM Contracts
* A client can be created, read, updated or deleted only by Management and Sales members.
* By default, a Sales member who created a contract becomes the sales contact of this contract.
## CRM Events
* An event can be created by Management members and the sales contact of the client organizing the event.
* An event cannot be created directly. To do so, the contract between the company and a client must be signed.
* Once created, an event can be read by Management members, the sales contact of the client organizing this event, and the support contact in charge of the event.
* An event can be edited (updated or deleted) by Management members and the support contact on charge of this event.
## CRM Notes
* In order to organize events, it is possible to create notes.
* Several notes can be created for the same event.
* A note can be created or edited (updated or deleted) by Management members and the support member on charge of the event.
* Once created, a note can be read by Management members, the support contact in charge of the event, and the sales contact of the client organizing the event.  

# Installation  

This locally-executable API can be installed and executed from using the following steps.
1.	Clone this repository using `https://github.com/Alexandremerancienne/EpicEvents.git` (you can also download the code [as a zip file](https://github.com/Alexandremerancienne/EpicEvents/archive/refs/heads/main.zip)).
2.	Move to the project root folder.
3.	Create a virtual environment (venv).
4.	Activate your venv.
5.	Install project dependencies listed in requirements.txt file : `pip install -r requirements.txt`.
6.	Create a superuser to generate a user profile: `python manage.py createsuperuser`.
7.	You can consume the API with the newly created superuser, or with another user created with the superuser.
8.	Migrate the data: `python manage.py migrate`.
9.	Run the server: `python manage.py runserver`.  

When the server is running after step 7 of the procedure, the CRM can be requested after login from the endpoint [http://localhost:8000/crm/v1/login/](http://localhost:8000/crm/v1/login/).

# Usage and detailed endpoint documentation

One you have launched the server and opened a session, you can read the documentation through the browseable documentation interface of the API by visiting the following endpoints: 
* CRM users: [http://localhost:8000/crm/v1/users/](http://localhost:8000/crm/v1/users/)
* CRM clients: [http://localhost:8000/crm/v1/clients/](http://localhost:8000/crm/v1/clients/)
* CRM contracts: [http://localhost:8000/crm/v1/contracts/](http://localhost:8000/crm/v1/contracts/)
* CRM events: [http://localhost:8000/crm/v1/events/](http://localhost:8000/crm/v1/events/)
* CRM notes: [http://localhost:8000/crm/v1/notes/](http://localhost:8000/crm/v1/events/<event_id>/notes/)  

All these endpoints support HTTP requests using GET, POST, PUT and DELETE methods:

# Filters
You can apply filters to search an instance of any data available in the CRM system.
## Search and filter users
You can search and filter users with the following endpoint: http://localhost:8000/crm/v1/users/. The filters available are:
* `username=<username>` to get users filtered by username. The search does an exact match of the username.
* `role=<role>` to get users by role (management, sales or support).
* `username_contains=<string>` to search users whose username contains the search term. The search is independent of character case.

## Search and filter clients
You can search and filter clients with the following endpoint: http://localhost:8000/crm/v1/clients/. The filters available are:
* `first_name__contains=<string>` to search clients whose first name contains the search term. The search is independent of character case.
* `first_name=<first name>` to get clients filtered by first name. The search does an exact match of the first name.
* * `last_name__contains=<string>` to search clients whose last name contains the search term. The search is independent of character case.
* `last_name=<last name>` to get clients filtered by last name. The search does an exact match of the last name.
* `company=<company>` to get clients filtered by company. The search does an exact match of the company name.
* `sales_contact=<integer>` to get clients filtered by sales contact. The search does an exact match of the identification number (id) of the sales contact.


## Search and filter contracts
You can search and filter contracts with the following endpoint: http://localhost:8000/crm/v1/contracts/. The filters available are:
* `status=<boolean>` to search contracts whose status is true (contract signed) or false.
* `client=<integer>` to get contracts filtered by client. The search does an exact match of the identification number (id) of the client.
* `sales_contact=<integer>` to get contracts filtered by sales contact. The search does an exact match of the identification number (id) of the sales contact.

## Search and filter events
You can search and filter events with the following endpoint: http://localhost:8000/crm/v1/events/. The filters available are:
* `event_over=<boolean>` to search events whose status is true (event over) or false.
* `client=<integer>` to get events filtered by client. The search does an exact match of the identification number (id) of the client.
* `support_contact=<integer>` to get events filtered by support contact. The search does an exact match of the identification number (id) of the support contact.

## Search and filter notes
You can search and filter notes with the following endpoint: http://localhost:8000/crm/v1/events/<event_id>/notes/. The filters available are:
* `description__contains=<string>` to search notes whose description contains the search term. The search is independent of character case.

# Endpoints test
* Endpoints can be tested with tools such as Postman or cURL.
* A [Public Postman collection]( https://documenter.getpostman.com/view/15000046/TzzDLbHx) is available to test the API endpoints.
