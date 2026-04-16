from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ProgressSnapshot, QuestionSummary, SubjectDetail, SubjectSummary
from app.services import repository

router = APIRouter()


@router.get("/subjects", response_model=list[SubjectSummary])
def list_subjects(
    semester: int | None = Query(default=None),
    session: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
) -> list[SubjectSummary]:
    subjects = repository.list_subjects(session, semester=semester)
    return [
        SubjectSummary(
            id=subject.id,
            courseCode=subject.course_code,
            title=subject.title,
            semester=subject.semester,
            scheme=subject.scheme,
            credits=subject.credits,
            marksDisplay=subject.marks_display,
            totalQuestions=len(subject.question_ids),
        )
        for subject in subjects
    ]


@router.get("/subjects/{subject_id}", response_model=SubjectDetail)
def get_subject(
    subject_id: str,
    session: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
) -> SubjectDetail:
    subject = repository.get_subject(session, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return SubjectDetail(
        id=subject.id,
        courseCode=subject.course_code,
        title=subject.title,
        semester=subject.semester,
        scheme=subject.scheme,
        credits=subject.credits,
        marksDisplay=subject.marks_display,
        totalQuestions=len(subject.question_ids),
        status=subject.status,
    )


@router.get("/subjects/{subject_id}/questions", response_model=list[QuestionSummary])
def list_questions(
    subject_id: str,
    marks: int | None = Query(default=None),
    session: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
) -> list[QuestionSummary]:
    subject = repository.get_subject(session, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return [
        QuestionSummary(
            id=question.id,
            marks=question.marks,
            moduleNo=question.module_no,
            year=question.year,
            cieType=question.cie_type,
            diagramExpected=question.diagram_expected,
            text=question.text,
        )
        for question in repository.list_questions(session, subject_id, marks=marks)
    ]


@router.get("/subjects/{subject_id}/progress", response_model=ProgressSnapshot)
def subject_progress(
    subject_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProgressSnapshot:
    subject = repository.get_subject(session, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    attempts = [attempt for attempt in repository.list_attempts_for_user(session, current_user.id) if attempt.subject_id == subject_id]
    average = round(
        sum(attempt.feedback.score_normalized for attempt in attempts) / len(attempts),
        2,
    ) if attempts else 0.0

    missed_counter: dict[str, int] = {}
    for attempt in attempts:
        for concept in attempt.feedback.missed_concepts:
            missed_counter[concept] = missed_counter.get(concept, 0) + 1
    weak_topics = [
        concept for concept, _count in sorted(missed_counter.items(), key=lambda item: (-item[1], item[0]))[:3]
    ]
    return ProgressSnapshot(
        subjectId=subject_id,
        attemptsCount=len(attempts),
        averageNormalizedScore=average,
        weakTopics=weak_topics,
    )
