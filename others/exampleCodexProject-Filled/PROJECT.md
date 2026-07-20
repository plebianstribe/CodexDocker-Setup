# Author Citation and PDF Keyword Explorer

Build a local web application that searches for scholarly works by author name,
displays basic citation information, and lets a user inspect keyword frequency
inside PDFs they are authorized to access.

## User Workflow

1. Enter an author's name.
2. Retrieve and normalize matching works from a scholarly metadata API.
3. Review the title, authors, year, venue, DOI or source URL, and citation count
   for each result.
4. Attach or download an openly available PDF for a selected work.
5. Click through the available PDFs in the web interface.
6. Enter one or more keywords and see their occurrence counts for the selected
   PDF, sorted from most to least frequent.
7. Click a keyword result to see page-level matches and short text snippets.

## Initial Scope

- Support search by one author name at a time.
- Use one public scholarly metadata source initially, such as OpenAlex or
  Semantic Scholar, behind a replaceable adapter.
- Clearly distinguish API-provided citation counts from locally extracted PDF
  text.
- Accept local PDF uploads. Only fetch a remote PDF when the source explicitly
  identifies it as open access.
- Perform case-insensitive whole-word keyword matching by default.
- Store fetched metadata and extracted text in a local cache to avoid repeated
  API calls and PDF processing.
- Provide useful states for no matches, ambiguous authors, unavailable PDFs,
  unreadable/scanned PDFs, rate limits, and network failures.

## Suggested Architecture

- A small Python backend for scholarly API calls, metadata normalization, PDF
  text extraction, keyword counting, and caching.
- A lightweight web interface that lists works and provides a PDF viewer with a
  keyword-frequency side panel.
- A source adapter interface so another scholarly API can be added without
  changing the UI or normalized work model.
- Separate citation retrieval from PDF acquisition; a metadata result does not
  guarantee that its PDF may be downloaded.

Choose the specific framework and PDF libraries during implementation. Record
the choice and local run commands in the project README that you create.

## Core Data to Preserve

For every normalized work, retain:

- stable source identifier;
- title and ordered author list;
- publication year and venue;
- DOI and canonical source URL when available;
- citation count, citation source, and retrieval timestamp;
- PDF origin and open-access status when known;
- extracted-text status and any processing error.

## Acceptance Criteria

- An author search renders normalized scholarly results without page reload
  errors.
- Similar or ambiguous author matches are shown rather than silently combined.
- A user can select each available PDF and move between documents.
- Keyword counts are reproducible and include per-page locations.
- Empty keywords, punctuation, capitalization, and repeated keywords are
  handled consistently.
- Failed API calls and non-text PDFs produce actionable messages.
- Cached results reduce duplicate API and extraction work.
- Unit tests cover metadata normalization and keyword-frequency logic.
- Setup, configuration, attribution, and local run instructions are documented.

## Boundaries

- Do not bypass paywalls or download PDFs without permission.
- Do not present citation counts from different providers as directly
  equivalent without identifying their source.
- Do not infer author identity solely from a matching display name; expose
  available identifiers and affiliations so the user can choose.
- Keep API keys outside source control and avoid logging secrets.

## Optional Follow-ups

- Add ORCID-based author selection.
- Compare keyword frequencies across several papers by the same author.
- Export citations as BibTeX or CSL JSON.
- Add OCR as an explicit opt-in path for scanned PDFs.
