# Backend Spec (FastAPI + PostgreSQL)

## Summary
Backend provides ingestion, catalog, practice, evaluation, and progress APIs for the Flutter app.
Evaluation uses hybrid rubric + retrieval, with explicit evidence references.

## Services / Modules
- `auth`
- `catalog`
- `content_ingestion`
- `question_bank`
- `practice_sessions`
- `evaluation`
- `analytics`

## Ingestion Pipeline
1. Admin uploads syllabus/notes/question bank files.
2. Extract text + metadata from files.
3. Classify scheme/semester/subject/course code.
4. Chunk notes into retrievable units.
5. Extract questions (text, marks, module, year).
6. Build/refresh rubrics (concepts, mark split, diagram expected).
7. Publish subject pack after review.

## Runtime Evaluation Pipeline
1. Load question + rubric.
2. Retrieve relevant chunks from subject material.
3. Generate grounded reference answer.
4. Score concept coverage and writing coherence.
5. Normalize score for subject display rule.
6. Persist attempt, evidence, and feedback payload.

## Failure Handling
- Missing rubric: generate-on-read and flag admin review.
- Weak retrieval quality: return lower confidence + limited evidence warning.
- Poor extraction quality: keep subject pack unpublished.

