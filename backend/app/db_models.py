from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255), default="")


class SubjectRecord(Base):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    course_code: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(255))
    semester: Mapped[int] = mapped_column(Integer, index=True)
    scheme: Mapped[str] = mapped_column(String(20))
    credits: Mapped[int] = mapped_column(Integer)
    marks_display: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), index=True)

    questions: Mapped[list["QuestionRecord"]] = relationship(back_populates="subject")


class QuestionRecord(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    marks: Mapped[int] = mapped_column(Integer, index=True)
    module_no: Mapped[int] = mapped_column(Integer, index=True)
    year: Mapped[int] = mapped_column(Integer)
    cie_type: Mapped[str] = mapped_column(String(30))
    diagram_expected: Mapped[int] = mapped_column(Integer, default=0)
    concepts_blob: Mapped[str] = mapped_column(Text)
    reference_answer: Mapped[str] = mapped_column(Text)
    evidence_blob: Mapped[str] = mapped_column(Text)

    subject: Mapped[SubjectRecord] = relationship(back_populates="questions")


class SubjectPackRecord(Base):
    __tablename__ = "subject_packs"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PracticeSessionRecord(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class AttemptRecord(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("practice_sessions.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), index=True)
    answer_text: Mapped[str] = mapped_column(Text)
    score_raw: Mapped[float] = mapped_column(Float)
    score_normalized: Mapped[float] = mapped_column(Float)
    missed_concepts_blob: Mapped[str] = mapped_column(Text)
    concept_coverage_blob: Mapped[str] = mapped_column(Text)
    reference_answer: Mapped[str] = mapped_column(Text)
    diagram_suggestion: Mapped[str] = mapped_column(Text)
    evidence_blob: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    subject_pack_id: Mapped[str] = mapped_column(ForeignKey("subject_packs.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    uploaded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(30), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(Text)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ContentChunkRecord(Base):
    __tablename__ = "content_chunks"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), index=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), index=True)
    chunk_text: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RubricRecord(Base):
    __tablename__ = "rubrics"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id"), index=True)
    concepts_blob: Mapped[str] = mapped_column(Text)
    mark_split_blob: Mapped[str] = mapped_column(Text)
    diagram_expected: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(30), default="heuristic")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
