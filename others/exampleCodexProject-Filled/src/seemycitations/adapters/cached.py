from __future__ import annotations

from seemycitations.adapters.base import ScholarlyAdapter
from seemycitations.models import AuthorCandidate, NormalizedWork
from seemycitations.services.cache import JsonCache


class CachedScholarlyAdapter(ScholarlyAdapter):
    def __init__(self, provider: ScholarlyAdapter, cache: JsonCache):
        self.provider = provider
        self.cache = cache

    async def search_authors(self, query: str) -> list[AuthorCandidate]:
        key = query.strip().casefold()
        cached = self.cache.get("authors", key)
        if cached is not None:
            return [AuthorCandidate.model_validate(item) for item in cached]
        results = await self.provider.search_authors(query)
        self.cache.set("authors", key, [item.model_dump(mode="json") for item in results])
        return results

    async def get_works(self, author_id: str) -> list[NormalizedWork]:
        cached = self.cache.get("works", author_id)
        if cached is not None:
            return [NormalizedWork.model_validate(item) for item in cached]
        results = await self.provider.get_works(author_id)
        self.cache.set("works", author_id, [item.model_dump(mode="json") for item in results])
        return results
