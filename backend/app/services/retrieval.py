from __future__ import annotations

import re

from app.models import EvidenceSnippet


def retrieve_evidence(question_text: str, answer_text: str, chunks: list[tuple[str, str]], top_k: int = 3) -> list[EvidenceSnippet]:
    query_tokens = set(_tokenize(question_text) + _tokenize(answer_text))
    scored: list[tuple[int, str, str]] = []
    for chunk_id, chunk_text in chunks:
        chunk_tokens = set(_tokenize(chunk_text))
        score = len(query_tokens & chunk_tokens)
        if score > 0:
            scored.append((score, chunk_id, chunk_text))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:top_k]
    return [
        EvidenceSnippet(
            source_title=f"Chunk {item[1]}",
            snippet=item[2][:280].strip(),
        )
        for item in top
    ]


def generate_rubric(question_text: str, marks: int) -> tuple[list[str], dict[str, float], bool]:
    concepts = _extract_concepts(question_text)
    if not concepts:
        concepts = ["definition", "core steps", "example"]
    per_concept = round(marks / len(concepts), 2)
    split = {concept: per_concept for concept in concepts}
    diagram_expected = any(token in question_text.lower() for token in ["diagram", "draw", "architecture", "flowchart"])
    return concepts, split, diagram_expected


def _extract_concepts(text: str) -> list[str]:
    tokens = _tokenize(text)
    concepts: list[str] = []
    for token in tokens:
        if token not in concepts:
            concepts.append(token)
    return concepts[:6]


def _tokenize(text: str) -> list[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "what",
        "which",
        "explain",
        "define",
        "write",
        "about",
        "marks",
    }
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_]{2,}", text.lower())
    return [token for token in tokens if token not in stop]
