# Full Auth Flask Backend - Productivity App

## Project Description
A secure RESTful Flask API backend for a personal productivity notes application. It implements session-based user authentication with Bcrypt password hashing, full CRUD functionality for user-owned notes, route protection ensuring users can only view or modify their own notes, and paginated index responses.

## Installation Instructions

1. Clone this repository and navigate into the project directory:
   bash
   git clone [https://github.com/patrickngumba-cmd/flask-auth-productivity-lab.git](https://github.com/patrickngumba-cmd/flask-auth-productivity-lab.git)
   cd flask-auth-productivity-lab


2. Install dependencies and activate the virtual environment:
   bash
   pipenv install
   pipenv shell
   
   *(Or using `venv` on Windows):*
   powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install flask flask-sqlalchemy flask-migrate flask-restful flask-bcrypt marshmallow faker pytest
   

3. Run database migrations and seed initial data:
   bash
   cd server
   flask --app app.py db upgrade head
   python seed.py
   

## Run Instructions

From the `server` folder, start the Flask API server (runs on `http://127.0.0.1:5555`):
bash
python app.py

Or using the Flask CLI:
bash
flask --app app.py run --port 5555


To run the automated tests from the `server` folder:
bash
pytest


## API Endpoints

### Authentication Endpoints
- **`POST /signup`** - Register a new user account (`username`, `password`), hash password with Bcrypt, and log the user into the session.
- **`POST /login`** - Authenticate an existing user (`username`, `password`) and store `user_id` in the session.
- **`GET /check_session`** (also **`GET /me`**) - Return the currently authenticated user's profile if a valid session exists.
- **`DELETE /logout`** - Clear the current user session and log out.

### Notes Resource Endpoints (Protected)
- **`GET /notes?page=<int>&per_page=<int>`** - Retrieve a paginated list of notes belonging only to the currently logged-in user.
- **`GET /notes/<id>`** - Retrieve a single note by ID if owned by the logged-in user.
- **`POST /notes`** - Create a new note (`title`, `content`) associated with the logged-in user.
- **`PATCH /notes/<id>`** - Update the `title` or `content` of an existing note owned by the logged-in user.
- **`DELETE /notes/<id>`** - Delete a note owned by the logged-in user.