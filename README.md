# ExamIgnite VTU CIE Portal

An AI-powered exam practice platform for VTU CSE students to prepare for CIE assessments through answer-writing practice, rubric-based evaluation, and progress tracking.

## Project Overview

ExamIgnite is a full-stack system designed around VTU-style internal exam preparation:

- Backend: FastAPI + SQLAlchemy + Alembic
- Frontend: lightweight web client (`frontend-web`)
- Authentication: JWT-based role-aware access (student/admin)
- Evaluation: rubric + retrieval-grounded feedback
- Ingestion: admin upload and question/rubric generation pipeline

The platform focuses on practical preparation:
- pick subject and question
- write answer
- receive normalized marks, missed concepts, and evidence-backed feedback
- track weak topics over time

## Core Features

- Real-time answer evaluation with normalized scoring
- Subject-wise question bank browsing (marks/module/year)
- Practice session lifecycle (`start session -> submit -> review`)
- Concept coverage and missed-concept feedback
- Evidence snippets and reference answer guidance
- Attempt history and subject progress insights
- Admin ingestion workflow for uploaded content
- Alembic migration support for reliable schema management

## Repository Structure

```text
CIE-studyapp/
|-- backend/
|   |-- app/
|   |   |-- api/routes/          # auth, catalog, practice, attempts, admin
|   |   |-- core/                # config + db session
|   |   |-- services/            # eval, retrieval, ingestion, security, seed, repository
|   |   |-- db_models.py         # SQLAlchemy models
|   |   |-- schemas.py           # request/response contracts
|   |   `-- main.py              # FastAPI app entrypoint
|   |-- alembic/                 # migrations
|   |-- tests/                   # API tests
|   |-- requirements.txt
|   `-- README.md
|-- frontend-web/
|   |-- index.html               # student UI shell
|   |-- style.css                # Scholarly Curator visual theme
|   `-- app.js                   # client state + API integration
|-- docs/                        # product/backend/db/api specs
|-- stitch_examignite_study_portal/  # Stitch reference exports (design source)
`-- README.md
```

## Technology Stack

### Backend

- Python 3.11+ (tested on 3.14 locally)
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

### Frontend

- HTML + CSS + vanilla JavaScript
- Google Fonts: Epilogue + Manrope
- Material Symbols (icon font)

### Storage

- Default: SQLite (`backend/vtu_cie.db`)
- Production-ready path: PostgreSQL via `DATABASE_URL`

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- `pip`
- PowerShell or terminal of choice

### 1. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure environment (optional for local default)

```bash
copy .env.example .env
```

Key settings (in `.env`):
- `DATABASE_URL` (default SQLite fallback works if omitted)
- startup seed/create flags (see `backend/.env.example`)

### 3. Apply migrations

```bash
alembic upgrade head
```

## Running the Application

### Backend (FastAPI)

From `backend/`:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Available at:
- API root: `http://127.0.0.1:8000`
- OpenAPI docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

### Frontend (Static server)

From `frontend-web/`:

```bash
python -m http.server 8001
```

Open:
- `http://localhost:8001/`
- or `http://127.0.0.1:8001/`

## Demo Credentials

- Student: `student@cie.app` / `student123`
- Admin: `admin@cie.app` / `admin123`

## Student Workflow

1. Login from frontend
2. Load semester subjects and questions
3. Choose a question and enter practice workspace
4. Start session
5. Submit answer
6. Review score, concept coverage, and evidence
7. Check history/progress and repeat weak areas

## Admin Workflow

1. Create or manage subject pack
2. Upload source document(s)
3. Extract questions
4. Generate rubrics
5. Publish pack for student usage

## API Overview

### Auth

- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`

### Catalog and Progress

- `GET /subjects`
- `GET /subjects/{subject_id}`
- `GET /subjects/{subject_id}/questions`
- `GET /subjects/{subject_id}/progress`

### Practice and Attempts

- `POST /practice-sessions`
- `GET /practice-sessions/{session_id}`
- `POST /practice-sessions/{session_id}/submit`
- `GET /attempts/history`
- `GET /attempts/{attempt_id}`

### Admin

- `POST /admin/subject-packs`
- `POST /admin/documents/upload`
- `POST /admin/questions/extract`
- `POST /admin/rubrics/generate`
- `POST /admin/subject-packs/{pack_id}/publish`

## Testing

From `backend/`:

```bash
pytest -q
```

Expected:
- all tests pass (current baseline: passing)

## Database and Migrations

- Alembic config: `backend/alembic.ini`
- Migration scripts: `backend/alembic/versions/`
- Initial schema migration already included

Typical commands:

```bash
alembic upgrade head
alembic revision -m "describe change" --autogenerate
alembic downgrade -1
```

## Frontend Theme Notes

The UI uses the Scholarly Curator visual direction:
- editorial typography hierarchy
- teal/blue/amber tonal system
- no-line sectioning preference (layering and tone over hard separators)
- bento-like hero + focus cards
- responsive behavior for desktop and mobile

The folder `stitch_examignite_study_portal/` contains reference exports used as visual source material, not runtime app logic.

## Troubleshooting

### Frontend not opening

- Ensure you started the static server in `frontend-web/`
- Keep that terminal window open
- Try both:
  - `http://localhost:8001/`
  - `http://127.0.0.1:8001/`

### Backend not reachable

- Confirm Uvicorn is running on port `8000`
- Check `http://127.0.0.1:8000/health`
- Ensure migrations are applied (`alembic upgrade head`)

### Login fails

- Verify backend is running
- Use seeded credentials listed above
- If seed disabled in env, enable local seed flags or seed manually

### Stale frontend styling

- Hard refresh browser (`Ctrl+Shift+R`)
- Confirm latest `frontend-web/style.css` is loaded

## Current Status

- Backend API implemented with auth, practice, progress, and admin ingestion routes
- DB persistence and migrations in place
- Student frontend integrated with live backend APIs
- Stitch-aligned UI theme applied to the web client

## Roadmap

- Add richer analytics endpoints (dashboard summary aggregation)
- Add persistent draft API (cross-device continuation)
- Expand question filtering server-side (`module`, `year`, `diagramExpected`)
- Add production deployment configs (frontend + backend)
- Add optional Flutter client aligned to same backend contracts

## License

Educational and project use.
