from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class User:
    id: str
    name: str
    email: str
    role: str


@dataclass(slots=True)
class EvidenceSnippet:
    source_title: str
    snippet: str


@dataclass(slots=True)
class Question:
    id: str
    subject_id: str
    text: str
    marks: int
    module_no: int
    year: int
    cie_type: str
    diagram_expected: bool
    concepts: list[str]
    reference_answer: str
    evidence: list[EvidenceSnippet]


@dataclass(slots=True)
class Subject:
    id: str
    course_code: str
    title: str
    semester: int
    scheme: str
    credits: int
    marks_display: int
    status: str
    question_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SubjectPack:
    id: str
    subject_id: str
    title: str
    status: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class PracticeSession:
    id: str
    user_id: str
    subject_id: str
    question_id: str
    status: str
    created_at: datetime = field(default_factory=utc_now)
    submitted_at: datetime | None = None


@dataclass(slots=True)
class AttemptFeedback:
    attempt_id: str
    question_id: str
    score_raw: float
    score_normalized: float
    missed_concepts: list[str]
    concept_coverage: list[str]
    reference_answer: str
    diagram_suggestion: str
    evidence: list[EvidenceSnippet]
    summary: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class AnswerAttempt:
    id: str
    session_id: str
    user_id: str
    subject_id: str
    question_id: str
    answer_text: str
    feedback: AttemptFeedback
    created_at: datetime = field(default_factory=utc_now)
