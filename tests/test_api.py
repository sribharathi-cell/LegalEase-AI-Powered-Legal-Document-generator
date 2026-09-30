from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "LegalEase API"


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_generate_validation():

    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "Person A and Person B",
            "terms": "Payment within 30 days",
            "effective_date": "October 1, 2026"
        }
    )

    assert response.status_code == 422