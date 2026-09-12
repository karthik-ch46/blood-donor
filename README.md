# Blood Donor Search System

A Flask-based Blood Donor Search System developed as a CSP/AI project.

## Features

- Mobile number login
- No OTP authentication
- Donor registration
- Donor profile
- Blood group search
- City-based donor search
- Donor availability
- Contact donor by phone
- OpenStreetMap location
- Interactive donor map
- SQLite database
- Responsive website

## Technologies

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Leaflet
- OpenStreetMap

## Blood Groups

- A+
- A-
- B+
- B-
- O+
- O-
- AB+
- AB-

## Installation

Install Python.

Open the project folder in VS Code.

Open the VS Code terminal.

Run:

pip install -r requirements.txt

Then run:

python app.py

Open:

http://127.0.0.1:5000

## Project Structure

blood-donor/

    app.py

    requirements.txt

    README.md

    database.db

    templates/
        login.html
        home.html
        profile.html
        register.html
        search.html
        donors.html

    static/
        css/
            style.css

        js/
            script.js

## Database

SQLite is used as the database.

The database is automatically created when app.py is started.

## Map

The project uses:

Leaflet

and

OpenStreetMap

for displaying donor locations.

No Google Maps API key is required.

## Important

This is an educational CSP project.

For a production blood donation application, additional security,
authentication, privacy protection, donor verification and medical
eligibility checks should be implemented.