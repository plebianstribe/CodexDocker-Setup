# SEEMYCITATIONS Goals

## Objective
Deliver a local web application based on `PROJECT.md` that searches scholarly works by author, shows normalized citation metadata, maintains a durable per-author paper/PDF library, supports authorized PDF selection/upload, and provides reproducible keyword frequency with page-level matches.

## Active Goal Scope
Single non-recursive scope for delivery and incremental extension of the Author Citation and PDF Keyword Explorer described in `PROJECT.md`, including durable per-author synchronization.

## Reuse Decision
- Reuse current repository baseline as starting scaffold.
- No existing `*_GOALS.md` or `*_COMPLETIONTRACKER.md` artifacts were found for this scope.
- Create fresh canonical artifacts: `SEEMYCITATIONS_GOALS.md` and `SEEMYCITATIONS_COMPLETIONTRACKER.md`.
- Reuse the completed SG-01 through SG-06 application and evidence; add SG-07 as an incremental stage rather than reopening previously accepted work.

## Subgoal Plan

### SG-01 (stage_id: STAGE-01) — Project foundation and architecture decisions
- step_id: SG-01
- status: completed
- Dependencies: none.
- depends_on: []
- expected_outputs: `pyproject.toml`, `src/seemycitations/`, `README.md`
- expected_functional_change: A runnable local application skeleton with replaceable scholarly-provider boundary.
- required_tests: `uv run pytest`; `uv run python -c "from seemycitations.main import app; print(app.title)"`
- evidence: PASS (RUN-20260720-01); `artifacts/stage-01/pytest.log`, package import/version verification, runnable scaffold and `README.md`.
- Acceptance criteria:
  - Backend framework, frontend approach, and PDF/text libraries are selected.
  - Initial project structure supports adapter pattern for metadata providers.
  - `README.md` includes setup, run commands, and architecture rationale.
- Evidence hooks:
  - Committed project tree with skeleton modules.
  - `README.md` entries for chosen stack and run steps.

### SG-02 (stage_id: STAGE-02) — Scholarly metadata retrieval + normalization
- step_id: SG-02
- status: completed
- Dependencies: STAGE-01.
- depends_on: [SG-01]
- expected_outputs: OpenAlex adapter, normalized models, API routes, fixtures, and unit tests.
- expected_functional_change: Users can choose among ambiguous author candidates and view normalized, provider-attributed works.
- required_tests: `uv run pytest tests/test_openalex.py tests/test_api.py`
- evidence: PASS (RUN-20260720-01); `artifacts/stage-02/pytest.log` (5 passed), OpenAlex fixture normalization and API route checks.
- Acceptance criteria:
  - Author search uses one public provider (OpenAlex or Semantic Scholar) through replaceable adapter.
  - Normalized work model includes identifiers, authors, venue/year, DOI/source URL, citation fields, retrieval timestamp, and PDF availability metadata.
  - Ambiguous author results are exposed explicitly.
- Evidence hooks:
  - Adapter interface and first implementation.
  - Normalization unit tests and sample fixtures.

### SG-03 (stage_id: STAGE-03) — Caching and resilient error handling
- step_id: SG-03
- status: completed
- Dependencies: STAGE-02.
- depends_on: [SG-02]
- expected_outputs: Local cache service, cache tests, and typed API/UI error states.
- expected_functional_change: Repeated metadata requests avoid provider calls and failures preserve actionable context.
- required_tests: `uv run pytest tests/test_cache.py tests/test_api.py`
- evidence: PASS (RUN-20260720-01); `artifacts/stage-03/pytest.log` (7 passed), provider call-count cache assertion, extracted-text cache payload, and error recovery map.
- Acceptance criteria:
  - Metadata responses and extracted text are cached locally.
  - Distinct actionable states exist for rate limits, network failures, no matches, unavailable PDFs, and unreadable PDFs.
  - Cache reduces duplicate API/extraction work in repeated flows.
- Evidence hooks:
  - Cache module and cache-hit assertions/logging.
  - Error-state tests or deterministic handling checks.

### SG-04 (stage_id: STAGE-04) — PDF acquisition, selection, and text extraction
- step_id: SG-04
- status: completed
- Dependencies: STAGE-03.
- depends_on: [SG-03]
- expected_outputs: Upload/OA fetch endpoints, document repository, PDF extraction service, and tests.
- expected_functional_change: Users can attach, fetch only OA-eligible, switch, and process PDFs with persisted outcomes.
- required_tests: `uv run pytest tests/test_documents.py tests/test_api.py`
- evidence: PASS (RUN-20260720-01); `artifacts/stage-04/pytest.log` (8 passed), PDF validation/extraction, OA guard, persisted failures, and multi-document selection tests.
- Acceptance criteria:
  - Local PDF uploads supported.
  - Remote PDF fetch allowed only when marked open access.
  - User can select and switch among available PDFs.
  - Extraction status and processing errors are persisted per work/document.
- Evidence hooks:
  - Upload/fetch handlers with OA guardrails.
  - Extraction pipeline outputs with status fields.

### SG-05 (stage_id: STAGE-05) — Keyword frequency and page-level matches
- step_id: SG-05
- status: completed
- Dependencies: STAGE-04.
- depends_on: [SG-04]
- expected_outputs: Keyword parser/counter, analysis endpoint, page snippets, and deterministic tests.
- expected_functional_change: Users receive sorted whole-word counts and verifiable page-level evidence.
- required_tests: `uv run pytest tests/test_keywords.py tests/test_api.py`
- evidence: PASS (RUN-20260720-01); `artifacts/stage-05/pytest.log` (8 passed), deterministic parser/count/order/page-snippet tests.
- Acceptance criteria:
  - Case-insensitive whole-word matching by default.
  - Multiple keywords supported with consistent handling of empty input, punctuation, capitalization, and repeated terms.
  - Counts are sorted high-to-low and reproducible.
  - Clicking keyword result reveals page-level locations and short snippets.
- Evidence hooks:
  - Keyword parser/counter module and deterministic tests.
  - UI/API response showing per-page snippet payload.

### SG-06 (stage_id: STAGE-06) — End-to-end UX completion and verification
- step_id: SG-06
- status: completed
- Dependencies: STAGE-05.
- depends_on: [SG-05]
- expected_outputs: Complete accessible UI, end-to-end tests/evidence, and final documentation.
- expected_functional_change: The full author-to-page-evidence workflow completes without reload and with recovery states.
- required_tests: `uv run pytest`; deterministic browser workflow command documented in evidence.
- evidence: PASS (RUN-20260720-01); 21-test full suite, live keyless OpenAlex smoke test, and Playwright artifacts under `artifacts/ui/run-20260720-01/` with 6 paced marked actions and zero timing violations.
- Acceptance criteria:
  - Full workflow completes without page reload errors.
  - Unit tests cover normalization and keyword logic.
  - Documentation covers setup/configuration/attribution and operational boundaries.
- Evidence hooks:
  - Test run output for targeted suites.
  - Final README coverage checklist tied to `PROJECT.md` acceptance criteria.

### SG-07 (stage_id: STAGE-07) — Durable per-author paper library and incremental synchronization
- step_id: SG-07
- status: completed
- Dependencies: STAGE-06.
- depends_on: [SG-06]
- expected_outputs: per-author storage service, versioned author/paper index schema, migration/reconciliation logic, incremental download planner, UI/API library status, documentation, fixtures, and deterministic tests.
- expected_functional_change: Each selected author has a durable local folder containing an indexed catalog of discovered papers and authorized PDFs, and later refreshes reuse valid local files while downloading only newly discovered or locally missing eligible PDFs.
- required_tests: `uv run pytest tests/test_author_library.py tests/test_documents.py tests/test_api.py`; `npm run test:ui` for visible saved/downloaded/reused status when the UI changes.
- evidence: PASS (RUN-20260720-02); 14 targeted tests, 26-test full regression, zero-download repeat and one-download delta spies, live Mehul Motani OpenAlex/UI verification, and Playwright artifacts under `artifacts/ui/run-20260720-02/`.
- Acceptance criteria:
  - The data root contains one deterministic folder per provider-qualified author identity using a collision-safe key such as `openalex_A123`; display names may be stored as metadata but must not be the sole filesystem identity.
  - Each author folder contains an atomic, versioned `index.json` with author identity, provider, display metadata, `last_synced_at`, and one entry per normalized paper.
  - Every paper index entry preserves the provider work ID, title, authors, year, venue, DOI/source URL, citation provenance/retrieval time, OA metadata, first/last-seen timestamps, and local document records.
  - Authorized PDFs are stored beneath that author folder in deterministic per-paper locations such as `papers/<provider_work_id>/`, with filenames and paths sanitized against traversal and invalid characters.
  - Local document records include origin, source URL, relative path, byte size, content hash, processing status/error, page count, and created/verified timestamps.
  - Refresh reconciles the latest provider result set with `index.json` by stable provider work ID, updating mutable metadata without deleting papers or PDFs that are absent from one provider response.
  - Before any remote PDF request, the planner checks the paper's indexed local records and filesystem. A readable file whose recorded content hash matches is marked `reused` and causes zero network download calls.
  - Only papers that are newly discovered or lack a valid local PDF may enter the download queue, and remote downloading remains restricted to explicit open-access locations.
  - A missing, corrupt, or hash-mismatched indexed file is marked accordingly and may be re-downloaded only when an eligible OA URL exists; otherwise the UI exposes an upload-required recovery state.
  - Duplicate DOI variants, provider IDs, URLs, or identical content hashes must not create duplicate paper/PDF records within an author library.
  - Concurrent or interrupted synchronization cannot leave a partially written index: writes use a temporary file plus atomic replacement, and a failed download never replaces a previously valid PDF.
  - The UI/API reports per-paper states including `saved locally`, `new`, `downloaded`, `reused`, `missing`, `failed`, and `upload required`, plus an author-level summary of discovered, already-local, downloaded, and failed counts.
  - The author library survives application restart and can be reconstructed from `index.json` and relative paths without requiring an API call.
- Evidence hooks:
  - Temporary-directory fixture proving the specified author/index/paper directory layout and restart reconstruction.
  - Provider call/download spy proving a second identical sync performs zero PDF downloads.
  - Delta fixture proving a later sync downloads only one newly added eligible paper while retaining all prior paper/PDF records.
  - Corrupt/missing-file, deduplication, path-sanitization, interrupted-write, and OA-guard tests.
  - UI/API evidence showing incremental-sync counts and per-paper local-library states.

### SG-08 (stage_id: STAGE-08) — Automatic keyword extraction and navigable PDF reader
- step_id: SG-08
- status: completed
- Dependencies: STAGE-07.
- depends_on: [SG-07]
- expected_outputs: deterministic frequency-based keyword extractor, suggestion/content APIs, editable keyword workflow, full-document reader view, highlighted match anchors, collapsible sidebar, Back navigation, tests, and Playwright artifacts.
- expected_functional_change: Loading a ready document automatically proposes editable keywords; `Find keywords` opens a page-preserving document reader where selecting any sidebar match scrolls to and highlights the corresponding passage.
- required_tests: `uv run pytest tests/test_keyword_extraction.py tests/test_keywords.py tests/test_api.py`; `npm run test:ui:reader`.
- evidence: PASS (RUN-20260720-03); 31-test full suite and Playwright reader artifacts under `artifacts/ui/run-20260720-03/` prove editable suggestions, exact 75/25 geometry, full-page rendering, match focus/highlight, sidebar minimize/restore, Back restoration, and eight paced actions with zero violations.
- Acceptance criteria:
  - When the active document becomes `ready`, deterministic frequency-based extraction runs over all extracted pages and fills an editable text box with ranked suggestions.
  - Extraction is local, requires no model/API key, filters common stop words and numeric/noise tokens, prefers meaningful two- and three-word phrases when repeated, retains useful single terms, deduplicates case-insensitively, and returns at most the configured limit.
  - User edits are authoritative: additions, removals, capitalization, and ordering in the text box are the exact input to the existing whole-word matcher.
  - The primary action label is `Find keywords`, replacing `Analyze keywords`.
  - `Find keywords` switches from the search/workspace page to a dedicated reader view without reloading the application.
  - At desktop widths the complete page-preserving PDF text preview occupies 75% of the reader and the keyword/match sidebar occupies 25%; responsive layouts remain usable below 1024 px.
  - The preview contains every extracted page in document order with visible page labels and stable anchors; it is not a snippet-only view.
  - The right sidebar lists each keyword with total matches, matching-page count, and every page-numbered snippet.
  - Activating a match scrolls the corresponding full-page passage into view, moves programmatic focus to it, and applies a visible semantic highlight for the exact whole-word match.
  - Match controls are keyboard operable and expose current keyword/page/match position without relying on color alone.
  - The sidebar has a labelled minimize/restore control; minimizing expands the preview and does not discard results or current highlight.
  - A visible `Back to papers` button returns to the prior author/work/document state and preserves the editable keywords and results.
  - Empty extraction, no matches, unreadable content, loading, and API failure states have explicit recovery text and never leave the UI indefinitely busy.
- Evidence hooks:
  - Fixture tests for ranking, phrase preference, stop-word/noise removal, deterministic ties, empty text, and suggestion limit.
  - API tests proving all pages and stable match coordinates are returned without unsafe HTML.
  - Playwright capture proving automatic editable suggestions, `Find keywords`, 75/25 layout, sidebar minimize/restore, match-click autoscroll/focus/highlight, and Back restoration.

## Stage Assignments (in GOALS)
- STAGE-01: SG-01
- STAGE-02: SG-02
- STAGE-03: SG-03
- STAGE-04: SG-04
- STAGE-05: SG-05
- STAGE-06: SG-06
- STAGE-07: SG-07
- STAGE-08: SG-08

## Evidence Requirements
- All stage evidence must be reproducible from repository artifacts and deterministic commands.
- Stage completion update must be appended to `TimeTaken.md` with:
  - UTC+8 timestamp,
  - completed `stage_id`,
  - one-line concrete description of completed functionality/tasks.
- Use `update_timetaken.sh` after each stage completion.

## Open Risks
- API response schema drift from chosen provider.
- PDF text extraction variance across documents.
- Ambiguous author disambiguation quality may require UI iteration.
- Non-text/scanned PDF handling may require optional OCR in follow-up scope.
- Provider work IDs or DOI metadata may merge/split over time; reconciliation must preserve aliases and never silently discard local files.
- Large author libraries may exceed a single-index performance envelope; keep the index schema versioned so a later database migration remains possible.
- Manual deletion or modification of PDFs can desynchronize the index; hash verification and explicit missing/corrupt states must repair rather than conceal drift.
- Concurrent refreshes risk lost index updates; serialize writes per author and use atomic replacement.
- Frequency alone can over-rank boilerplate, references, or extraction artifacts; apply conservative filters and keep every suggestion user-editable.
- Text extraction cannot reproduce graphical PDF layout perfectly; preserve page ordering/labels and clearly treat the reader as an extracted-text preview.
- Very large PDFs can create expensive DOM rendering; render complete text for initial scope but retain stable page anchors for later virtualization.

## UI Expert Refinement Specifications

### 1. Idea Reframe (UI/UX lens)
The product is a local, task-oriented research workspace rather than a generic scholarly search page. Its interface must help a researcher move confidently through four visible steps: identify the correct author, choose a work and authorized PDF, process the document, and inspect reproducible keyword evidence. The UI must preserve context between these steps and make provenance, permissions, and processing state understandable without requiring knowledge of the underlying provider or extraction pipeline.

### 2. Domain Problem and JTBD
- Primary user assumption: a researcher, librarian, student, or research administrator working on a desktop or tablet and evaluating one author or document at a time.
- Core job: "When I investigate an author's publications, help me select the right identity and document, then show where my terms occur so I can verify the evidence quickly."
- Confidence jobs:
  - Distinguish authors with similar names using affiliation, works count, topics, external identifier, and provider attribution.
  - Understand whether a PDF is open access, locally supplied, unavailable, processing, ready, or failed.
  - Trace every keyword count to page-level snippets in the selected document.
- UX success measures: a first-time user can complete the happy path without documentation; no destructive or network action is implicit; the selected author, work, PDF, and matching mode remain visible while reviewing results.

### 3. Solution Blueprint

#### 3.1 Information architecture and persistent context
Use a single-page workspace with the following regions in reading and keyboard-focus order:
1. Application header: product name, short purpose statement, and local/privacy status.
2. Author search and disambiguation.
3. Selected-author summary and works results.
4. Selected-work detail and PDF source controls.
5. Extraction status and keyword analysis.
6. Page-level evidence viewer.

On screens at least 1024 px wide, use a master-detail layout: works list on the left and selected work/document analysis on the right. Below 1024 px, stack the same regions without changing DOM order. Do not hide required actions behind hover-only controls.

#### 3.2 Author search and disambiguation
- Provide a labelled author-name search field, explicit Search button, and Enter-key submission.
- Require at least two non-whitespace characters; show inline guidance rather than sending an invalid request.
- While searching, keep the entered query visible, disable duplicate submission, and show a textual loading status.
- Display ambiguous matches as selectable cards or rows containing: full name, current or most recent affiliation when available, works count, cited-by count, up to three topic hints, external/provider identifier, and provider name.
- Never auto-select an author when multiple matches are returned. Selecting a candidate must update a persistent selected-author summary and load works.
- Provide "Change author" without clearing the query or previously returned candidates.

#### 3.3 Works results
- Show works in a semantic list or table with title as the primary label and year, venue, authors, citation count, DOI/source link, and PDF availability as supporting metadata.
- Default ordering is newest year first; provide explicit controls for newest, oldest, and citation count. Announce the active sort and result count.
- Use distinct text-and-icon badges for `Open-access PDF`, `Upload required`, and `PDF unavailable`; color alone must not carry meaning.
- Selecting a work visibly highlights it, updates the detail panel, and moves focus to the detail heading only when selection was keyboard initiated.
- Long lists require pagination or incremental loading with a visible result range; preserve selection and scroll position when more results load.

#### 3.4 PDF selection and processing
- Present source options in priority order: existing local document, eligible open-access remote PDF, then local upload.
- Remote actions must state the host/domain and use the label `Fetch open-access PDF`; do not offer remote fetch when OA eligibility is absent or unknown.
- Upload must support a standard file picker and optional drag/drop, accept `.pdf`, state the configured size limit before selection, and provide an accessible remove/replace action.
- If multiple documents exist for a work, show a labelled document selector with source, filename or host, added date, page count when known, and processing status.
- Model processing as visible states: `Not started`, `Fetching`, `Uploading`, `Queued`, `Extracting`, `Ready`, and `Failed`. Indeterminate activity includes text, not only a spinner.
- A failure message must preserve the selected work/document and offer one relevant recovery action such as Retry, Replace PDF, or Choose another document.

#### 3.5 Keyword analysis and evidence
- Keep analysis disabled until extraction is `Ready`, with an explanatory message tied to the disabled control.
- Use a labelled multi-keyword input accepting comma or newline separation. Show parsed keyword chips before execution; trim whitespace and collapse case-insensitive duplicates while preserving the first-entered display form.
- Expose `Whole words` as the selected default matching mode. If additional modes are out of scope, describe the active rule as read-only text rather than implying configurability.
- Results must show keyword, total count, number of matching pages, and an affordance to expand evidence; default sort is count descending with alphabetical tie-breaking.
- Selecting a keyword opens or updates the evidence viewer with page number, concise snippet, and an emphasized match. Snippets must remain understandable without relying on highlight color.
- Provide Previous/Next match controls and a status such as `Match 3 of 18`; preserve the keyword-results list while navigating evidence.
- Zero-result keywords remain in the list with `0 matches` and explanatory empty-state copy. Provide a `Clear analysis` action that does not clear the selected document.

#### 3.6 State, feedback, and recovery matrix
| Situation | Required presentation | Recovery/action |
|---|---|---|
| Initial visit | Short task statement and author search | Focus search field |
| No author matches | Query-specific empty state | Edit query |
| Provider rate limit | Non-blocking error with retry timing when known | Retry |
| Network failure | Preserve query and prior stable content | Retry |
| No works | Selected-author context plus empty state | Change author |
| PDF unavailable | Explain that no eligible remote file exists | Upload authorized PDF |
| Invalid upload | File-specific reason and allowed type/size | Choose another file |
| Extraction failure | Persist document and failure reason safe for display | Retry or replace |
| No keyword matches | Keep parsed terms and matching rule visible | Edit keywords |
| Stale cached data | Show retrieval timestamp | Refresh metadata |

#### 3.7 Visual, responsive, and accessibility contract
- Establish reusable tokens for spacing, type, color, borders, focus rings, and state colors; target a calm, evidence-first visual hierarchy rather than a dashboard dense with decoration.
- Body text is at least 16 px with line height at least 1.5; touch targets are at least 44 by 44 CSS px.
- Meet WCAG 2.2 AA contrast and interaction requirements. All workflows must be operable by keyboard with visible focus, logical heading structure, programmatic labels, and no keyboard traps.
- Use polite live regions for search/result-count and processing updates; use an assertive alert only for blocking failures. Avoid repeated announcements for rapidly changing progress.
- At 320 CSS px width, content must not require horizontal page scrolling; data rows may reflow into labelled cards. At 200% zoom, actions and labels must remain available.
- Respect `prefers-reduced-motion`; no essential meaning may depend on animation.

### 4. Operating Model and Economics
- Optimize initial delivery around native HTML controls and a small reusable component set: search form, candidate card, works row/card, status badge, document selector, keyword chip, result row, evidence item, empty state, and alert.
- Prefer progressive disclosure over separate routes so the local application remains inexpensive to implement and easy to recover after errors.
- Instrument locally, without transmitting document content, the following UX events: search submitted, candidate selected, work selected, PDF source chosen, extraction outcome, analysis run, and evidence opened.
- Pilot targets: at least 80% unassisted happy-path completion, median time under 3 minutes using a ready PDF, zero critical keyboard blockers, and at least 90% of test participants correctly identifying the active document and matching rule.

### 5. Architecture and Integration Notes
- The frontend must render from explicit domain states rather than infer status from missing fields. API/UI contracts should include stable identifiers and status enums for author, work, document, extraction, cache freshness, and errors.
- Preserve selected IDs in URL query parameters or equivalent reload-safe local state where practical; never place uploaded content or extracted text in the URL.
- Every asynchronous request needs loading, success, empty, and error render paths. Ignore or cancel stale responses when the user changes author, work, or document mid-request.
- Treat snippets as untrusted text and render them escaped; highlight matches through safe text segmentation, not HTML injection.
- Return enough snippet context and page metadata from the API for the UI to render evidence without reimplementing PDF parsing.
- Component and end-to-end tests should use stable roles, labels, and test identifiers only where semantic selectors are insufficient.

### 6. Assumptions and Risk Register
| Assumption or risk | Type | UX impact | Mitigation / decision rule |
|---|---|---|---|
| Provider metadata is sufficient to distinguish authors | Assumption | Wrong identity selection | Show all available identity signals; test ambiguous-name fixtures |
| Most initial use is desktop research | Assumption | Mobile workflow may be secondary | Fully support 320 px reflow but optimize master-detail at 1024 px+ |
| Users understand citation counts are provider snapshots | Risk | False precision | Pair counts with provider and retrieval timestamp |
| Extraction can take long enough to feel stalled | Risk | Duplicate actions or abandonment | Persist explicit stages, disable duplicate actions, allow safe navigation |
| PDF authorization language may be misunderstood | Risk | Inappropriate fetching/upload | Label OA eligibility and require user-initiated source actions |
| Snippet highlighting alone may fail accessibility | Risk | Evidence is invisible to some users | Add semantic emphasis and textual match position/context |
| Large works or match lists may degrade responsiveness | Risk | Lost context and slow interaction | Paginate/virtualize only after measuring; retain semantic navigation |

### 7. Validation Experiments
1. Ambiguous-author test: give five representative users a common name with at least three candidates. Pass if at least four choose the fixture's intended identity without assistance and can state which metadata informed the choice.
2. Happy-path usability test: search, select, upload/fetch, extract, analyze three keywords, and open a page match. Pass if at least 80% complete without facilitator help and median completion is under 3 minutes after PDF readiness.
3. State-recovery test: inject rate-limit, network, invalid-upload, and extraction failures. Pass if 100% of participants retain their prior query/selection and at least 80% choose the intended recovery action.
4. Accessibility gate: automated WCAG scan plus keyboard-only walkthrough at 320 px and 200% zoom. Pass with zero critical/serious automated findings, zero keyboard traps, visible focus throughout, and no clipped required action.
5. Evidence-comprehension test: compare displayed counts/snippets with deterministic fixtures. Pass when all totals, page numbers, ordering, zero states, and duplicate-term handling match expected results.

### 8. 30/60/90 Day Execution Plan
- Days 1-30 (STAGE-01 to STAGE-02): define state enums and data contracts; build the responsive shell, author search/disambiguation, works list, tokens, and component accessibility baseline; validate with ambiguous-author fixtures.
- Days 31-60 (STAGE-03 to STAGE-04): add cache freshness, complete error/empty states, PDF source selection/upload, persistent extraction states, and recovery flows; run keyboard and injected-failure tests.
- Days 61-90 (STAGE-05 to STAGE-06): implement parsed keyword preview, deterministic result ordering, evidence navigation, responsive/zoom QA, and the full usability pilot; resolve all release-gate failures.

### 9. Open Questions for Next Iteration
- Should the selected author/work/document survive browser restarts, or only reloads in the current session?
- What upload-size limit and PDF retention/deletion policy should the interface state?
- Is an embedded PDF page preview required, or are extracted snippets sufficient for initial delivery?
- Which affiliation/topic fields are reliably available from the selected metadata provider?
- Should users be able to export keyword results and evidence in a later scope?
- Is OCR explicitly excluded from the initial UI, or should scanned documents expose a future-facing status/action?

## UI Acceptance Addendum by Stage
- STAGE-01: responsive shell, semantic region order, design tokens, and the explicit async-state model are documented and testable.
- STAGE-02: ambiguous candidates are never auto-selected; candidate and works metadata meet sections 3.2 and 3.3.
- STAGE-03: every provider/cache path implements the state and recovery matrix without discarding stable content.
- STAGE-04: PDF eligibility, upload constraints, document switching, processing stages, and recovery actions meet section 3.4.
- STAGE-05: parsing preview, default whole-word rule, deterministic ordering, zero results, and page evidence navigation meet section 3.5.
- STAGE-06: all five validation experiments have reproducible evidence; release is blocked by any failed accessibility gate or incorrect deterministic result.

## UI Refinement Rubric Result
- Domain fidelity: 5/5 — scholarly identity, citation provenance, OA authorization, PDF extraction, and page evidence are represented explicitly.
- Persona realism: 4/5 — researcher confidence and verification needs are covered; retention and export preferences remain open.
- Value mechanism clarity: 4/5 — task success and confidence are measurable; commercial ownership is outside this local-app scope.
- Implementation specificity: 5/5 — regions, components, states, responsive behavior, contracts, and staged delivery are defined.
- Risk and assumptions quality: 5/5 — assumptions are labelled and paired with mitigations or decision rules.
- Validation design: 5/5 — experiments include fixtures, thresholds, and release gates.
- Average: 4.67/5; no category is below 3.
