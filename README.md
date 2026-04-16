# ExamIgnite VTU CIE

AI-powered VTU CSE exam-practice platform for CIE preparation.

It includes:
- FastAPI backend with JWT auth, role-based access, Alembic migrations, and SQLAlchemy persistence
- Admin ingestion pipeline (upload -> extract -> question generation -> rubric generation)
- Student practice flow (start session -> submit answer -> feedback with evidence)
- Lightweight web starter frontend for immediate usage

## Repository structure

- `backend/`: API, DB models, migrations, tests
- `frontend-web/`: quick web UI client
- `docs/`: architecture, API, DB, and product docs

## Quick start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

### 2. Frontend web starter

Open `frontend-web/index.html` in your browser.

## Demo credentials

- Student: `student@cie.app` / `student123`
- Admin: `admin@cie.app` / `admin123`

## Core API flow

1. Student logs in (`/auth/login`)
2. Student loads subjects/questions (`/subjects`, `/subjects/{id}/questions`)
3. Student starts session and submits answer (`/practice-sessions`, `/practice-sessions/{id}/submit`)
4. Student checks attempts and progress (`/attempts/history`, `/subjects/{id}/progress`)
5. Admin uploads and processes content (`/admin/documents/upload`, `/admin/questions/extract`, `/admin/rubrics/generate`)

## Migrations and environment

- Migration config: `backend/alembic.ini`
- Env template: `backend/.env.example`
- Default DB: SQLite (`sqlite:///./vtu_cie.db`)
- For PostgreSQL, set `DATABASE_URL` and run `alembic upgrade head`

## Status

Current backend test suite passes with `pytest -q`.
