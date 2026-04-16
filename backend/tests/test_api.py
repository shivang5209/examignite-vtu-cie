from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _student_headers() -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": "student@cie.app", "password": "student123"},
    )
    assert response.status_code == 200
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


def _admin_headers() -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": "admin@cie.app", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_and_me() -> None:
    headers = _student_headers()
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "student@cie.app"


def test_subject_listing_and_filtering() -> None:
    headers = _student_headers()
    response = client.get("/subjects", params={"semester": 4}, headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 2
    assert all(subject["semester"] == 4 for subject in payload)


def test_practice_submission_flow() -> None:
    headers = _student_headers()
    session_response = client.post(
        "/practice-sessions",
        json={"subjectId": "sub-ada", "questionId": "q-ada-dijkstra"},
        headers=headers,
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["id"]

    submit_response = client.post(
        f"/practice-sessions/{session_id}/submit",
        json={
            "answerText": (
                "Dijkstra is a greedy shortest path algorithm. It uses relaxation and a priority queue to "
                "compute shortest path values and the time complexity is O((V + E) log V)."
            )
        },
        headers=headers,
    )
    assert submit_response.status_code == 200
    feedback = submit_response.json()
    assert feedback["questionId"] == "q-ada-dijkstra"
    assert feedback["scoreNormalized"] > 0
    assert "greedy choice" in feedback["conceptCoverage"]

    attempt_response = client.get(f"/attempts/{feedback['attemptId']}", headers=headers)
    assert attempt_response.status_code == 200
    assert attempt_response.json()["attemptId"] == feedback["attemptId"]


def test_attempt_history_endpoint() -> None:
    headers = _student_headers()
    response = client.get("/attempts/history", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_progress_snapshot_updates_after_submission() -> None:
    headers = _student_headers()
    session_response = client.post(
        "/practice-sessions",
        json={"subjectId": "sub-dbms", "questionId": "q-dbms-normalization"},
        headers=headers,
    )
    session_id = session_response.json()["id"]

    client.post(
        f"/practice-sessions/{session_id}/submit",
        json={
            "answerText": (
                "Normalization reduces anomalies. 1NF ensures atomic values, 2NF removes partial dependency, "
                "and 3NF removes transitive dependency using functional dependency rules."
            )
        },
        headers=headers,
    )

    progress_response = client.get("/subjects/sub-dbms/progress", headers=headers)
    assert progress_response.status_code == 200
    payload = progress_response.json()
    assert payload["subjectId"] == "sub-dbms"
    assert payload["attemptsCount"] >= 1


def test_admin_upload_extract_rubric_pipeline() -> None:
    admin_headers = _admin_headers()

    pack_response = client.post(
        "/admin/subject-packs",
        json={"subjectId": "sub-dbms", "title": "DBMS Test Pack"},
        headers=admin_headers,
    )
    assert pack_response.status_code == 201
    pack_id = pack_response.json()["id"]

    file_content = b"1) Define ACID properties [10 marks]\n2) Explain transaction states [10 marks]\n"
    upload_response = client.post(
        "/admin/documents/upload",
        data={"subject_pack_id": pack_id, "document_type": "question_bank"},
        files={"file": ("question_bank.txt", BytesIO(file_content), "text/plain")},
        headers=admin_headers,
    )
    assert upload_response.status_code == 202

    extract_response = client.post(
        "/admin/questions/extract",
        json={"subjectPackId": pack_id},
        headers=admin_headers,
    )
    assert extract_response.status_code == 202
    assert extract_response.json()["metadata"]["questionsCreated"] >= 1

    rubric_response = client.post(
        "/admin/rubrics/generate",
        json={"subjectPackId": pack_id},
        headers=admin_headers,
    )
    assert rubric_response.status_code == 202


def test_admin_routes_reject_student() -> None:
    student_headers = _student_headers()
    response = client.post(
        "/admin/subject-packs",
        json={"subjectId": "sub-dbms", "title": "Should fail"},
        headers=student_headers,
    )
    assert response.status_code == 403
