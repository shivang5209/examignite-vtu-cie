from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(alias="refreshToken", min_length=8)

    model_config = ConfigDict(populate_by_name=True)


class AuthTokens(BaseModel):
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    token_type: str = Field(alias="tokenType", default="bearer")
    expires_in: int = Field(alias="expiresIn")

    model_config = ConfigDict(populate_by_name=True)


class UserProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class SubjectSummary(BaseModel):
    id: str
    course_code: str = Field(alias="courseCode")
    title: str
    semester: int
    scheme: str
    credits: int
    marks_display: int = Field(alias="marksDisplay")
    total_questions: int = Field(alias="totalQuestions")

    model_config = ConfigDict(populate_by_name=True)


class SubjectDetail(SubjectSummary):
    status: str


class QuestionSummary(BaseModel):
    id: str
    marks: int
    module_no: int = Field(alias="moduleNo")
    year: int
    cie_type: str = Field(alias="cieType")
    diagram_expected: bool = Field(alias="diagramExpected")
    text: str

    model_config = ConfigDict(populate_by_name=True)


class ProgressSnapshot(BaseModel):
    subject_id: str = Field(alias="subjectId")
    attempts_count: int = Field(alias="attemptsCount")
    average_normalized_score: float = Field(alias="averageNormalizedScore")
    weak_topics: list[str] = Field(alias="weakTopics")

    model_config = ConfigDict(populate_by_name=True)


class CreatePracticeSessionRequest(BaseModel):
    subject_id: str = Field(alias="subjectId")
    question_id: str = Field(alias="questionId")

    model_config = ConfigDict(populate_by_name=True)


class PracticeSessionResponse(BaseModel):
    id: str
    subject_id: str = Field(alias="subjectId")
    question_id: str = Field(alias="questionId")
    status: str
    created_at: datetime = Field(alias="createdAt")
    submitted_at: datetime | None = Field(alias="submittedAt")

    model_config = ConfigDict(populate_by_name=True)


class SubmitAnswerRequest(BaseModel):
    answer_text: str = Field(alias="answerText", min_length=10)

    model_config = ConfigDict(populate_by_name=True)


class EvidenceResponse(BaseModel):
    source_title: str = Field(alias="sourceTitle")
    snippet: str

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class AttemptFeedbackResponse(BaseModel):
    attempt_id: str = Field(alias="attemptId")
    question_id: str = Field(alias="questionId")
    score_raw: float = Field(alias="scoreRaw")
    score_normalized: float = Field(alias="scoreNormalized")
    missed_concepts: list[str] = Field(alias="missedConcepts")
    concept_coverage: list[str] = Field(alias="conceptCoverage")
    reference_answer: str = Field(alias="referenceAnswer")
    diagram_suggestion: str = Field(alias="diagramSuggestion")
    evidence: list[EvidenceResponse]
    summary: str
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class SubjectPackCreateRequest(BaseModel):
    subject_id: str = Field(alias="subjectId")
    title: str

    model_config = ConfigDict(populate_by_name=True)


class SubjectPackResponse(BaseModel):
    id: str
    subject_id: str = Field(alias="subjectId")
    title: str
    status: str
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)


class AdminActionResponse(BaseModel):
    message: str
    resource_id: str | None = Field(default=None, alias="resourceId")
    metadata: dict[str, object] | None = None

    model_config = ConfigDict(populate_by_name=True)


class ExtractQuestionsRequest(BaseModel):
    subject_pack_id: str = Field(alias="subjectPackId")

    model_config = ConfigDict(populate_by_name=True)


class GenerateRubricsRequest(BaseModel):
    subject_pack_id: str = Field(alias="subjectPackId")

    model_config = ConfigDict(populate_by_name=True)
