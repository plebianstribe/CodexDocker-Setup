# SEEMYCITATIONS Completion Tracker

Reference goals: `SEEMYCITATIONS_GOALS.md`
Progress log target: `TimeTaken.md`
Updater utility: `update_timetaken.sh`

## Execution Control
- Execution mode: standard
- Latest run ID: RUN-20260720-03
- Current stage cursor: COMPLETE
- Current blocker: none

## Step and Stage Map
| step_id | stage_id | depends_on | status | parallel group |
|---|---|---|---|---|
| SG-01 | STAGE-01 | none | Completed | A |
| SG-02 | STAGE-02 | SG-01 | Completed | A |
| SG-03 | STAGE-03 | SG-02 | Completed | A |
| SG-04 | STAGE-04 | SG-03 | Completed | A |
| SG-05 | STAGE-05 | SG-04 | Completed | A |
| SG-06 | STAGE-06 | SG-05 | Completed | A |
| SG-07 | STAGE-07 | SG-06 | Completed | A |
| SG-08 | STAGE-08 | SG-07 | Completed | A |

## Stage Dependency Graph
- STAGE-01 -> none
- STAGE-02 -> STAGE-01
- STAGE-03 -> STAGE-02
- STAGE-04 -> STAGE-03
- STAGE-05 -> STAGE-04
- STAGE-06 -> STAGE-05
- STAGE-07 -> STAGE-06
- STAGE-08 -> STAGE-07

## Evidence Log
- RUN-20260720-01: execution started; evidence is appended here only after each harsh gate.
- SG-01 / STAGE-01 — PASS: `uv run pytest tests/test_foundation.py -q` (2 passed); app import and dependency versions verified. Artifact: `artifacts/stage-01/pytest.log`. Non-blocking: upstream TestClient deprecation warning.
- SG-02 / STAGE-02 — PASS: `uv run pytest tests/test_openalex.py tests/test_api.py -q` (5 passed); normalization, ambiguity, and API contracts verified. Artifact: `artifacts/stage-02/pytest.log`.
- SG-03 / STAGE-03 — PASS: `uv run pytest tests/test_cache.py tests/test_api.py -q` (7 passed); metadata/text cache paths, call reduction, corruption handling, and actionable failure-state map verified. Artifact: `artifacts/stage-03/pytest.log`.
- SG-04 / STAGE-04 — PASS: `uv run pytest tests/test_documents.py tests/test_api.py -q` (8 passed); authorized acquisition guard, upload validation, extraction persistence, page-text cache, and document switching verified. Artifact: `artifacts/stage-04/pytest.log`.
- SG-05 / STAGE-05 — PASS: `uv run pytest tests/test_keywords.py tests/test_api.py -q` (8 passed); parsing, case-insensitive whole-word counts, deterministic ordering, zero terms, pages, and snippets verified. Artifact: `artifacts/stage-05/pytest.log`.
- SG-06 / STAGE-06 — PASS: `uv run pytest -q` (21 passed); live keyless OpenAlex author-search smoke test succeeded; `npm run test:ui` completed the no-reload workflow with 6 marked actions, 700 ms minimum spacing, and zero pacing violations. Artifacts: `artifacts/stage-06/pytest.log`, `artifacts/stage-06/playwright.log`, and `artifacts/ui/run-20260720-01/` (screenshots, trace, video, action log, report). Non-blocking: upstream TestClient deprecation warning; manual assistive-technology evaluation remains recommended before public deployment.
- PLANNED-RUN-20260720-02: SG-07 added by goal refinement; no implementation evidence or PASS verdict exists yet.
- SG-07 / STAGE-07 — PASS (RUN-20260720-02): `uv run pytest tests/test_author_library.py tests/test_documents.py tests/test_api.py -q` (14 passed) and full regression (26 passed). Call spies prove an identical sync makes zero additional PDF requests and a one-paper delta makes exactly one; restart, hash drift, OA guard, deduplication, safe paths, and interrupted atomic replacement pass. Live keyless OpenAlex/Playwright search for `Mehul Motani` returned 3 candidates, indexed 100 works at `data/authors/openalex_A5069355437/index.json`, opened a work, and produced 3 marked actions with 700 ms minimum spacing and zero violations. Artifacts: `artifacts/stage-07/` and `artifacts/ui/run-20260720-02/`.
- RUN-20260720-03: SG-08 started for automatic keyword suggestions and navigable full-document reader; evidence pending harsh gate.
- SG-08 / STAGE-08 — PASS (RUN-20260720-03): `uv run pytest -q` passed 31 tests. `npm run test:ui:reader` populated editable frequency suggestions, rendered all fixture pages at an exact 0.75 preview ratio, scrolled/focused/highlighted the selected match, minimized/restored the sidebar, and restored edited state through Back. Eight marked actions met the 700 ms policy with zero violations. Artifacts: `artifacts/stage-08/` and `artifacts/ui/run-20260720-03/`.

## Stage-Sorted Plan

### STAGE-01 — Foundation (unlock: none)
- Status: Completed
- Parallel group: A
- Tasks:
  - Finalize backend/frontend/PDF stack.
  - Scaffold architecture with replaceable scholarly adapter boundary.
  - Document run/setup/choice rationale in `README.md`.
- Deterministic unlock condition:
  - Stage marked complete only when stack choices and runnable scaffold are documented and present.
- Completion logging command:
  - `./update_timetaken.sh STAGE-01 "Scaffolded project foundation and documented architecture/tooling decisions."`

### STAGE-02 — Metadata + Normalization (unlock: STAGE-01 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Implement provider adapter and author search.
  - Normalize work model per `PROJECT.md` fields.
  - Surface ambiguous author matches.
- Deterministic unlock condition:
  - Normalization outputs include required canonical fields with passing targeted tests.
- Completion logging command:
  - `./update_timetaken.sh STAGE-02 "Implemented author metadata retrieval through adapter with normalized citation records."`

### STAGE-03 — Cache + Error States (unlock: STAGE-02 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Add metadata/text caching.
  - Add actionable states for network/rate/PDF availability/readability outcomes.
  - Demonstrate duplicate-work reduction paths.
- Deterministic unlock condition:
  - Repeated requests hit cache paths and failure modes map to explicit user-facing states.
- Completion logging command:
  - `./update_timetaken.sh STAGE-03 "Added local cache and resilient user-facing handling for API/PDF failure states."`

### STAGE-04 — PDF Flow + Extraction (unlock: STAGE-03 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Support local PDF upload.
  - Gate remote fetch to explicit open-access sources.
  - Enable selection/switching between available PDFs.
  - Persist extraction status/error metadata.
- Deterministic unlock condition:
  - Authorized PDF acquisition and extraction pipeline both execute with persisted status outcomes.
- Completion logging command:
  - `./update_timetaken.sh STAGE-04 "Enabled authorized PDF upload/fetch, selection flow, and persisted extraction status."`

### STAGE-05 — Keyword Analytics (unlock: STAGE-04 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Implement case-insensitive whole-word keyword counting.
  - Normalize input handling for punctuation/case/repeats/empties.
  - Return sorted counts with per-page locations and snippets.
- Deterministic unlock condition:
  - Deterministic keyword tests pass and payload includes sorted counts + page snippets.
- Completion logging command:
  - `./update_timetaken.sh STAGE-05 "Implemented reproducible keyword frequency analytics with page-level match snippets."`

### STAGE-06 — E2E Validation + Docs (unlock: STAGE-05 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Verify complete no-reload workflow.
  - Run/record unit tests for normalization + keyword logic.
  - Finalize setup/config/attribution/boundary docs.
- Deterministic unlock condition:
  - Acceptance criteria mapping is complete and validation evidence is recorded.
- Completion logging command:
  - `./update_timetaken.sh STAGE-06 "Completed end-to-end workflow validation, tests, and delivery documentation."`

### STAGE-07 — Per-Author Library + Incremental Sync (unlock: STAGE-06 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Introduce deterministic provider-qualified author folders and versioned, atomic `index.json` catalogs.
  - Move or route paper PDFs and document metadata into deterministic per-author/per-paper paths.
  - Reconcile provider metadata by stable work identity while retaining local history and files.
  - Verify local files by relative path and content hash before planning remote work.
  - Download only newly discovered or locally missing eligible OA PDFs; retain upload-only behavior otherwise.
  - Expose per-paper sync state and author-level discovered/reused/downloaded/failed totals.
  - Document the storage schema, recovery behavior, and backup/migration boundary.
- Deterministic unlock condition:
  - SG-07 is marked complete only when restart reconstruction passes, a repeated identical sync produces zero PDF download calls, a one-paper delta produces exactly one eligible PDF download, prior indexed files remain intact, and corruption/OA/path/atomic-write gates pass.
- Required evidence:
  - Changed-file manifest and documented example folder tree.
  - `uv run pytest tests/test_author_library.py tests/test_documents.py tests/test_api.py` output.
  - Spy/call-count artifacts for identical-sync and one-paper-delta scenarios.
  - Playwright artifacts when library/sync state changes the UI.
- Completion logging command:
  - `./update_timetaken.sh STAGE-07 "Added durable per-author paper indexes and incremental PDF synchronization that reuses verified local downloads."`

### STAGE-08 — Automatic Keywords + PDF Reader (unlock: STAGE-07 complete)
- Status: Completed
- Parallel group: A
- Tasks:
  - Add deterministic local frequency/phrase keyword extraction and suggestion API.
  - Populate an editable keyword field whenever a ready document is selected.
  - Replace `Analyze keywords` with `Find keywords` and transition to a dedicated reader.
  - Render all extracted pages in a 75/25 preview/sidebar layout with stable match anchors.
  - Add match-click scroll/focus/highlighting, sidebar minimize/restore, and Back restoration.
- Deterministic unlock condition:
  - SG-08 completes only when extractor/API tests pass and Playwright artifacts prove editable suggestions, the reader transition, desktop 75/25 geometry, match autoscroll/focus/highlight, sidebar minimize/restore, Back state restoration, and compliant click timing.
- Completion logging command:
  - `./update_timetaken.sh STAGE-08 "Added automatic editable keyword extraction and a navigable highlighted full-document reader."`

## Blocker Handling
- If a stage is blocked, record:
  - blocker summary,
  - impacted stage,
  - immediate mitigation attempt,
  - required external decision/input.
- Do not unlock dependent stages until blocker is resolved and prior stage completion criteria are met.

## Evidence Requirements
- For each stage completion, provide:
  - changed file list,
  - command/test evidence (where applicable),
  - one-line functional completion summary.
- After stage acceptance, append `TimeTaken.md` entry via `update_timetaken.sh`.
