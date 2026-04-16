from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.dependencies import require_admin
from app.models import User
from app.schemas import (
    AdminActionResponse,
    ExtractQuestionsRequest,
    GenerateRubricsRequest,
    SubjectPackCreateRequest,
    SubjectPackResponse,
)
from app.services import repository
from app.services.ingestion import (
    chunk_text,
    derive_concepts,
    extract_questions_from_text,
    extract_text_from_file,
    persist_uploaded_file,
)
from app.services.retrieval import generate_rubric, retrieve_evidence

router = APIRouter()


@router.post("/subject-packs", response_model=SubjectPackResponse, status_code=status.HTTP_201_CREATED)
def create_subject_pack(
    payload: SubjectPackCreateRequest,
    session: Session = Depends(get_db_session),
    _admin: User = Depends(require_admin),
) -> SubjectPackResponse:
    subject = repository.get_subject(session, payload.subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    pack = repository.create_subject_pack(session, payload.subject_id, payload.title)
    return SubjectPackResponse(
        id=pack.id,
        subjectId=pack.subject_id,
        title=pack.title,
        status=pack.status,
        createdAt=pack.created_at,
    )


@router.post("/documents/upload", response_model=AdminActionResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    subject_pack_id: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
    admin: User = Depends(require_admin),
) -> AdminActionResponse:
    if document_type not in {"syllabus", "notes", "question_bank", "timetable"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document type")

    pack = repository.get_subject_pack(session, subject_pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject pack not found")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    file_path = persist_uploaded_file(file.filename or "upload.bin", file_bytes)
    extracted_text = extract_text_from_file(file_path)
    document_id = repository.create_document(
        session=session,
        subject_pack_id=subject_pack_id,
        subject_id=pack.subject_id,
        uploaded_by=admin.id,
        document_type=document_type,
        filename=file.filename or "upload.bin",
        file_path=file_path,
        extracted_text=extracted_text,
    )
    chunks = chunk_text(extracted_text)
    chunk_count = repository.replace_chunks_for_document(session, document_id, pack.subject_id, chunks)
    return AdminActionResponse(
        message="Document uploaded and processed.",
        resourceId=document_id,
        metadata={"chunks": chunk_count, "textLength": len(extracted_text)},
    )


@router.post("/questions/extract", response_model=AdminActionResponse, status_code=status.HTTP_202_ACCEPTED)
def extract_questions(
    payload: ExtractQuestionsRequest,
    session: Session = Depends(get_db_session),
    _admin: User = Depends(require_admin),
) -> AdminActionResponse:
    pack = repository.get_subject_pack(session, payload.subject_pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject pack not found")
    documents = repository.get_documents_by_pack(session, payload.subject_pack_id, document_type="question_bank")
    if not documents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No question bank document uploaded")

    combined_text = "\n".join(doc.extracted_text for doc in documents if doc.extracted_text.strip())
    extracted = extract_questions_from_text(combined_text)
    if not extracted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No parseable questions found")

    normalized_questions: list[dict[str, object]] = []
    for idx, question in enumerate(extracted, start=1):
        concepts = question.get("concepts") or derive_concepts(str(question["text"]))
        normalized_questions.append(
            {
                "text": question["text"],
                "marks": question.get("marks", 10),
                "module_no": ((idx - 1) % 5) + 1,
                "year": 2026,
                "diagram_expected": question.get("diagram_expected", False),
                "concepts": concepts,
                "reference_answer": "Generated from uploaded question bank and will improve after rubric generation.",
            }
        )
    count = repository.replace_question_bank(session, pack.subject_id, normalized_questions)
    return AdminActionResponse(message="Question extraction completed.", metadata={"questionsCreated": count})


@router.post("/rubrics/generate", response_model=AdminActionResponse, status_code=status.HTTP_202_ACCEPTED)
def generate_rubrics(
    payload: GenerateRubricsRequest,
    session: Session = Depends(get_db_session),
    _admin: User = Depends(require_admin),
) -> AdminActionResponse:
    pack = repository.get_subject_pack(session, payload.subject_pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject pack not found")
    questions = repository.list_questions(session, pack.subject_id)
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No questions found for subject")

    chunks = repository.get_subject_chunks(session, pack.subject_id)
    chunk_tuples = [(chunk.id, chunk.chunk_text) for chunk in chunks]
    for question in questions:
        concepts, mark_split, diagram_expected = generate_rubric(question.text, question.marks)
        repository.save_rubric(
            session=session,
            question_id=question.id,
            concepts=concepts,
            mark_split=mark_split,
            diagram_expected=diagram_expected,
            source="heuristic-v1",
        )
        retrieved = retrieve_evidence(question.text, "", chunk_tuples, top_k=3)
        if retrieved:
            repository.set_question_evidence(session, question.id, retrieved)
    return AdminActionResponse(message="Rubric generation completed.", metadata={"questionsProcessed": len(questions)})


@router.post("/subject-packs/{pack_id}/publish", response_model=AdminActionResponse)
def publish_subject_pack(
    pack_id: str,
    session: Session = Depends(get_db_session),
    _admin: User = Depends(require_admin),
) -> AdminActionResponse:
    pack = repository.publish_subject_pack(session, pack_id)
    if pack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject pack not found")
    return AdminActionResponse(message="Subject pack published.", resourceId=pack.id)
