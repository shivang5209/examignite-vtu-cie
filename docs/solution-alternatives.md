# Other Ways to Solve the Problem

## 1. Hybrid rubric plus retrieval
This is the current path in the codebase.
It works by linking each question to expected concepts, retrieving evidence from notes/question banks, and scoring answers against those concepts.

### Best when
- you want explainable feedback
- you have notes and question-bank PDFs
- you need a practical MVP quickly

## 2. Teacher-curated evaluation packs
Instead of relying mainly on AI-generated rubrics, teachers or toppers can upload:
- ideal answers
- must-include points
- common mistakes
- diagram expectations

### Best when
- you want strong trust from students
- a few key subjects matter most
- you can get faculty or topper help

## 3. Retrieval plus flashcard and test generator
The system can turn notes and question banks into:
- flashcards
- 2-mark and 5-mark quick checks
- 10-mark structured writing prompts
- module revision sheets

### Best when
- students need both memory support and long-answer practice
- you want stronger daily retention, not just mock evaluation

## 4. Handwritten answer OCR pipeline
Students upload written pages, OCR extracts text, and the evaluator scores the extracted answer.

### Best when
- the target behavior is actual exam writing
- students mostly practice on paper

### Main risk
- OCR quality drops on messy handwriting, diagrams, and mixed English/technical notation

## 5. Peer review plus AI moderation
Students review each other's answers using a simplified rubric, and AI checks whether the peer review seems reasonable.

### Best when
- you want low-cost scaling
- students benefit from reading other answers

### Main risk
- review quality can be noisy without strong rubrics

## 6. Fine-tuned subject scorer
Train a model using past answers, marks, and corrected scripts.

### Best when
- you have lots of labeled answer data
- you need subject-specific grading consistency

### Main risk
- high data and maintenance cost
- weaker explainability than retrieval-grounded scoring

## Recommended combined roadmap
1. Keep the current hybrid rubric + retrieval core.
2. Add teacher-curated ideal answers for high-frequency questions.
3. Add flashcard/test generation for daily use.
4. Add handwritten OCR only after typed-answer scoring is stable.
5. Consider model fine-tuning only after real attempt data accumulates.
