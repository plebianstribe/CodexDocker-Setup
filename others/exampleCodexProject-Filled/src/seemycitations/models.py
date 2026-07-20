from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AuthorCandidate(BaseModel):
    id: str
    name: str
    affiliation: str | None = None
    works_count: int = 0
    cited_by_count: int = 0
    topics: list[str] = Field(default_factory=list)
    orcid: str | None = None
    provider: str


class PdfAvailability(BaseModel):
    url: HttpUrl | None = None
    is_open_access: bool = False
    origin: str | None = None


class NormalizedWork(BaseModel):
    id: str
    title: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    source_url: HttpUrl | None = None
    citation_count: int = 0
    citation_source: str
    retrieved_at: datetime
    pdf: PdfAvailability = Field(default_factory=PdfAvailability)


DocumentStatus = Literal[
    "not_started", "fetching", "uploading", "queued", "extracting", "ready", "failed"
]


class DocumentRecord(BaseModel):
    id: str
    work_id: str
    display_name: str
    origin: Literal["upload", "open_access"]
    source_url: str | None = None
    local_path: str
    status: DocumentStatus
    error: str | None = None
    page_count: int | None = None
    created_at: datetime


class PageMatch(BaseModel):
    page: int
    snippet: str
    start: int


class KeywordResult(BaseModel):
    keyword: str
    count: int
    pages: list[PageMatch]
