# SeeMyCitations

SeeMyCitations is a local web application for finding scholarly works by author, reviewing provider-attributed citation metadata, attaching PDFs the user is authorized to access, and inspecting reproducible page-level keyword matches.

## Current completion

The planned application stages are implemented:

- Keyless OpenAlex author search, author disambiguation, normalized works, citation provenance, caching, and recoverable errors.
- Durable per-author folders with atomic paper indexes and hash-verified reuse of previously downloaded PDFs.
- Explicit local PDF upload and remote download only when OpenAlex identifies an open-access PDF.
- Page-preserving PDF text extraction, deterministic whole-word matching, and page-level snippets.
- Automatic local frequency-based keyword suggestions in a user-editable field.
- A **Find keywords** reader with a 75/25 full-document and match-sidebar layout, highlighted match navigation, collapsible sidebar, and **Back to papers** navigation.
- Automated Python and Playwright coverage with screenshots, traces, video, and paced action logs.

No API key is required. `OPENALEX_EMAIL` is an optional contact address for polite OpenAlex usage.

## Stack and rationale

- **FastAPI + Uvicorn:** typed async API endpoints and a small local server.
- **Server-hosted HTML + vanilla JavaScript:** a lightweight, accessible single-page workflow without a frontend build toolchain.
- **OpenAlex adapter:** broad scholarly metadata and open-access location metadata. Basic use is free and does not require an API key. Set `OPENALEX_EMAIL` to identify requests to the OpenAlex polite pool; it is an email address, not a secret.
- **PyMuPDF:** page-preserving PDF text extraction suitable for page-level evidence.
- **Filesystem JSON cache:** transparent, local, reproducible caching with no database service.
- **pytest + HTTPX:** deterministic unit and API-level checks.

The scholarly provider lives behind `ScholarlyAdapter`, so another provider can replace OpenAlex without changing the normalized models or UI contract. Citation retrieval and PDF acquisition are separate: metadata never grants permission to fetch a file.

## Launch the app

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn seemycitations.main:app --host 0.0.0.0 --port 8888
```

Open <http://localhost:8888>. From another machine, use the host machine's IP address with port `8888`.

Verify the server:

```bash
curl http://127.0.0.1:8888/health
# Expected: {"status":"ok"}
```

For development with automatic reload, append `--reload`. Stop the server with `Ctrl+C`.

## Durable author libraries

Selecting an author reconciles their current OpenAlex works into a durable provider-qualified folder without downloading PDFs automatically:

```text
data/authors/openalex_A123/
├── index.json
└── papers/
    └── W456/
        └── paper.pdf
```

`index.json` is versioned and atomically replaced. It retains normalized paper metadata, first/last-seen times, local document paths, SHA-256 hashes, and sync state. The **Sync new open-access PDFs** action verifies indexed hashes first, reuses valid local files, and requests only new or missing PDFs that OpenAlex explicitly marks open access. Missing closed-access files remain `upload required`; no paywall is bypassed. Back up `data/authors/` to preserve the library. A later schema change must migrate `schema_version` rather than silently rewriting incompatible data.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `OPENALEX_EMAIL` | unset | Optional contact email appended to OpenAlex requests; no API key required |
| `SEEMYCITATIONS_DATA_DIR` | `data` | Local cache, upload, and extracted-text root |
| `SEEMYCITATIONS_MAX_UPLOAD_MB` | `25` | Maximum accepted PDF upload size |

Keep any future provider secrets in environment variables and out of source control.

## Automatic keyword reader

When a PDF reaches `ready`, the app ranks repeated local terms and two-/three-word phrases after filtering common stop words and noise. Suggestions are placed in an editable field; the user's final text is authoritative. **Find keywords** opens a page-preserving extracted-text reader with the full document on the left and every keyword match on the right. Selecting a match scrolls to, focuses, and highlights the exact passage. The sidebar can be minimized, and **Back to papers** restores the current author, work, document, keywords, and results. This extraction runs locally and requires no model or API key.

## Boundaries

- Only explicit open-access PDF locations may be fetched remotely.
- Users are responsible for authorization of locally uploaded documents.
- Citation counts retain provider attribution and retrieval time.
- Scanned/image-only PDFs return an actionable error; OCR is not part of the initial scope.

## Tests

```bash
uv run pytest
npm install
npx playwright install chromium
npm run test:ui
```

The browser capture uses deterministic fixture responses, 700 ms minimum click spacing, persistent click markers, and writes screenshots, trace, video, action log, and a capture report under `artifacts/ui/run-20260720-01/`.

## Acceptance coverage

- Author ambiguity: candidates display affiliation, works/citation counts, topics, provider, and stable ID before user selection.
- Citation provenance: every count is labelled OpenAlex and normalized works retain retrieval time.
- PDF authorization: local upload is explicit; remote fetch is offered only for an OpenAlex location marked open access.
- Processing recovery: invalid, image-only, network, and extraction failure states retain actionable messages and persisted document status.
- Keyword evidence: case-insensitive whole-word results retain zero counts, deterministic ordering, pages, and snippets.
- Accessibility baseline: semantic headings/forms, keyboard-native controls, visible focus, live status regions, non-color state labels, 44 px controls, reduced-motion handling, and responsive stacking are built in. The deterministic browser capture verifies the critical no-reload workflow; manual assistive-technology evaluation remains recommended before public deployment.

The delivery stages and evidence requirements are tracked in [SEEMYCITATIONS_GOALS.md](SEEMYCITATIONS_GOALS.md) and [SEEMYCITATIONS_COMPLETIONTRACKER.md](SEEMYCITATIONS_COMPLETIONTRACKER.md).
