from fastapi.testclient import TestClient

from seemycitations.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_adapter_is_replaceable_contract() -> None:
    from seemycitations.adapters.base import ScholarlyAdapter

    assert ScholarlyAdapter.__abstractmethods__ == {"search_authors", "get_works"}
