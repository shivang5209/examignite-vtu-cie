from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    AttemptFeedbackResponse,
    CreatePracticeSessionRequest,
    PracticeSessionResponse,
    SubmitAnswerRequest,
)
from app.services.evaluation import evaluate_answer
from app.services import repository
from app.services.retrieval import retrieve_evidence

router = APIRouter()


@router.post("/practice-sessions", response_model=PracticeSessionResponse, status_code=status.HTTP_201_CREATED)
def create_practice_session(
    payload: CreatePracticeSessionRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> PracticeSessionResponse:
    subject = repository.get_subject(session, payload.subject_id)
    question = repository.get_question(session, payload.question_id)
    if subject is None or question is None or question.subject_id != payload.subject_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subject/question selection")
    practice_session = repository.create_practice_session(session, current_user.id, payload.subject_id, payload.question_id)
    return PracticeSessionResponse(
        id=practice_session.id,
        subjectId=practice_session.subject_id,
        questionId=practice_session.question_id,
        status=practice_session.status,
        createdAt=practice_session.created_at,
        submittedAt=practice_session.submitted_at,
    )


@router.get("/practice-sessions/{session_id}", response_model=PracticeSessionResponse)
def get_practice_session(
    session_id: str,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PracticeSessionResponse:
    practice_session = repository.get_practice_session(session, session_id)
    if practice_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice session not found")
    if practice_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session belongs to another user")
    return PracticeSessionResponse(
        id=practice_session.id,
        subjectId=practice_session.subject_id,
        questionId=practice_session.question_id,
        status=practice_session.status,
        createdAt=practice_session.created_at,
        submittedAt=practice_session.submitted_at,
    )


@router.post("/practice-sessions/{session_id}/submit", response_model=AttemptFeedbackResponse)
def submit_answer(
    session_id: str,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> AttemptFeedbackResponse:
    practice_session = repository.get_practice_session(session, session_id)
    if practice_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice session not found")
    if practice_session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session belongs to another user")

    question = repository.get_question(session, practice_session.question_id)
    subject = repository.get_subject(session, practice_session.subject_id)
    if question is None or subject is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is missing source data")

    rubric = repository.get_rubric(session, question.id)
    chunks = repository.get_subject_chunks(session, subject.id)
    chunk_pairs = [(chunk.id, chunk.chunk_text) for chunk in chunks]
    retrieved_evidence = retrieve_evidence(question.text, payload.answer_text, chunk_pairs, top_k=3)
    feedback = evaluate_answer(
        question=question,
        subject=subject,
        answer_text=payload.answer_text,
        rubric=rubric,
        retrieved_evidence=retrieved_evidence or question.evidence,
    )
    attempt = repository.add_attempt(session, practice_session, payload.answer_text, feedback)
    return AttemptFeedbackResponse(
        attemptId=attempt.id,
        questionId=feedback.question_id,
        scoreRaw=feedback.score_raw,
        scoreNormalized=feedback.score_normalized,
        missedConcepts=feedback.missed_concepts,
        conceptCoverage=feedback.concept_coverage,
        referenceAnswer=feedback.reference_answer,
        diagramSuggestion=feedback.diagram_suggestion,
        evidence=feedback.evidence,
        summary=feedback.summary,
        createdAt=feedback.created_at,
    )
