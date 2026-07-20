from datetime import UTC, datetime

import httpx
import pytest

from seemycitations.adapters.openalex import OpenAlexAdapter


AUTHOR = {
    "id": "https://openalex.org/A123",
    "display_name": "Ada Example",
    "works_count": 12,
    "cited_by_count": 99,
    "last_known_institutions": [{"display_name": "Example University"}],
    "topics": [{"display_name": "Machine Learning"}],
    "orcid": "https://orcid.org/0000-0000-0000-0001",
}

WORK = {
    "id": "https://openalex.org/W123",
    "display_name": "Evidence by Page",
    "publication_year": 2025,
    "authorships": [{"author": {"display_name": "Ada Example"}}],
    "primary_location": {
        "landing_page_url": "https://example.org/work",
        "source": {"display_name": "Journal of Examples"},
    },
    "best_oa_location": {
        "pdf_url": "https://example.org/work.pdf",
        "landing_page_url": "https://example.org/work",
    },
    "open_access": {"is_oa": True},
    "doi": "https://doi.org/10.1234/example",
    "cited_by_count": 42,
}


def test_normalize_author_exposes_disambiguation_fields() -> None:
    result = OpenAlexAdapter.normalize_author(AUTHOR)
    assert result.affiliation == "Example University"
    assert result.topics == ["Machine Learning"]
    assert result.provider == "OpenAlex"


def test_normalize_work_preserves_provenance_and_oa() -> None:
    now = datetime.now(UTC)
    result = OpenAlexAdapter.normalize_work(WORK, retrieved_at=now)
    assert result.id == "W123"
    assert result.doi == "10.1234/example"
    assert result.citation_count == 42
    assert result.citation_source == "OpenAlex"
    assert result.retrieved_at == now
    assert result.pdf.is_open_access is True


@pytest.mark.asyncio
async def test_search_authors_keeps_ambiguous_candidates_separate() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": [AUTHOR, {**AUTHOR, "id": "A456", "display_name": "Ada Example Jr"}]})

    adapter = OpenAlexAdapter(client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    results = await adapter.search_authors("Ada Example")
    await adapter._client.aclose()
    assert [item.id for item in results] == ["A123", "A456"]
