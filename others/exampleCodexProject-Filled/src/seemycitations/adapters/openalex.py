from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from seemycitations.adapters.base import ScholarlyAdapter, ScholarlyProviderError
from seemycitations.models import AuthorCandidate, NormalizedWork, PdfAvailability


class OpenAlexAdapter(ScholarlyAdapter):
    provider_name = "OpenAlex"
    base_url = "https://api.openalex.org"

    def __init__(self, *, email: str | None = None, client: httpx.AsyncClient | None = None):
        self.email = email
        self._client = client

    def _params(self, values: dict[str, Any]) -> dict[str, Any]:
        if self.email:
            values["mailto"] = self.email
        return values

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=15, follow_redirects=True)
        try:
            response = await client.get(f"{self.base_url}{path}", params=self._params(params))
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise ScholarlyProviderError(
                    "OpenAlex rate limit reached. Please wait and retry.", code="rate_limit"
                ) from exc
            raise ScholarlyProviderError(
                f"OpenAlex returned HTTP {exc.response.status_code}.", code="provider_http"
            ) from exc
        except (httpx.RequestError, ValueError) as exc:
            raise ScholarlyProviderError(
                "OpenAlex could not be reached. Check the network and retry.", code="network"
            ) from exc
        finally:
            if owns_client:
                await client.aclose()

    async def search_authors(self, query: str) -> list[AuthorCandidate]:
        payload = await self._get("/authors", {"search": query, "per-page": 10})
        return [self.normalize_author(item) for item in payload.get("results", [])]

    async def get_works(self, author_id: str) -> list[NormalizedWork]:
        short_id = author_id.rsplit("/", 1)[-1]
        payload = await self._get(
            "/works",
            {"filter": f"authorships.author.id:{short_id}", "per-page": 100, "sort": "publication_date:desc"},
        )
        retrieved_at = datetime.now(UTC)
        return [self.normalize_work(item, retrieved_at=retrieved_at) for item in payload.get("results", [])]

    @classmethod
    def normalize_author(cls, item: dict[str, Any]) -> AuthorCandidate:
        institutions = item.get("last_known_institutions") or []
        topics = item.get("topics") or item.get("x_concepts") or []
        return AuthorCandidate(
            id=item["id"].rsplit("/", 1)[-1],
            name=item.get("display_name") or "Unknown author",
            affiliation=institutions[0].get("display_name") if institutions else None,
            works_count=item.get("works_count") or 0,
            cited_by_count=item.get("cited_by_count") or 0,
            topics=[topic.get("display_name", "") for topic in topics[:3] if topic.get("display_name")],
            orcid=item.get("orcid"),
            provider=cls.provider_name,
        )

    @classmethod
    def normalize_work(cls, item: dict[str, Any], *, retrieved_at: datetime) -> NormalizedWork:
        primary = item.get("primary_location") or {}
        best_oa = item.get("best_oa_location") or {}
        oa_url = best_oa.get("pdf_url")
        source = primary.get("source") or {}
        doi = item.get("doi")
        source_url = primary.get("landing_page_url") or doi or item.get("id")
        return NormalizedWork(
            id=item["id"].rsplit("/", 1)[-1],
            title=item.get("display_name") or item.get("title") or "Untitled work",
            authors=[
                authorship.get("author", {}).get("display_name", "Unknown author")
                for authorship in item.get("authorships", [])
            ],
            year=item.get("publication_year"),
            venue=source.get("display_name"),
            doi=doi.removeprefix("https://doi.org/") if doi else None,
            source_url=source_url,
            citation_count=item.get("cited_by_count") or 0,
            citation_source=cls.provider_name,
            retrieved_at=retrieved_at,
            pdf=PdfAvailability(
                url=oa_url,
                is_open_access=bool(oa_url and (item.get("open_access") or {}).get("is_oa")),
                origin=best_oa.get("landing_page_url") if oa_url else None,
            ),
        )
