# Expense Splitter

## Backend

1. Create and activate the Python environment.
2. Install dependencies: `pip install -r requirements.txt` (or install Django and DRF manually).
3. Configure `backend/expense_manager/settings.py` with the local PostgreSQL credentials.
4. Run migrations: `python manage.py migrate`.
5. Start the server from `backend`: `python manage.py runserver`.

## Frontend

1. Change into `frontend`.
2. Install dependencies: `npm install`.
3. Start the Vite app: `npm run dev`.

## CSV Import

- Upload a CSV file to `POST /api/imports/run/`.
- The import endpoint returns an import summary and issue list.
- The app creates groups, users, expenses, and settlements from valid rows.

## Authentication

- Login with `POST /api/accounts/login/`.
- The frontend login page creates a user record if none exists and returns a token.

## Running locally

Backend:
1. Activate `backend/venv`.
2. Install Python dependencies: `python -m pip install -r requirements.txt`.
3. Run migrations: `python manage.py makemigrations && python manage.py migrate`.
4. Start the backend server: `python manage.py runserver`.

Frontend:
1. From `frontend`, install dependencies: `npm install`.
2. Start the frontend: `npm run dev`.

The frontend uses Vite proxy so requests to `/api/*` route to `http://localhost:8000`.
