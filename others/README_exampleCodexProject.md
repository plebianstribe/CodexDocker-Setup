# Example Codex Project

This example gives Codex a small, concrete application to build: a local web
interface that finds papers by author, lets you browse their PDFs, and reports
frequently occurring keywords from each document.

## Copy the Starter Project

The main README creates an empty sibling folder named
`exampleCodexProject`. From the Docker setup repository root, copy the starter
brief into that folder:

```bash
export codexProjDir="exampleCodexProject"
cp -a "others/exampleCodexProject/." "../$codexProjDir/"
```

The existing Docker command mounts that folder at `/app`. Start the container,
then ask Codex to read `/app/PROJECT.md` and implement the project in `/app`.

## Suggested First Prompt

```text
Read /app/PROJECT.md, propose a small implementation plan, and build the first
working version. Keep external scholarly APIs behind adapters, document any API
keys or rate limits, and add tests for citation normalization and PDF keyword
counting.
```

The full starter specification is in
[`exampleCodexProject/PROJECT.md`](exampleCodexProject/PROJECT.md).
