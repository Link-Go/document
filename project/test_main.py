from pydantic import ValidationError
from fastapi.testclient import TestClient

from main import app
from schemas import EvaluationPageInfo

client = TestClient(app)


def test_get_evaluation_record():
    response = client.get("/compliance/evaluation")
    try:
        EvaluationPageInfo(**response.json())
    except ValidationError:
        raise ValidationError

    response = client.get("/compliance/evaluation/?page=2&limit=50")
    assert response.status_code == 200
    assert response.json() is None

    response = client.get(
        "/compliance/evaluation/?page=1&limit=50&keyword=HRM")
    assert response.status_code == 200
    assert len(response.json()["evaluation_record"]) == 3

    response = client.get(
        "/compliance/evaluation/?page=1&limit=50&keyword=  ")
    assert response.status_code == 200
    assert len(response.json()["evaluation_record"]) == 3

    response = client.get(
        "/compliance/evaluation/?page=1&limit=1&keyword=  ")
    assert response.status_code == 200
    assert len(response.json()["evaluation_record"]) == 1

    response = client.get(
        "/compliance/evaluation/?page=1&limit=50&keyword=HRM2")
    assert response.status_code == 200
    assert len(response.json()["evaluation_record"]) == 2

    response = client.get(
        "/compliance/evaluation/?page=1&limit=50&keyword=HRM123")
    assert response.status_code == 200
    assert response.json() is None
