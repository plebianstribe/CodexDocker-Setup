from __future__ import annotations

from abc import ABC, abstractmethod

from seemycitations.models import AuthorCandidate, NormalizedWork


class ScholarlyProviderError(RuntimeError):
    def __init__(self, message: str, *, code: str = "provider_error", retryable: bool = True):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ScholarlyAdapter(ABC):
    @abstractmethod
    async def search_authors(self, query: str) -> list[AuthorCandidate]: ...

    @abstractmethod
    async def get_works(self, author_id: str) -> list[NormalizedWork]: ...
