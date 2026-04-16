from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from app.core.config import settings


def persist_uploaded_file(filename: str, content: bytes) -> str:
    upload_dir = Path(settings.upload_root).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", filename)
    target = upload_dir / safe_name
    suffix = 1
    while target.exists():
        target = upload_dir / f"{target.stem}_{suffix}{target.suffix}"
        suffix += 1
    target.write_bytes(content)
    return str(target)


def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _extract_pdf_text(path)
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def chunk_text(text: str, max_words: int = 120) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        current.append(word)
        if len(current) >= max_words:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def extract_questions_from_text(text: str) -> list[dict[str, object]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    questions: list[dict[str, object]] = []
    numbered = re.compile(r"^(\d+)[\).:-]\s*(.+)$")
    marks_pattern = re.compile(r"\[(\d+)\s*marks?\]|\((\d+)\s*marks?\)", re.IGNORECASE)
    for line in lines:
        match = numbered.match(line)
        if not match:
            continue
        question_text = match.group(2)
        marks = 10
        marks_match = marks_pattern.search(question_text)
        if marks_match:
            marks = int(marks_match.group(1) or marks_match.group(2))
            question_text = marks_pattern.sub("", question_text).strip(" -:")
        questions.append(
            {
                "text": question_text,
                "marks": marks,
                "module_no": 1,
                "year": 2026,
                "diagram_expected": "diagram" in question_text.lower(),
                "concepts": derive_concepts(question_text),
                "reference_answer": "Auto-generated; refine via rubric workflow.",
            }
        )
    return questions


def derive_concepts(text: str) -> list[str]:
    stop_words = {
        "the",
        "and",
        "or",
        "with",
        "for",
        "from",
        "into",
        "this",
        "that",
        "what",
        "when",
        "where",
        "which",
        "about",
        "explain",
        "define",
        "write",
        "short",
        "note",
    }
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]{2,}", text.lower())
    ordered: list[str] = []
    for token in tokens:
        if token in stop_words:
            continue
        if token not in ordered:
            ordered.append(token)
    return ordered[:6] if ordered else ["concept", "definition", "application"]


def _extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            parts.append(page_text)
    return "\n".join(parts)
