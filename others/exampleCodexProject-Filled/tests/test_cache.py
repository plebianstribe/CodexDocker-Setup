from pathlib import Path

import pytest

from seemycitations.adapters.cached import CachedScholarlyAdapter
from seemycitations.models import AuthorCandidate
from seemycitations.services.cache import JsonCache


class CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def search_authors(self, query: str):
        self.calls += 1
        return [AuthorCandidate(id="A1", name=query, provider="fixture")]

    async def get_works(self, author_id: str):
        self.calls += 1
        return []


@pytest.mark.asyncio
async def test_repeated_author_search_hits_cache(tmp_path: Path) -> None:
    provider = CountingProvider()
    adapter = CachedScholarlyAdapter(provider, JsonCache(tmp_path))
    first = await adapter.search_authors("Ada")
    second = await adapter.search_authors(" ada ")
    assert first == second
    assert provider.calls == 1


def test_expired_or_corrupt_cache_is_a_miss(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path, ttl_seconds=-1)
    cache.set("test", "key", {"ok": True})
    assert cache.get("test", "key") is None
    path = cache._path("test", "broken")
    path.write_text("not-json")
    assert cache.get("test", "broken") is None


def test_page_text_payload_uses_same_local_cache(tmp_path: Path) -> None:
    cache = JsonCache(tmp_path)
    cache.set("extracted_text", "document-1", [{"page": 1, "text": "evidence"}])
    assert cache.get("extracted_text", "document-1") == [{"page": 1, "text": "evidence"}]
