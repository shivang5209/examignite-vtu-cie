<proposed_plan>
# Hybrid VTU CIE App Spec Pack

## Summary
Prepare a greenfield spec pack for a **VTU CSE-first student practice app** with these locked decisions:
- **Frontend:** Flutter student app
- **Content source:** admin-curated subject packs
- **Release focus:** practice answer submission and feedback
- **Backend:** FastAPI + PostgreSQL
- **Evaluation:** hybrid rubric + retrieval
- **Diagram support in v1:** recommend expected diagrams, no image grading

Create four Markdown specs plus one overview doc:
- `docs/product-overview.md`
- `docs/frontend-spec.md`
- `docs/backend-spec.md`
- `docs/database-spec.md`
- `docs/api-spec.md`

## Key Changes

### 1. `product-overview.md`
Document the product and end-to-end flow so the other specs share one vocabulary.
- Define target user: VTU CSE student preparing for CIE exams.
- Describe the primary flow: select subject -> pick/generate question -> write answer -> receive marks, missing points, ideal answer, and diagram suggestion.
- Fix v1 boundaries: admin-curated content only, typed answers only, no handwriting OCR scoring, no deep diagram grading, no multi-university support.
- State the academic model: `University -> Scheme -> Branch -> Semester -> Subject -> Module -> Topic -> Question -> Rubric -> Attempt`.
- Describe internal marks handling: questions may originate from 50-mark style papers, but displayed evaluation must normalize to the subject's practical internal-mark display target.

### 2. `frontend-spec.md`
Specify the Flutter student app screens, state, and user interactions.
- App sections: auth/onboarding, subject dashboard, question practice, answer editor, feedback screen, history/progress, profile/settings.
- Required screens:
  - subject list filtered by semester and subject
  - question picker with marks, module, and year tags
  - practice editor with timer, word count, and diagram recommendation area
  - feedback view with score, concept coverage, missing points, model answer, and source-backed feedback
  - attempt history with weak-topic indicators
- Define key UI models:
  - `SubjectCardVM`, `QuestionSummaryVM`, `PracticeSessionVM`, `AttemptFeedbackVM`, `ProgressSnapshotVM`
- Define app state transitions:
  - loading curated subject pack
  - starting practice session
  - draft autosave
  - answer submission
  - feedback retrieval
  - retry/rewrite flow
- Include UX rules:
  - show confidence/explanation only when grounded in retrieved notes/rubric
  - surface "diagram expected" as guidance, not a penalty-only warning
  - preserve prior attempts for comparison
- Keep admin tools out of Flutter v1; they belong to backend/admin later.

### 3. `backend-spec.md`
Define FastAPI services, orchestration, and evaluation flow.
- Organize backend into modules/services:
  - `auth`
  - `catalog`
  - `content_ingestion`
  - `question_bank`
  - `practice_sessions`
  - `evaluation`
  - `analytics`
- Describe ingestion pipeline:
  - admin uploads syllabus/notes/question banks
  - extraction service parses PDF text and metadata
  - classifier maps document to scheme/semester/subject/course code
  - chunker creates note/topic chunks
  - question extractor identifies question text, marks, unit, and year
  - rubric builder generates concept lists, mark splits, and diagram expectation
  - reviewer state marks pack as draft/reviewed/published
- Describe runtime evaluation flow:
  1. load question and stored rubric
  2. retrieve relevant chunks from subject notes/question bank
  3. generate grounded reference answer
  4. score answer by rubric concepts and coherence
  5. normalize marks for display
  6. persist attempt, evidence, and feedback payload
- Define failure handling:
  - missing rubric -> generate-on-read and flag for admin review
  - weak retrieval -> lower confidence and note limited source coverage
  - low OCR quality -> keep pack unpublished until reviewed
- Keep LLM usage bounded to extraction, rubric generation, grounded evaluation, and feedback phrasing; no freeform scoring without evidence.

### 4. `database-spec.md`
Define PostgreSQL schema and storage boundaries.
- Core relational tables:
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
- Add status/ownership fields where needed:
  - `subject_packs.status`: draft/review/published/archived
  - `documents.type`: syllabus/notes/question_bank/timetable
  - `question_bank_items.source_type`: extracted/manual/generated
- Define vectorized content storage:
  - either `content_chunks` table with `embedding` via pgvector
  - or separate vector collection keyed by `subject_id`, `topic_id`, `document_id`
- Required relationships:
  - each question belongs to one subject and may map to multiple topics
  - each rubric belongs to one question version
  - each attempt stores normalized score plus raw rubric score
  - feedback must reference evidence rows for explainability
- Include indexes for:
  - `subject_id + semester_id`
  - `question_bank_items(subject_id, marks, module_no)`
  - vector similarity on chunks
  - `answer_attempts(user_id, subject_id, created_at)`

### 5. `api-spec.md`
Define external API contracts for Flutter.
- Auth endpoints:
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `GET /me`
- Subject/catalog endpoints:
  - `GET /subjects`
  - `GET /subjects/{subjectId}`
  - `GET /subjects/{subjectId}/questions`
  - `GET /subjects/{subjectId}/progress`
- Practice endpoints:
  - `POST /practice-sessions`
  - `GET /practice-sessions/{sessionId}`
  - `POST /practice-sessions/{sessionId}/submit`
  - `GET /attempts/{attemptId}`
  - `GET /attempts/history`
- Feedback payload must include:
  - question metadata
  - raw and normalized score
  - concept coverage list
  - missed concepts
  - reference answer
  - diagram suggestion
  - source evidence snippets
- Admin/internal endpoints for later documentation:
  - `POST /admin/subject-packs`
  - `POST /admin/documents/upload`
  - `POST /admin/questions/extract`
  - `POST /admin/rubrics/generate`
  - `POST /admin/subject-packs/{id}/publish`
- Keep public student APIs read-heavy plus one submission endpoint; ingestion/admin APIs should be protected and separate.

## Test Plan
- Ingestion of a VTU syllabus PDF and question-bank PDF produces one valid published subject pack.
- Course-code and semester detection work for noisy file names and extracted text.
- A 10-mark theory question returns rubric-backed concept scoring and evidence references.
- Answer submission stores draft/session/attempt data without losing user text.
- Feedback response includes normalized marks, missing points, and a diagram recommendation when flagged by rubric.
- Student progress view aggregates attempts by subject and weak topics.
- API rejects practice for unpublished subject packs and returns clear error states.

## Assumptions
- Student app is English-only in v1.
- One admin workflow exists, but admin UI is not part of this first spec pack.
- Marks normalization policy will be documented as configurable per subject pack rather than hardcoded globally.
- Diagram support is text guidance only in v1; uploaded diagram images are out of scope.
- The Markdown files are product/engineering specs, not implementation code or generated OpenAPI/DDL exports.
</proposed_plan>
