# Project X Backend

Production-oriented FastAPI backend scaffold for Big Mama Restaurant's food ordering platform.

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- JWT authentication
- Paystack integration points
- Supabase Storage integration points

## Run

1. Create a virtual environment.
```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```
2. Install dependencies from `requirements.txt`.
```powershell
pip install -r requirements.txt
```
3. Copy `.env.example` to `.env`.
4. Create the database schema.

Recommended with Alembic:
```powershell
alembic upgrade head
```

Quick bootstrap option:
```powershell
python -m app.scripts.init_db
```

5. Start the API.
```powershell
uvicorn app.main:app --reload
```

## Notes

- This codebase includes the layered architecture scaffold, database models, service layer, and API contracts.
- External integrations like live Paystack verification, Supabase Storage operations, SMTP, and SMS sending are scaffolded for later completion.
- For Supabase Postgres, make sure `DATABASE_URL` uses the `postgresql+psycopg://...?...sslmode=require` format.
