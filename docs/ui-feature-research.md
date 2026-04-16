# UI and Feature Research

Research date: 2026-04-16

## Product patterns worth adapting

### 1. "Explain my answer" as a first-class action
Inspired by Duolingo's "Explain My Answer" flow, the app should not stop at marks.
Each evaluated answer should have a dedicated explanation drawer that tells the student why marks were lost and what concept or exam-writing rule caused the loss.

### 2. Revision loop, not one-shot scoring
Khan Academy Writing Coach emphasizes highlighted feedback, clarifying questions, exemplar writing, and a second review after revision.
For this app, feedback should support:
- a short overall summary
- rubric point highlights
- "rewrite this answer" mode
- "show a better exam-style paragraph" mode

### 3. Course-personalized home screen
Pearson Study Prep personalizes content after syllabus upload.
That maps well to a VTU app home screen with:
- current semester subjects
- weak modules
- likely repeated 10-mark topics
- next recommended practice question

### 4. Adaptive tutoring over static question banks
Quizlet's Q-Chat used adaptive questions grounded in study materials.
For this product, the tutor mode should ask follow-up viva-style prompts after submission, especially when a student misses core concepts.

### 5. Progress-driven practice
Brilliant focuses on concept mastery, adaptive pacing, and interactive feedback.
The app should track concept-level mastery, not just average marks, so students can see weak areas such as "normalization" or "shortest path complexity."

### 6. Habit and motivation loops
Duolingo's streak and friend-streak work shows that daily commitment and social accountability increase return behavior.
For this app, practical low-cost habit features are:
- daily practice streak
- "one 10-mark answer today" prompt
- classmate comparison only if privacy-safe
- module completion badges

## UI direction for the first strong version

### Home
- Semester-first subject shelf with bold course codes and internal-mark targets.
- A "Practice now" card that jumps directly into the next weak topic.
- A compact streak/progress strip instead of a generic dashboard chart wall.

### Practice screen
- Large question prompt with marks and module chips at the top.
- Answer editor in the main view.
- Collapsible "what examiners expect" panel that appears only after submission.
- Diagram guidance card when a question is diagram-heavy.

### Feedback screen
- Split into four blocks:
  - score and confidence
  - covered concepts
  - missed concepts
  - improved answer
- Evidence snippets should look like source cards, not plain text dumps.
- Keep one clear "Try again" button above the fold.

### Visual style
- Use a warm, high-contrast academic palette rather than generic purple AI gradients.
- Prefer expressive but serious typography.
- Use module colors and subject accents for scannability.
- Animate progress and streak changes, not every card on the screen.

## Features to implement next
1. Weak-topic recommendation engine
2. Rewrite and resubmit loop
3. Diagram expectation card
4. Subject-level streak and consistency tracking
5. Teacher-curated ideal answers for repeated questions
6. Viva follow-up mode after written answer submission
