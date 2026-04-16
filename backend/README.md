# Backend Scaffold

This scaffold aligns with the Hybrid VTU CIE architecture plan.

## Stack
- FastAPI
- PostgreSQL
- pgvector

## Structure
- `app/main.py`: API bootstrap
- `app/core/config.py`: settings placeholder
- `app/api/routes`: endpoint modules
- `openapi/v1.yaml`: API contract skeleton
- `tests/test_api.py`: integration-style API tests

## Local commands
- Install dependencies: `pip install -r requirements.txt`
- Run migrations: `alembic upgrade head`
- Run API: `uvicorn app.main:app --reload`
- Run tests: `pytest -q`

## Demo credentials
- Student: `student@cie.app` / `student123`
- Admin: `admin@cie.app` / `admin123`

## Database workflow
- Default local DB is SQLite (`DATABASE_URL=sqlite:///./vtu_cie.db`).
- For an existing SQLite file created before Alembic, mark it as migrated once: `alembic stamp head`.
- For PostgreSQL, set `DATABASE_URL` in `.env` and run `alembic upgrade head`.
- Startup can auto-create and auto-seed in local mode (`AUTO_CREATE_SCHEMA=true`, `AUTO_SEED_DATA=true`).
- For production, set `AUTO_CREATE_SCHEMA=false` and `AUTO_SEED_DATA=false` and rely strictly on Alembic migrations.

## Current implementation
1. SQLAlchemy-backed persistence with SQLite default (`vtu_cie.db`) and startup seed data.
2. Seeded VTU-style subject catalog, question bank, and subject packs.
3. JWT auth with role-based access (`student`, `admin`) and protected endpoints.
4. Practice session creation and answer submission with concept-aware evaluation.
5. Evidence-backed feedback, attempt history, and subject progress snapshot endpoints.
6. Admin pack creation/publish + working upload/extract/rubric generation pipeline.
7. Retrieval-backed evidence from uploaded content chunks during evaluation.

## Admin ingestion flow
1. Login as admin and create a subject pack.
2. Upload `question_bank` and `notes` documents with `/admin/documents/upload`.
3. Run `/admin/questions/extract` for that subject pack.
4. Run `/admin/rubrics/generate` for that subject pack.
5. Publish the pack via `/admin/subject-packs/{id}/publish`.

## Next Implementation Steps
1. Replace simple token-overlap retrieval with pgvector embeddings.
2. Add OCR fallback for scanned PDFs and handwritten answer uploads.
3. Add full Flutter app (current web client is lightweight starter).
4. Move startup events to FastAPI lifespan and harden production deployment profiles.
