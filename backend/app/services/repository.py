from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import Select, delete, select
from sqlalchemy.orm import Session

from app.db_models import (
    AttemptRecord,
    ContentChunkRecord,
    DocumentRecord,
    PracticeSessionRecord,
    QuestionRecord,
    RubricRecord,
    SubjectPackRecord,
    SubjectRecord,
    UserRecord,
)
from app.models import AnswerAttempt, AttemptFeedback, EvidenceSnippet, PracticeSession, Question, Subject, SubjectPack, User


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    from app.services.security import verify_password

    record = session.scalar(select(UserRecord).where(UserRecord.email == email))
    if record is None:
        return None
    if not verify_password(password, record.password_hash):
        return None
    return _to_user(record)


def get_user(session: Session, user_id: str) -> User | None:
    record = session.get(UserRecord, user_id)
    return _to_user(record) if record is not None else None


def list_subjects(session: Session, semester: int | None = None) -> list[Subject]:
    query: Select[tuple[SubjectRecord]] = select(SubjectRecord).where(SubjectRecord.status == "published")
    if semester is not None:
        query = query.where(SubjectRecord.semester == semester)
    records = session.scalars(query.order_by(SubjectRecord.semester, SubjectRecord.course_code)).all()
    return [_to_subject(session, record) for record in records]


def get_subject(session: Session, subject_id: str) -> Subject | None:
    record = session.get(SubjectRecord, subject_id)
    return _to_subject(session, record) if record is not None else None


def list_questions(session: Session, subject_id: str, marks: int | None = None) -> list[Question]:
    query: Select[tuple[QuestionRecord]] = select(QuestionRecord).where(QuestionRecord.subject_id == subject_id)
    if marks is not None:
        query = query.where(QuestionRecord.marks == marks)
    records = session.scalars(query.order_by(QuestionRecord.module_no, QuestionRecord.year, QuestionRecord.id)).all()
    return [_to_question(record) for record in records]


def get_question(session: Session, question_id: str) -> Question | None:
    record = session.get(QuestionRecord, question_id)
    return _to_question(record) if record is not None else None


def replace_question_bank(session: Session, subject_id: str, questions: list[dict[str, object]]) -> int:
    existing_ids = session.scalars(select(QuestionRecord.id).where(QuestionRecord.subject_id == subject_id)).all()
    generated_ids: list[str] = []
    for idx, question in enumerate(questions, start=1):
        question_id = f"q-{subject_id}-{idx}-{uuid4().hex[:6]}"
        generated_ids.append(question_id)
        record = QuestionRecord(
            id=question_id,
            subject_id=subject_id,
            text=str(question["text"]),
            marks=int(question.get("marks", 10)),
            module_no=int(question.get("module_no", 1)),
            year=int(question.get("year", 2026)),
            cie_type="theory",
            diagram_expected=1 if bool(question.get("diagram_expected", False)) else 0,
            concepts_blob=json.dumps(list(question.get("concepts", []))),
            reference_answer=str(question.get("reference_answer", "Reference answer pending rubric generation.")),
            evidence_blob=json.dumps([]),
        )
        session.add(record)

    for old_id in existing_ids:
        if old_id not in generated_ids:
            session.execute(delete(RubricRecord).where(RubricRecord.question_id == old_id))
            session.execute(delete(QuestionRecord).where(QuestionRecord.id == old_id))
    session.commit()
    return len(generated_ids)


def create_practice_session(session: Session, user_id: str, subject_id: str, question_id: str) -> PracticeSession:
    record = PracticeSessionRecord(
        id=f"ps-{uuid4().hex[:10]}",
        user_id=user_id,
        subject_id=subject_id,
        question_id=question_id,
        status="in_progress",
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _to_practice_session(record)


def get_practice_session(session: Session, session_id: str) -> PracticeSession | None:
    record = session.get(PracticeSessionRecord, session_id)
    return _to_practice_session(record) if record is not None else None


def add_attempt(
    session: Session,
    practice_session: PracticeSession,
    answer_text: str,
    feedback: AttemptFeedback,
) -> AnswerAttempt:
    session_record = session.get(PracticeSessionRecord, practice_session.id)
    if session_record is None:
        raise ValueError("Practice session not found")

    attempt_record = AttemptRecord(
        id=feedback.attempt_id,
        session_id=practice_session.id,
        user_id=practice_session.user_id,
        subject_id=practice_session.subject_id,
        question_id=practice_session.question_id,
        answer_text=answer_text,
        score_raw=feedback.score_raw,
        score_normalized=feedback.score_normalized,
        missed_concepts_blob=json.dumps(feedback.missed_concepts),
        concept_coverage_blob=json.dumps(feedback.concept_coverage),
        reference_answer=feedback.reference_answer,
        diagram_suggestion=feedback.diagram_suggestion,
        evidence_blob=json.dumps([{"source_title": e.source_title, "snippet": e.snippet} for e in feedback.evidence]),
        summary=feedback.summary,
        created_at=feedback.created_at,
    )
    session_record.status = "submitted"
    session_record.submitted_at = feedback.created_at
    session.add(attempt_record)
    session.commit()
    session.refresh(attempt_record)
    return _to_attempt(attempt_record)


def get_attempt(session: Session, attempt_id: str) -> AnswerAttempt | None:
    record = session.get(AttemptRecord, attempt_id)
    return _to_attempt(record) if record is not None else None


def list_attempts_for_user(session: Session, user_id: str) -> list[AnswerAttempt]:
    records = session.scalars(
        select(AttemptRecord).where(AttemptRecord.user_id == user_id).order_by(AttemptRecord.created_at.desc())
    ).all()
    return [_to_attempt(record) for record in records]


def create_subject_pack(session: Session, subject_id: str, title: str) -> SubjectPack:
    record = SubjectPackRecord(
        id=f"pack-{uuid4().hex[:8]}",
        subject_id=subject_id,
        title=title,
        status="draft",
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return _to_subject_pack(record)


def publish_subject_pack(session: Session, pack_id: str) -> SubjectPack | None:
    record = session.get(SubjectPackRecord, pack_id)
    if record is None:
        return None
    record.status = "published"
    session.commit()
    session.refresh(record)
    return _to_subject_pack(record)


def get_subject_pack(session: Session, pack_id: str) -> SubjectPack | None:
    record = session.get(SubjectPackRecord, pack_id)
    return _to_subject_pack(record) if record is not None else None


def create_document(
    session: Session,
    subject_pack_id: str,
    subject_id: str,
    uploaded_by: str,
    document_type: str,
    filename: str,
    file_path: str,
    extracted_text: str,
) -> str:
    document_id = f"doc-{uuid4().hex[:10]}"
    record = DocumentRecord(
        id=document_id,
        subject_pack_id=subject_pack_id,
        subject_id=subject_id,
        uploaded_by=uploaded_by,
        document_type=document_type,
        filename=filename,
        file_path=file_path,
        extracted_text=extracted_text,
        status="processed",
    )
    session.add(record)
    session.commit()
    return document_id


def get_documents_by_pack(session: Session, subject_pack_id: str, document_type: str | None = None) -> list[DocumentRecord]:
    query: Select[tuple[DocumentRecord]] = select(DocumentRecord).where(DocumentRecord.subject_pack_id == subject_pack_id)
    if document_type is not None:
        query = query.where(DocumentRecord.document_type == document_type)
    return session.scalars(query.order_by(DocumentRecord.created_at.desc())).all()


def replace_chunks_for_document(session: Session, document_id: str, subject_id: str, chunks: list[str]) -> int:
    session.execute(delete(ContentChunkRecord).where(ContentChunkRecord.document_id == document_id))
    records = [
        ContentChunkRecord(
            id=f"chk-{uuid4().hex[:10]}",
            document_id=document_id,
            subject_id=subject_id,
            chunk_text=chunk,
            token_count=len(chunk.split()),
        )
        for chunk in chunks
    ]
    session.add_all(records)
    session.commit()
    return len(records)


def get_subject_chunks(session: Session, subject_id: str) -> list[ContentChunkRecord]:
    return session.scalars(select(ContentChunkRecord).where(ContentChunkRecord.subject_id == subject_id)).all()


def set_question_evidence(session: Session, question_id: str, evidence: list[EvidenceSnippet]) -> None:
    question = session.get(QuestionRecord, question_id)
    if question is None:
        return
    question.evidence_blob = json.dumps([{"source_title": e.source_title, "snippet": e.snippet} for e in evidence])
    session.commit()


def save_rubric(
    session: Session,
    question_id: str,
    concepts: list[str],
    mark_split: dict[str, float],
    diagram_expected: bool,
    source: str = "heuristic",
) -> None:
    session.execute(delete(RubricRecord).where(RubricRecord.question_id == question_id))
    record = RubricRecord(
        id=f"rub-{uuid4().hex[:10]}",
        question_id=question_id,
        concepts_blob=json.dumps(concepts),
        mark_split_blob=json.dumps(mark_split),
        diagram_expected=1 if diagram_expected else 0,
        source=source,
    )
    session.add(record)
    session.commit()


def get_rubric(session: Session, question_id: str) -> dict[str, object] | None:
    record = session.scalar(select(RubricRecord).where(RubricRecord.question_id == question_id))
    if record is None:
        return None
    return {
        "concepts": json.loads(record.concepts_blob),
        "mark_split": json.loads(record.mark_split_blob),
        "diagram_expected": bool(record.diagram_expected),
        "source": record.source,
    }


def _to_user(record: UserRecord) -> User:
    return User(id=record.id, name=record.name, email=record.email, role=record.role)


def _to_subject(session: Session, record: SubjectRecord) -> Subject:
    question_ids = session.scalars(select(QuestionRecord.id).where(QuestionRecord.subject_id == record.id)).all()
    return Subject(
        id=record.id,
        course_code=record.course_code,
        title=record.title,
        semester=record.semester,
        scheme=record.scheme,
        credits=record.credits,
        marks_display=record.marks_display,
        status=record.status,
        question_ids=list(question_ids),
    )


def _to_question(record: QuestionRecord) -> Question:
    evidence_payload = json.loads(record.evidence_blob or "[]")
    return Question(
        id=record.id,
        subject_id=record.subject_id,
        text=record.text,
        marks=record.marks,
        module_no=record.module_no,
        year=record.year,
        cie_type=record.cie_type,
        diagram_expected=bool(record.diagram_expected),
        concepts=json.loads(record.concepts_blob or "[]"),
        reference_answer=record.reference_answer,
        evidence=[EvidenceSnippet(**item) for item in evidence_payload],
    )


def _to_practice_session(record: PracticeSessionRecord) -> PracticeSession:
    return PracticeSession(
        id=record.id,
        user_id=record.user_id,
        subject_id=record.subject_id,
        question_id=record.question_id,
        status=record.status,
        created_at=record.created_at,
        submitted_at=record.submitted_at,
    )


def _to_subject_pack(record: SubjectPackRecord) -> SubjectPack:
    return SubjectPack(
        id=record.id,
        subject_id=record.subject_id,
        title=record.title,
        status=record.status,
        created_at=record.created_at,
    )


def _to_attempt(record: AttemptRecord) -> AnswerAttempt:
    evidence_payload = json.loads(record.evidence_blob or "[]")
    feedback = AttemptFeedback(
        attempt_id=record.id,
        question_id=record.question_id,
        score_raw=record.score_raw,
        score_normalized=record.score_normalized,
        missed_concepts=json.loads(record.missed_concepts_blob or "[]"),
        concept_coverage=json.loads(record.concept_coverage_blob or "[]"),
        reference_answer=record.reference_answer,
        diagram_suggestion=record.diagram_suggestion,
        evidence=[EvidenceSnippet(**item) for item in evidence_payload],
        summary=record.summary,
        created_at=record.created_at,
    )
    return AnswerAttempt(
        id=record.id,
        session_id=record.session_id,
        user_id=record.user_id,
        subject_id=record.subject_id,
        question_id=record.question_id,
        answer_text=record.answer_text,
        feedback=feedback,
        created_at=record.created_at,
    )
