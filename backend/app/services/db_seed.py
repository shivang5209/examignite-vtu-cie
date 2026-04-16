from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import QuestionRecord, SubjectPackRecord, SubjectRecord, UserRecord
from app.services.security import hash_password


def seed_demo_data(session: Session) -> None:
    existing_user = session.scalar(select(UserRecord.id).limit(1))
    if existing_user is not None:
        return

    users = [
        UserRecord(
            id="user-student-1",
            name="Shivang VTU",
            email="student@cie.app",
            role="student",
            password_hash=hash_password("student123"),
        ),
        UserRecord(
            id="user-admin-1",
            name="VTU Admin",
            email="admin@cie.app",
            role="admin",
            password_hash=hash_password("admin123"),
        ),
    ]
    subjects = [
        SubjectRecord(
            id="sub-ada",
            course_code="BCS401",
            title="Analysis and Design of Algorithms",
            semester=4,
            scheme="2022",
            credits=4,
            marks_display=15,
            status="published",
        ),
        SubjectRecord(
            id="sub-dbms",
            course_code="BCS403",
            title="Database Management Systems",
            semester=4,
            scheme="2022",
            credits=4,
            marks_display=15,
            status="published",
        ),
    ]
    questions = [
        QuestionRecord(
            id="q-ada-dijkstra",
            subject_id="sub-ada",
            text="Explain Dijkstra's algorithm with its steps, working principle, and time complexity.",
            marks=10,
            module_no=3,
            year=2025,
            cie_type="theory",
            diagram_expected=1,
            concepts_blob=json.dumps(
                ["greedy choice", "priority queue", "relaxation", "shortest path", "time complexity"]
            ),
            reference_answer=(
                "Dijkstra's algorithm is a greedy single-source shortest path algorithm for non-negative edge "
                "weights. It initializes source distance to 0, others to infinity, repeatedly selects the minimum "
                "tentative vertex, relaxes adjacent edges, and continues until all vertices are finalized. With a "
                "binary heap, the time complexity is O((V + E) log V)."
            ),
            evidence_blob=json.dumps(
                [
                    {
                        "source_title": "ADA Notes - Module 3",
                        "snippet": "Dijkstra repeatedly picks the minimum distance vertex and relaxes its outgoing edges.",
                    },
                    {
                        "source_title": "Question Bank 2025",
                        "snippet": "For 10 marks, include greedy idea, data structure used, algorithm steps, and complexity.",
                    },
                ]
            ),
        ),
        QuestionRecord(
            id="q-dbms-normalization",
            subject_id="sub-dbms",
            text="Define normalization and explain 1NF, 2NF, and 3NF with suitable examples.",
            marks=10,
            module_no=2,
            year=2025,
            cie_type="theory",
            diagram_expected=0,
            concepts_blob=json.dumps(["normalization", "1nf", "2nf", "3nf", "functional dependency"]),
            reference_answer=(
                "Normalization organizes data to reduce redundancy and anomalies. 1NF removes repeating groups and "
                "stores atomic values, 2NF removes partial dependency on a composite key, and 3NF removes transitive "
                "dependency. Good answers define each normal form and show a decomposed table example."
            ),
            evidence_blob=json.dumps(
                [
                    {
                        "source_title": "DBMS Notes - Module 2",
                        "snippet": "Normalization aims to remove insertion, deletion, and update anomalies.",
                    },
                    {
                        "source_title": "CIE Repeated Questions",
                        "snippet": "3NF answers should mention transitive dependency explicitly.",
                    },
                ]
            ),
        ),
    ]
    packs = [
        SubjectPackRecord(id="pack-ada-2022", subject_id="sub-ada", title="ADA 2022 Scheme Core Pack", status="published"),
        SubjectPackRecord(
            id="pack-dbms-2022",
            subject_id="sub-dbms",
            title="DBMS 2022 Scheme Core Pack",
            status="published",
        ),
    ]

    session.add_all(users + subjects + questions + packs)
    session.commit()
