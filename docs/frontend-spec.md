# Flutter Frontend Spec (Student App)

## Summary
Flutter app focused on practice + feedback for VTU CSE subjects.
Admin tooling is not part of this app in v1.

## Core Screens
1. Auth and onboarding
2. Subject dashboard (filtered by semester)
3. Question picker (marks, module, year tags)
4. Practice editor (timer, word count, diagram expectation badge)
5. Feedback screen (score + coverage + missed points + model answer)
6. Attempt history and progress
7. Settings/profile

## View Models
- `SubjectCardVM`
- `QuestionSummaryVM`
- `PracticeSessionVM`
- `AttemptFeedbackVM`
- `ProgressSnapshotVM`

## State Transitions
1. Load curated subject packs.
2. Start practice session.
3. Autosave answer draft.
4. Submit answer.
5. Poll/fetch evaluated feedback.
6. Retry or rewrite answer.

## UX Rules
- Show explanation only with grounded evidence from retrieved sources.
- Show diagram expectation as guidance, not hard penalty-only messaging.
- Keep previous attempts available for side-by-side improvement tracking.

