"""initial schema

Revision ID: 20260416_01
Revises: 
Create Date: 2026-04-16 15:05:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260416_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "subjects",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("course_code", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column("scheme", sa.String(length=20), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False),
        sa.Column("marks_display", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subjects_course_code"), "subjects", ["course_code"], unique=False)
    op.create_index(op.f("ix_subjects_semester"), "subjects", ["semester"], unique=False)
    op.create_index(op.f("ix_subjects_status"), "subjects", ["status"], unique=False)

    op.create_table(
        "questions",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=50), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("module_no", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("cie_type", sa.String(length=30), nullable=False),
        sa.Column("diagram_expected", sa.Integer(), nullable=False),
        sa.Column("concepts_blob", sa.Text(), nullable=False),
        sa.Column("reference_answer", sa.Text(), nullable=False),
        sa.Column("evidence_blob", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_questions_marks"), "questions", ["marks"], unique=False)
    op.create_index(op.f("ix_questions_module_no"), "questions", ["module_no"], unique=False)
    op.create_index(op.f("ix_questions_subject_id"), "questions", ["subject_id"], unique=False)

    op.create_table(
        "subject_packs",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subject_packs_status"), "subject_packs", ["status"], unique=False)
    op.create_index(op.f("ix_subject_packs_subject_id"), "subject_packs", ["subject_id"], unique=False)

    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=50), nullable=False),
        sa.Column("subject_id", sa.String(length=50), nullable=False),
        sa.Column("question_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_practice_sessions_question_id"), "practice_sessions", ["question_id"], unique=False)
    op.create_index(op.f("ix_practice_sessions_status"), "practice_sessions", ["status"], unique=False)
    op.create_index(op.f("ix_practice_sessions_subject_id"), "practice_sessions", ["subject_id"], unique=False)
    op.create_index(op.f("ix_practice_sessions_user_id"), "practice_sessions", ["user_id"], unique=False)

    op.create_table(
        "attempts",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("session_id", sa.String(length=80), nullable=False),
        sa.Column("user_id", sa.String(length=50), nullable=False),
        sa.Column("subject_id", sa.String(length=50), nullable=False),
        sa.Column("question_id", sa.String(length=80), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("score_raw", sa.Float(), nullable=False),
        sa.Column("score_normalized", sa.Float(), nullable=False),
        sa.Column("missed_concepts_blob", sa.Text(), nullable=False),
        sa.Column("concept_coverage_blob", sa.Text(), nullable=False),
        sa.Column("reference_answer", sa.Text(), nullable=False),
        sa.Column("diagram_suggestion", sa.Text(), nullable=False),
        sa.Column("evidence_blob", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["practice_sessions.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_attempts_question_id"), "attempts", ["question_id"], unique=False)
    op.create_index(op.f("ix_attempts_session_id"), "attempts", ["session_id"], unique=False)
    op.create_index(op.f("ix_attempts_subject_id"), "attempts", ["subject_id"], unique=False)
    op.create_index(op.f("ix_attempts_user_id"), "attempts", ["user_id"], unique=False)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("subject_pack_id", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=50), nullable=False),
        sa.Column("uploaded_by", sa.String(length=50), nullable=False),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["subject_pack_id"], ["subject_packs.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_document_type"), "documents", ["document_type"], unique=False)
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)
    op.create_index(op.f("ix_documents_subject_id"), "documents", ["subject_id"], unique=False)
    op.create_index(op.f("ix_documents_subject_pack_id"), "documents", ["subject_pack_id"], unique=False)
    op.create_index(op.f("ix_documents_uploaded_by"), "documents", ["uploaded_by"], unique=False)

    op.create_table(
        "content_chunks",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("document_id", sa.String(length=80), nullable=False),
        sa.Column("subject_id", sa.String(length=50), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_chunks_document_id"), "content_chunks", ["document_id"], unique=False)
    op.create_index(op.f("ix_content_chunks_subject_id"), "content_chunks", ["subject_id"], unique=False)

    op.create_table(
        "rubrics",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("question_id", sa.String(length=80), nullable=False),
        sa.Column("concepts_blob", sa.Text(), nullable=False),
        sa.Column("mark_split_blob", sa.Text(), nullable=False),
        sa.Column("diagram_expected", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rubrics_question_id"), "rubrics", ["question_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_rubrics_question_id"), table_name="rubrics")
    op.drop_table("rubrics")

    op.drop_index(op.f("ix_content_chunks_subject_id"), table_name="content_chunks")
    op.drop_index(op.f("ix_content_chunks_document_id"), table_name="content_chunks")
    op.drop_table("content_chunks")

    op.drop_index(op.f("ix_documents_uploaded_by"), table_name="documents")
    op.drop_index(op.f("ix_documents_subject_pack_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_subject_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_document_type"), table_name="documents")
    op.drop_table("documents")

    op.drop_index(op.f("ix_attempts_user_id"), table_name="attempts")
    op.drop_index(op.f("ix_attempts_subject_id"), table_name="attempts")
    op.drop_index(op.f("ix_attempts_session_id"), table_name="attempts")
    op.drop_index(op.f("ix_attempts_question_id"), table_name="attempts")
    op.drop_table("attempts")

    op.drop_index(op.f("ix_practice_sessions_user_id"), table_name="practice_sessions")
    op.drop_index(op.f("ix_practice_sessions_subject_id"), table_name="practice_sessions")
    op.drop_index(op.f("ix_practice_sessions_status"), table_name="practice_sessions")
    op.drop_index(op.f("ix_practice_sessions_question_id"), table_name="practice_sessions")
    op.drop_table("practice_sessions")

    op.drop_index(op.f("ix_subject_packs_subject_id"), table_name="subject_packs")
    op.drop_index(op.f("ix_subject_packs_status"), table_name="subject_packs")
    op.drop_table("subject_packs")

    op.drop_index(op.f("ix_questions_subject_id"), table_name="questions")
    op.drop_index(op.f("ix_questions_module_no"), table_name="questions")
    op.drop_index(op.f("ix_questions_marks"), table_name="questions")
    op.drop_table("questions")

    op.drop_index(op.f("ix_subjects_status"), table_name="subjects")
    op.drop_index(op.f("ix_subjects_semester"), table_name="subjects")
    op.drop_index(op.f("ix_subjects_course_code"), table_name="subjects")
    op.drop_table("subjects")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
