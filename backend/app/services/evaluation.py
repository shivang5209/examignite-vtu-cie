from __future__ import annotations

from uuid import uuid4

from app.models import AttemptFeedback, EvidenceSnippet, Question, Subject, utc_now


def evaluate_answer(
    question: Question,
    subject: Subject,
    answer_text: str,
    rubric: dict[str, object] | None = None,
    retrieved_evidence: list[EvidenceSnippet] | None = None,
) -> AttemptFeedback:
    expected_concepts = list(rubric["concepts"]) if rubric and rubric.get("concepts") else question.concepts
    normalized_answer = answer_text.lower()
    covered = [concept for concept in expected_concepts if _concept_present(concept, normalized_answer)]
    missed = [concept for concept in expected_concepts if concept not in covered]

    coverage_ratio = len(covered) / max(len(expected_concepts), 1)
    structure_bonus = 0.1 if len(answer_text.split()) >= 80 else 0.0
    raw_score = round(min(question.marks, question.marks * (coverage_ratio + structure_bonus)), 2)
    normalized_score = round((raw_score / question.marks) * subject.marks_display, 2)

    evidence_source = retrieved_evidence or question.evidence
    evidence = _select_evidence(evidence_source, covered, missed)
    diagram_suggestion = (
        "Include a stepwise graph or flow diagram showing vertex selection and edge relaxation."
        if (rubric and bool(rubric.get("diagram_expected"))) or question.diagram_expected
        else "No diagram is essential; use a table or example only if it improves clarity."
    )

    summary = _build_summary(covered, missed, question.diagram_expected)
    return AttemptFeedback(
        attempt_id=f"att-{uuid4().hex[:10]}",
        question_id=question.id,
        score_raw=raw_score,
        score_normalized=normalized_score,
        missed_concepts=missed,
        concept_coverage=covered,
        reference_answer=question.reference_answer,
        diagram_suggestion=diagram_suggestion,
        evidence=evidence,
        summary=summary,
        created_at=utc_now(),
    )


def _select_evidence(
    evidence: list[EvidenceSnippet],
    covered: list[str],
    missed: list[str],
) -> list[EvidenceSnippet]:
    if covered and missed:
        return evidence[:2]
    if covered:
        return evidence[:1]
    return evidence


def _concept_present(concept: str, normalized_answer: str) -> bool:
    aliases = {
        "greedy choice": ["greedy choice", "greedy", "greedy method"],
        "priority queue": ["priority queue", "min heap", "heap"],
        "shortest path": ["shortest path", "minimum path"],
        "time complexity": ["time complexity", "complexity", "big o", "o("],
        "functional dependency": ["functional dependency", "fd"],
    }
    for candidate in aliases.get(concept, [concept.lower()]):
        if candidate in normalized_answer:
            return True
    return False


def _build_summary(covered: list[str], missed: list[str], diagram_expected: bool) -> str:
    if not covered:
        base = "The answer needs more direct subject terminology and core points from the expected rubric."
    elif missed:
        base = "The answer covers some expected ideas but misses a few scoring concepts that would lift the mark."
    else:
        base = "The answer covers the expected concepts well and reads like a strong CIE response."

    if diagram_expected:
        return f"{base} Add a small supporting diagram or flow representation to make the explanation exam-ready."
    return base
