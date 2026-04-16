# Database Spec (PostgreSQL)

## Summary
Relational core with evidence-backed evaluation records.
Vector retrieval is stored via `pgvector` in `content_chunks`.

## Core Tables
- `users`
- `admins`
- `universities`
- `schemes`
- `branches`
- `semesters`
- `subjects`
- `subject_packs`
- `documents`
- `topics`
- `question_bank_items`
- `rubrics`
- `practice_sessions`
- `answer_attempts`
- `attempt_feedback`
- `attempt_evidence`
- `progress_snapshots`
- `content_chunks`

## Key Status Fields
- `subject_packs.status`: `draft | review | published | archived`
- `documents.type`: `syllabus | notes | question_bank | timetable`
- `question_bank_items.source_type`: `extracted | manual | generated`

## Required Relationships
- A question belongs to one subject and maps to one or more topics.
- A rubric belongs to a question version.
- An attempt stores raw score and normalized score.
- Feedback links to one or more evidence entries.

## Recommended Indexes
- `(subject_id, semester_id)` on subject-facing query tables
- `(subject_id, marks, module_no)` on question bank
- vector similarity index on `content_chunks.embedding`
- `(user_id, subject_id, created_at)` on answer attempts

