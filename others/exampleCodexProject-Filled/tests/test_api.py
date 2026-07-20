from fastapi.testclient import TestClient

from seemycitations.main import app
from seemycitations.adapters.base import ScholarlyProviderError
from seemycitations.models import AuthorCandidate
from seemycitations.errors import ERROR_ACTIONS, UserErrorCode


class StubProvider:
    async def search_authors(self, query: str):
        return [AuthorCandidate(id="A1", name=query, provider="fixture")]

    async def get_works(self, author_id: str):
        return []


def test_full_provider_work_ids_are_canonicalized_for_routes() -> None:
    from datetime import UTC, datetime
    from seemycitations.models import NormalizedWork
    class FullIdProvider(StubProvider):
        async def get_works(self, author_id: str):
            return [NormalizedWork(id="https://openalex.org/W123", title="Paper", authors=[], citation_source="fixture", retrieved_at=datetime.now(UTC))]
    original = app.state.provider
    app.state.provider = FullIdProvider()
    try:
        response = TestClient(app).get("/api/authors/A1/works")
    finally:
        app.state.provider = original
    assert response.status_code == 200
    assert response.json()["works"][0]["id"] == "W123"


def test_author_search_api() -> None:
    original = app.state.provider
    app.state.provider = StubProvider()
    try:
        response = TestClient(app).get("/api/authors", params={"q": "Ada"})
    finally:
        app.state.provider = original
    assert response.status_code == 200
    assert response.json()["authors"][0]["name"] == "Ada"


def test_author_search_validates_short_query() -> None:
    response = TestClient(app).get("/api/authors", params={"q": "A"})
    assert response.status_code == 422


def test_rate_limit_maps_to_actionable_error() -> None:
    class RateLimited(StubProvider):
        async def search_authors(self, query: str):
            raise ScholarlyProviderError("Wait and retry.", code="rate_limit")

    original = app.state.provider
    app.state.provider = RateLimited()
    try:
        response = TestClient(app).get("/api/authors", params={"q": "Ada"})
    finally:
        app.state.provider = original
    assert response.status_code == 429
    assert response.json()["error"] == {
        "code": "rate_limit",
        "message": "Wait and retry.",
        "retryable": True,
    }


def test_all_required_failure_states_have_recovery_copy() -> None:
    required = {
        UserErrorCode.RATE_LIMIT,
        UserErrorCode.NETWORK,
        UserErrorCode.NO_MATCHES,
        UserErrorCode.PDF_UNAVAILABLE,
        UserErrorCode.INVALID_PDF,
        UserErrorCode.UNREADABLE_PDF,
    }
    assert required <= ERROR_ACTIONS.keys()
    assert all(ERROR_ACTIONS[code] for code in required)


def test_keyword_suggestions_and_full_pages_api() -> None:
    from datetime import UTC, datetime
    from seemycitations.models import DocumentRecord
    class Cache:
        def get(self, namespace, key):
            return [{"page": 1, "text": "Neural networks improve memory. Neural networks retrieve memory."}]
    class Documents:
        text_cache = Cache()
        def get(self, document_id):
            return DocumentRecord(id=document_id, work_id="W1", display_name="paper.pdf", origin="upload", local_path="fixture", status="ready", page_count=1, created_at=datetime.now(UTC))
    original = app.state.documents
    app.state.documents = Documents()
    try:
        client = TestClient(app)
        suggested = client.get("/api/documents/D1/suggested-keywords")
        pages = client.get("/api/documents/D1/pages")
    finally:
        app.state.documents = original
    assert suggested.status_code == 200
    assert "neural networks" in suggested.json()["keywords"]
    assert pages.json()["pages"][0]["page"] == 1
    assert "<mark>" not in pages.text
