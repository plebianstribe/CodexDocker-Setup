from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from seemycitations.models import AuthorCandidate, NormalizedWork, PdfAvailability
from seemycitations.services.author_library import AuthorLibrary, safe_key


PDF = b"%PDF-1.4\nfixture evidence\n%%EOF"


def author() -> AuthorCandidate:
    return AuthorCandidate(id="https://openalex.org/A123", name="Mehul Motani", provider="OpenAlex")


def work(identifier: str, *, oa: bool = True) -> NormalizedWork:
    return NormalizedWork(
        id=f"https://openalex.org/{identifier}", title=f"Paper {identifier}", authors=["Mehul Motani"],
        year=2026, venue="Fixture", doi=f"10.1/{identifier}", source_url=f"https://example.org/{identifier}",
        citation_count=1, citation_source="OpenAlex", retrieved_at=datetime.now(UTC),
        pdf=PdfAvailability(url=f"https://example.org/{identifier}.pdf" if oa else None, is_open_access=oa),
    )


@pytest.mark.asyncio
async def test_author_folder_restart_and_identical_sync_skip_download(tmp_path: Path) -> None:
    library = AuthorLibrary(tmp_path)
    calls = []
    async def download(item):
        calls.append(item.id)
        return PDF
    first = await library.sync_downloads(author(), [work("W1")], download)
    assert first["summary"]["downloaded"] == 1
    folder = tmp_path / "openalex_A123"
    assert (folder / "index.json").is_file()
    assert (folder / "papers" / "W1" / "paper.pdf").is_file()
    restarted = AuthorLibrary(tmp_path)
    second = await restarted.sync_downloads(author(), [work("W1")], download)
    assert second["summary"]["already_local"] == 1
    assert len(calls) == 1
    assert restarted.load("OpenAlex", author().id)["papers"]["W1"]["library_state"] == "reused"


@pytest.mark.asyncio
async def test_delta_sync_downloads_only_new_paper_and_retains_old(tmp_path: Path) -> None:
    library = AuthorLibrary(tmp_path)
    calls = []
    async def download(item):
        calls.append(item.id)
        return PDF + item.id.encode()
    await library.sync_downloads(author(), [work("W1")], download)
    result = await library.sync_downloads(author(), [work("W1"), work("W2")], download)
    assert result["summary"] == {"discovered": 2, "already_local": 1, "downloaded": 1, "failed": 0, "upload_required": 0}
    assert calls == ["https://openalex.org/W1", "https://openalex.org/W2"]
    assert set(result["papers"]) == {"W1", "W2"}


@pytest.mark.asyncio
async def test_missing_hash_mismatch_and_oa_guard(tmp_path: Path) -> None:
    library = AuthorLibrary(tmp_path)
    calls = 0
    async def download(_item):
        nonlocal calls
        calls += 1
        return PDF
    await library.sync_downloads(author(), [work("W1")], download)
    path = tmp_path / "openalex_A123" / "papers" / "W1" / "paper.pdf"
    path.write_bytes(b"corrupt")
    await library.sync_downloads(author(), [work("W1")], download)
    result = await library.sync_downloads(author(), [work("W1"), work("W2", oa=False)], download)
    assert calls == 2
    assert result["papers"]["W2"]["library_state"] == "upload required"


def test_paths_are_sanitized_and_index_writes_are_atomic(tmp_path: Path) -> None:
    assert safe_key("../../A:123") == "A_123"
    library = AuthorLibrary(tmp_path)
    index = library.reconcile(author(), [work("../W:1", oa=False)])
    folder = tmp_path / "openalex_A123"
    assert "W_1" in index["papers"]
    assert not (folder / ".index.json.tmp").exists()
    assert json.loads((folder / "index.json").read_text())["schema_version"] == 1


def test_interrupted_atomic_replace_preserves_previous_index(tmp_path: Path, monkeypatch) -> None:
    library = AuthorLibrary(tmp_path)
    library.reconcile(author(), [work("W1", oa=False)])
    target = tmp_path / "openalex_A123" / "index.json"
    before = target.read_bytes()
    original_replace = Path.replace
    def fail_replace(self, destination):
        if self.name == ".index.json.tmp":
            raise OSError("simulated interruption")
        return original_replace(self, destination)
    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated interruption"):
        library.reconcile(author(), [work("W1", oa=False), work("W2", oa=False)])
    assert target.read_bytes() == before


@pytest.mark.asyncio
async def test_identical_content_is_deduplicated_across_papers(tmp_path: Path) -> None:
    library = AuthorLibrary(tmp_path)
    calls = 0
    async def download(_item):
        nonlocal calls
        calls += 1
        return PDF
    result = await library.sync_downloads(author(), [work("W1"), work("W2")], download)
    assert calls == 2
    documents = [paper["documents"][0] for paper in result["papers"].values()]
    assert documents[0]["sha256"] == documents[1]["sha256"]
    assert documents[0]["relative_path"] == documents[1]["relative_path"]
    assert len(list((tmp_path / "openalex_A123" / "papers").rglob("*.pdf"))) == 1
