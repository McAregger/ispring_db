Description
A database shall be created to manage customers, devices, calibrations, and errors.
A customer can own zero or multiple devices.
A device can be assigned to at most one customer, but it does not necessarily have to be assigned to a customer
from the beginning.
A device can have zero, one, or multiple device calibrations.
Each device calibration belongs to exactly one device.
Only standardized calibrations shall be used. For this purpose, calibration master data will be maintained.
For each device, zero, one, or multiple errors can be recorded.
An error type can occur on multiple devices, and a device can have multiple error types.
Database manipulation will initially be performed through the PySide6 GUI. However, during development,
the project must be structured in a way that allows for a future FastAPI implementation:


PySide6 GUI
        \
         -> Services -> Repositories -> SQLModel/DB
        /
FastAPI

ispring_db/
├─ core/
│  ├─ config.py
│  └─ database.py
├─ models/
│  ├─ customer.py
│  ├─ device.py
│  └─ ...
├─ repositories/
│  └─ ...
├─ services/
│  └─ ...
├─ gui/
│  ├─ main.py
│  └─ ...
└─ api/
   └─ main.py

Layer	      Usage
core	      Infrastruktur (DB, config, logging)
models	      SQLModel Datenbankmodelle
services	  Businesslogik
gui	PySide6   UI
api	FastAPI   Endpunkte
packaging	  exe build

Package Description:

app:
The app package contains the main application code.
It is divided into several sub-packages that represent different functional layers of the application.

core:
-The core package contains fundamental technical components that are used throughout the entire application.
-This includes:
-application configuration
-database connection and session management
-database initialization
-These components provide the technical foundation required by the rest of the system.

Typical contents:
-database engine configuration
-database table creation
-application configuration parameters (e.g., database path, environment variables)

models:
The models package contains the database models of the application.
Database tables are defined here using SQLModel.
Each class represents a table in the database.

The models define:
-table structure
-data types of attributes
-primary keys
-foreign keys
-relationships between tables

Examples of models in the project:
-Customer
-Device
-Error
-Calibration
-DeviceCalibration

These models therefore define the structure of the database

schemas:
The schemas package contains data structures used for input and output validation.
These models are separated from the database models and are typically used for:
-validating input data
-structuring API responses
-data exchange between different application layers

This separation makes it easier to use the database functionality through APIs in the future.

repositories:
The repositories package contains classes or functions responsible for direct interaction with the database.
Repositories encapsulate database operations such as:
-inserting records
-querying data
-updating records
-deleting records
This approach ensures that other parts of the application do not need to interact directly with SQLModel.

Repositories therefore act as the interface between the application logic and the database.

services:
The services package contains the business logic of the application.
This layer implements the functional rules of the system, for example:
-input validation
-data processing
-combining multiple database operations
-Services use repositories to read or modify data in the database.
Both the desktop application and a future API interact with the database through the service layer,
ensuring that business logic remains centralized and reusable.

gui:
The gui package contains the graphical user interface of the application implemented with PySide6.
It includes all components required for the desktop application, such as:
-the main application window
-input forms for data records
-dialog windows
-custom GUI widgets

The GUI does not access the database directly but instead uses the service layer to perform data operations.

api:
The api package contains the components required to expose the application functionality via a REST API using FastAPI.
This package typically includes:
-API endpoints
-routing definitions
-dependency management
-request and response handling

The API layer also uses the service layer to interact with the database.
This allows both the desktop application and external systems to reuse the same business logic.

utils:
The utils package contains general helper functions used across different parts of the application.
Examples include:
-formatting functions
-small helper utilities
-reusable utility functions

This package provides a central location for commonly used helper code.

tests:
The tests package contains automated tests for the application.
Tests may cover:
-database models
-repositories
-services
-API endpoints

Automated tests help ensure the reliability and stability of the application.

scripts:
The scripts package contains utility scripts used for development or maintenance tasks.
Examples include:
-database initialization
-generating test data
-maintenance operations
-These scripts are typically executed manually when needed.



