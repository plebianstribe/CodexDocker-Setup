from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.requests import Request

from seemycitations.adapters.base import ScholarlyProviderError
from seemycitations.adapters.cached import CachedScholarlyAdapter
from seemycitations.adapters.openalex import OpenAlexAdapter
from seemycitations.config import settings
from seemycitations.services.cache import JsonCache
from seemycitations.services.documents import DocumentError, DocumentService
from seemycitations.services.keywords import analyze_keywords, extract_keywords, parse_keywords
from seemycitations.services.author_library import AuthorLibrary
from pydantic import BaseModel

app = FastAPI(title="SeeMyCitations", version="0.1.0")
package_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=package_dir / "static"), name="static")
templates = Jinja2Templates(directory=package_dir / "templates")
app.state.provider = CachedScholarlyAdapter(
    OpenAlexAdapter(email=settings.openalex_email), JsonCache(settings.cache_dir / "metadata")
)
app.state.works = {}
app.state.authors = {}
app.state.work_authors = {}
app.state.library = AuthorLibrary(settings.author_dir)
app.state.documents = DocumentService(
    settings.upload_dir,
    JsonCache(settings.cache_dir / "documents", ttl_seconds=365 * 86400),
    max_bytes=settings.max_upload_mb * 1024 * 1024,
)


@app.exception_handler(ScholarlyProviderError)
async def provider_error_handler(_request, exc: ScholarlyProviderError) -> JSONResponse:
    status = 429 if exc.code == "rate_limit" else 502
    return JSONResponse(
        status_code=status,
        content={"error": {"code": exc.code, "message": str(exc), "retryable": exc.retryable}},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/authors")
async def search_authors(q: str = Query(min_length=2, max_length=200)):
    authors = await app.state.provider.search_authors(q)
    app.state.authors.update({author.id: author for author in authors})
    return {"query": q, "authors": authors}


@app.get("/api/authors/{author_id}/works")
async def author_works(author_id: str):
    works = await app.state.provider.get_works(author_id)
    works = [work.model_copy(update={"id": work.id.rsplit("/", 1)[-1]}) for work in works]
    app.state.works.update({work.id: work for work in works})
    app.state.work_authors.update({work.id: author_id for work in works})
    author = app.state.authors.get(author_id)
    library = app.state.library.reconcile(author, works) if author else None
    states = {key: value.get("library_state", "new") for key, value in (library or {}).get("papers", {}).items()}
    return {"author_id": author_id, "works": works, "library_states": states}


async def _download_oa(work):
    import httpx
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(str(work.pdf.url))
        response.raise_for_status()
        return response.content


@app.post("/api/authors/{author_id}/sync-library")
async def sync_author_library(author_id: str):
    author = app.state.authors.get(author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Search for and select this author before syncing.")
    works = await app.state.provider.get_works(author_id)
    works = [work.model_copy(update={"id": work.id.rsplit("/", 1)[-1]}) for work in works]
    app.state.works.update({work.id: work for work in works})
    return await app.state.library.sync_downloads(author, works, _download_oa)


@app.exception_handler(DocumentError)
async def document_error_handler(_request, exc: DocumentError) -> JSONResponse:
    status = 422 if exc.code in {"invalid_pdf", "unreadable_pdf"} else 502
    return JSONResponse(status_code=status, content={"error": {"code": exc.code, "message": str(exc)}})


@app.get("/api/works/{work_id}/documents")
async def list_documents(work_id: str):
    return {"documents": app.state.documents.list(work_id)}


@app.post("/api/documents/upload")
async def upload_document(work_id: str = Form(), file: UploadFile = File()):
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    record = app.state.documents.add_pdf(
        work_id=work_id,
        name=file.filename or "uploaded.pdf",
        content=content,
        origin="upload",
    )
    return {"document": record}


@app.post("/api/works/{work_id}/fetch-open-access")
async def fetch_open_access(work_id: str):
    work = app.state.works.get(work_id)
    if work is None:
        raise HTTPException(status_code=404, detail="Load this work from its author before fetching a PDF.")
    return {"document": await app.state.documents.fetch_open_access(work)}


class AnalysisRequest(BaseModel):
    keywords: str


def _ready_pages(document_id: str):
    document = app.state.documents.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    if document.status != "ready":
        raise HTTPException(status_code=409, detail="Document extraction is not ready.")
    pages = app.state.documents.text_cache.get("extracted_text", document_id)
    if pages is None:
        raise HTTPException(status_code=409, detail="Extracted text is unavailable; retry extraction.")
    return document, pages


@app.get("/api/documents/{document_id}/suggested-keywords")
async def suggested_keywords(document_id: str, limit: int = Query(default=12, ge=1, le=30)):
    _document, pages = _ready_pages(document_id)
    return {"keywords": extract_keywords(pages, limit=limit), "method": "local frequency and repeated phrases"}


@app.get("/api/documents/{document_id}/pages")
async def document_pages(document_id: str):
    document, pages = _ready_pages(document_id)
    return {"document_id": document.id, "page_count": len(pages), "pages": pages}


@app.post("/api/documents/{document_id}/analysis")
async def analyze_document(document_id: str, request: AnalysisRequest):
    if not parse_keywords(request.keywords):
        raise HTTPException(status_code=422, detail="Enter at least one keyword.")
    _document, pages = _ready_pages(document_id)
    return {"matching_mode": "case-insensitive whole words", "results": analyze_keywords(pages, request.keywords)}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"max_upload_mb": settings.max_upload_mb},
    )
