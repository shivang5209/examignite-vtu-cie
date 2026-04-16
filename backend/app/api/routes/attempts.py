from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AttemptFeedbackResponse
from app.services import repository

router = APIRouter()


@router.get("/attempts/history", response_model=list[AttemptFeedbackResponse])
def list_attempt_history(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> list[AttemptFeedbackResponse]:
    attempts = repository.list_attempts_for_user(session, current_user.id)
    attempts = sorted(attempts, key=lambda item: item.created_at, reverse=True)
    return [
        AttemptFeedbackResponse(
            attemptId=attempt.id,
            questionId=attempt.feedback.question_id,
            scoreRaw=attempt.feedback.score_raw,
            scoreNormalized=attempt.feedback.score_normalized,
            missedConcepts=attempt.feedback.missed_concepts,
            conceptCoverage=attempt.feedback.concept_coverage,
            referenceAnswer=attempt.feedback.reference_answer,
            diagramSuggestion=attempt.feedback.diagram_suggestion,
            evidence=attempt.feedback.evidence,
            summary=attempt.feedback.summary,
            createdAt=attempt.feedback.created_at,
        )
        for attempt in attempts
    ]


@router.get("/attempts/{attempt_id}", response_model=AttemptFeedbackResponse)
def get_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session),
) -> AttemptFeedbackResponse:
    attempt = repository.get_attempt(session, attempt_id)
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Attempt belongs to another user")
    feedback = attempt.feedback
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
