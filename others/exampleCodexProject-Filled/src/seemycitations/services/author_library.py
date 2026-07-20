from __future__ import annotations

import asyncio
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Awaitable, Callable

from seemycitations.models import AuthorCandidate, NormalizedWork

Download = Callable[[NormalizedWork], Awaitable[bytes]]


def safe_key(value: str) -> str:
    value = value.rsplit("/", 1)[-1]
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned[:120] or hashlib.sha256(value.encode()).hexdigest()[:16]


class AuthorLibrary:
    schema_version = 1

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, asyncio.Lock] = {}

    def author_key(self, provider: str, author_id: str) -> str:
        return f"{safe_key(provider).lower()}_{safe_key(author_id)}"

    def author_dir(self, provider: str, author_id: str) -> Path:
        return self.root / self.author_key(provider, author_id)

    def _index_path(self, provider: str, author_id: str) -> Path:
        return self.author_dir(provider, author_id) / "index.json"

    def load(self, provider: str, author_id: str) -> dict | None:
        path = self._index_path(provider, author_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if data.get("schema_version") == self.schema_version else None
        except (OSError, json.JSONDecodeError):
            return None

    def _write(self, provider: str, author_id: str, index: dict) -> None:
        folder = self.author_dir(provider, author_id)
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / "index.json"
        temporary = folder / ".index.json.tmp"
        temporary.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(target)

    def reconcile(self, author: AuthorCandidate, works: list[NormalizedWork]) -> dict:
        now = datetime.now(UTC).isoformat()
        current = self.load(author.provider, author.id) or {
            "schema_version": self.schema_version,
            "author": {},
            "last_synced_at": None,
            "papers": {},
        }
        current["author"] = author.model_dump(mode="json")
        current["last_synced_at"] = now
        for work in works:
            work_key = safe_key(work.id)
            previous = current["papers"].get(work_key, {})
            current["papers"][work_key] = {
                **work.model_dump(mode="json"),
                "first_seen_at": previous.get("first_seen_at", now),
                "last_seen_at": now,
                "documents": previous.get("documents", []),
                "library_state": previous.get("library_state", "new"),
            }
        self._write(author.provider, author.id, current)
        return current

    def _valid_document(self, author_dir: Path, document: dict) -> bool:
        relative = Path(document.get("relative_path", ""))
        if relative.is_absolute() or ".." in relative.parts:
            return False
        path = author_dir / relative
        if not path.is_file():
            return False
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return digest == document.get("sha256") and path.read_bytes().startswith(b"%PDF-")

    async def sync_downloads(
        self,
        author: AuthorCandidate,
        works: list[NormalizedWork],
        download: Download,
    ) -> dict:
        key = self.author_key(author.provider, author.id)
        async with self._locks.setdefault(key, asyncio.Lock()):
            index = self.reconcile(author, works)
            folder = self.author_dir(author.provider, author.id)
            summary = {"discovered": len(works), "already_local": 0, "downloaded": 0, "failed": 0, "upload_required": 0}
            by_id = {safe_key(work.id): work for work in works}
            known_hashes: dict[str, dict] = {}
            for existing in index["papers"].values():
                for document in existing.get("documents", []):
                    if self._valid_document_folder(folder, document):
                        known_hashes[document["sha256"]] = document
            for work_key, paper in index["papers"].items():
                valid = [doc for doc in paper["documents"] if self._valid_document_folder(folder, doc)]
                if valid:
                    paper["documents"] = valid
                    paper["library_state"] = "reused"
                    summary["already_local"] += 1
                    continue
                paper["documents"] = []
                work = by_id.get(work_key)
                if work is None or not work.pdf.is_open_access or not work.pdf.url:
                    paper["library_state"] = "upload required"
                    summary["upload_required"] += 1
                    continue
                try:
                    content = await download(work)
                    if not content.startswith(b"%PDF-"):
                        raise ValueError("Remote content is not a PDF")
                    digest = hashlib.sha256(content).hexdigest()
                    duplicate = known_hashes.get(digest)
                    if duplicate:
                        paper["documents"] = [duplicate]
                        paper["library_state"] = "reused"
                        summary["already_local"] += 1
                        continue
                    paper_dir = folder / "papers" / work_key
                    paper_dir.mkdir(parents=True, exist_ok=True)
                    target = paper_dir / "paper.pdf"
                    temporary = paper_dir / ".paper.pdf.tmp"
                    temporary.write_bytes(content)
                    temporary.replace(target)
                    now = datetime.now(UTC).isoformat()
                    paper["documents"] = [{
                        "origin": "open_access", "source_url": str(work.pdf.url),
                        "relative_path": str(target.relative_to(folder)), "byte_size": len(content),
                        "sha256": digest, "status": "ready", "error": None,
                        "page_count": None, "created_at": now, "verified_at": now,
                    }]
                    known_hashes[digest] = paper["documents"][0]
                    paper["library_state"] = "downloaded"
                    summary["downloaded"] += 1
                except Exception as exc:
                    paper["library_state"] = "failed"
                    paper["last_error"] = str(exc)
                    summary["failed"] += 1
            self._write(author.provider, author.id, index)
            return {"author_key": key, "summary": summary, "papers": index["papers"]}

    def _valid_document_folder(self, folder: Path, document: dict) -> bool:
        return self._valid_document(folder, document)
