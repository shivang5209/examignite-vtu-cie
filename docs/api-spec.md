# API Spec (v1)

## Summary
Public student APIs are read-heavy plus one submission action.
Admin ingestion/publish APIs are protected and separate.

## Auth APIs
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /me`

## Subject and Catalog APIs
- `GET /subjects`
- `GET /subjects/{subjectId}`
- `GET /subjects/{subjectId}/questions`
- `GET /subjects/{subjectId}/progress`

## Practice and Attempt APIs
- `POST /practice-sessions`
- `GET /practice-sessions/{sessionId}`
- `POST /practice-sessions/{sessionId}/submit`
- `GET /attempts/{attemptId}`
- `GET /attempts/history`

## Feedback Payload Requirements
- Question metadata
- Raw score and normalized score
- Concept coverage
- Missed concepts
- Reference answer
- Diagram suggestion
- Evidence snippets

## Admin APIs (Protected)
- `POST /admin/subject-packs`
- `POST /admin/documents/upload`
- `POST /admin/questions/extract`
- `POST /admin/rubrics/generate`
- `POST /admin/subject-packs/{id}/publish`

