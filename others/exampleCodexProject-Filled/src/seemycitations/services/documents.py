from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import fitz
import httpx

from seemycitations.models import DocumentRecord, NormalizedWork
from seemycitations.services.cache import JsonCache


class DocumentError(ValueError):
    def __init__(self, message: str, *, code: str):
        super().__init__(message)
        self.code = code


class DocumentService:
    def __init__(
        self,
        root: Path,
        text_cache: JsonCache,
        *,
        max_bytes: int,
        client: httpx.AsyncClient | None = None,
    ):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.records_file = self.root / "documents.json"
        self.text_cache = text_cache
        self.max_bytes = max_bytes
        self.client = client

    def _records(self) -> list[DocumentRecord]:
        if not self.records_file.exists():
            return []
        try:
            return [DocumentRecord.model_validate(item) for item in json.loads(self.records_file.read_text())]
        except (OSError, ValueError, json.JSONDecodeError):
            return []

    def _save_records(self, records: list[DocumentRecord]) -> None:
        temporary = self.records_file.with_suffix(".tmp")
        temporary.write_text(
            json.dumps([item.model_dump(mode="json") for item in records], indent=2), encoding="utf-8"
        )
        temporary.replace(self.records_file)

    def list(self, work_id: str) -> list[DocumentRecord]:
        return [item for item in self._records() if item.work_id == work_id]

    def get(self, document_id: str) -> DocumentRecord | None:
        return next((item for item in self._records() if item.id == document_id), None)

    def _persist(self, record: DocumentRecord) -> DocumentRecord:
        records = [item for item in self._records() if item.id != record.id]
        records.append(record)
        self._save_records(records)
        return record

    def add_pdf(self, *, work_id: str, name: str, content: bytes, origin: str, source_url: str | None = None) -> DocumentRecord:
        if len(content) > self.max_bytes:
            raise DocumentError("The PDF exceeds the configured upload limit.", code="invalid_pdf")
        if not content.startswith(b"%PDF-"):
            raise DocumentError("The selected file is not a valid PDF.", code="invalid_pdf")
        document_id = uuid4().hex
        path = self.root / f"{document_id}.pdf"
        path.write_bytes(content)
        record = DocumentRecord(
            id=document_id,
            work_id=work_id,
            display_name=name,
            origin=origin,
            source_url=source_url,
            local_path=str(path),
            status="queued",
            created_at=datetime.now(UTC),
        )
        self._persist(record)
        return self.extract(record)

    async def fetch_open_access(self, work: NormalizedWork) -> DocumentRecord:
        if not work.pdf.is_open_access or not work.pdf.url:
            raise DocumentError("No verified open-access PDF is available.", code="pdf_unavailable")
        owns_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=30, follow_redirects=True)
        try:
            response = await client.get(str(work.pdf.url))
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DocumentError("The open-access PDF could not be fetched.", code="network") from exc
        finally:
            if owns_client:
                await client.aclose()
        return self.add_pdf(
            work_id=work.id,
            name=str(work.pdf.url).rsplit("/", 1)[-1] or "open-access.pdf",
            content=response.content,
            origin="open_access",
            source_url=str(work.pdf.url),
        )

    def extract(self, record: DocumentRecord) -> DocumentRecord:
        extracting = record.model_copy(update={"status": "extracting", "error": None})
        self._persist(extracting)
        try:
            document = fitz.open(extracting.local_path)
            pages = [{"page": index + 1, "text": page.get_text("text")} for index, page in enumerate(document)]
            document.close()
            if not any(page["text"].strip() for page in pages):
                raise DocumentError(
                    "No extractable text was found; this may be a scanned PDF.", code="unreadable_pdf"
                )
            self.text_cache.set("extracted_text", extracting.id, pages)
            ready = extracting.model_copy(update={"status": "ready", "page_count": len(pages)})
            return self._persist(ready)
        except Exception as exc:
            message = str(exc) if isinstance(exc, DocumentError) else "PDF text extraction failed."
            failed = extracting.model_copy(update={"status": "failed", "error": message})
            self._persist(failed)
            if isinstance(exc, DocumentError):
                raise
            raise DocumentError(message, code="extraction_failed") from exc
