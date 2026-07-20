from pathlib import Path

import fitz
import pytest

from seemycitations.models import NormalizedWork
from seemycitations.services.cache import JsonCache
from seemycitations.services.documents import DocumentError, DocumentService


def make_pdf(text: str = "Evidence appears here.") -> bytes:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    payload = document.tobytes()
    document.close()
    return payload


def service(tmp_path: Path) -> DocumentService:
    return DocumentService(tmp_path / "uploads", JsonCache(tmp_path / "cache"), max_bytes=1_000_000)


def test_upload_extracts_and_persists_page_text(tmp_path: Path) -> None:
    documents = service(tmp_path)
    result = documents.add_pdf(work_id="W1", name="paper.pdf", content=make_pdf(), origin="upload")
    assert result.status == "ready"
    assert result.page_count == 1
    assert documents.get(result.id) == result
    assert documents.text_cache.get("extracted_text", result.id)[0]["text"].startswith("Evidence")


def test_invalid_and_scanned_pdfs_are_actionable(tmp_path: Path) -> None:
    documents = service(tmp_path)
    with pytest.raises(DocumentError, match="not a valid PDF"):
        documents.add_pdf(work_id="W1", name="bad.pdf", content=b"nope", origin="upload")
    with pytest.raises(DocumentError, match="scanned PDF"):
        documents.add_pdf(work_id="W1", name="scan.pdf", content=make_pdf(""), origin="upload")
    assert documents.list("W1")[-1].status == "failed"


@pytest.mark.asyncio
async def test_remote_fetch_requires_open_access_metadata(tmp_path: Path) -> None:
    documents = service(tmp_path)
    work = NormalizedWork(
        id="W1",
        title="Closed",
        authors=[],
        citation_source="fixture",
        retrieved_at="2026-01-01T00:00:00Z",
    )
    with pytest.raises(DocumentError, match="No verified open-access"):
        await documents.fetch_open_access(work)


def test_multiple_documents_can_be_selected_by_id(tmp_path: Path) -> None:
    documents = service(tmp_path)
    first = documents.add_pdf(work_id="W1", name="one.pdf", content=make_pdf("One"), origin="upload")
    second = documents.add_pdf(work_id="W1", name="two.pdf", content=make_pdf("Two"), origin="upload")
    assert [item.id for item in documents.list("W1")] == [first.id, second.id]
    assert documents.get(first.id).display_name == "one.pdf"
