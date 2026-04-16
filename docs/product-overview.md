# Hybrid VTU CIE App - Product Overview

## Summary
This product is a VTU CSE-first student practice app for CIE preparation.
Students select a subject, practice with curated questions, submit typed answers, and receive rubric-grounded feedback.

## Target User
- VTU CSE student preparing for internal (CIE) exams.

## Primary User Flow
1. Student logs in and picks semester and subject.
2. Student opens a curated question or generated practice question.
3. Student writes a typed answer.
4. System evaluates against rubric + retrieved course material.
5. Student sees marks, missing concepts, improved answer, and diagram guidance (if expected).

## V1 Boundaries
- Admin-curated content only.
- Typed answers only (no handwriting OCR-based grading).
- Diagram recommendation only (no diagram image grading).
- VTU CSE scope only (no multi-university in v1).

## Academic Model
`University -> Scheme -> Branch -> Semester -> Subject -> Module -> Topic -> Question -> Rubric -> Attempt`

## Marks Handling
Questions may come from 50-mark style papers, but displayed score is normalized per subject internal-mark display rule (for example, out of 10 or 15 where configured).

