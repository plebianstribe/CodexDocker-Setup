# Codex telemetry helpers

Portable, dependency-free telemetry support for multi-agent Codex rollouts.
Run directly with `PYTHONPATH=/workspace/telemetry_helpers`; installation is
optional.

## Lifecycle hooks

Initialize one run before spawning agents:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.hooks init \
  --run-dir /absolute/artifacts/telemetry \
  --run-id RUN-001 \
  --trajectory-id trajectory_name \
  --artifact-root /absolute/artifacts \
  --created-at-utc 2026-08-03T12:00:00Z
```

Record phase starts/completions, frozen checkpoints, direct-review joins,
overrides, corrections, verification, and verdicts:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.hooks record \
  --run-dir /absolute/artifacts/telemetry \
  --event-type checkpoint_frozen \
  --phase implement \
  --status completed \
  --timestamp-utc 2026-08-03T12:10:00Z \
  --root-session-id ROOT-SESSION-ID \
  --artifact /absolute/artifacts/checkpoint.json
```

Verify the append-only hash chain:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.hooks verify \
  --run-dir /absolute/artifacts/telemetry
```

Hooks intentionally store metadata and artifact hashes, not message/tool
content. Use the exporter for the authoritative observable-event record.

## Rollout export

After the actual terminal response is present in the source record:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.exporter \
  --source /absolute/codex/rollout.jsonl \
  --output /absolute/artifacts/telemetry/export \
  --run-id RUN-001 \
  --trajectory-id trajectory_name \
  --root-session-id ROOT-SESSION-ID \
  --redaction-salt NONSECRET-RANDOM-SALT \
  --requested-role coordinator \
  --requested-model gpt-5.6-terra \
  --requested-effort medium \
  --requested-sandbox danger-full-access
```

Repeat `--source` for explicitly selected descendant records. Never discover
records by date, title, working directory, or message text. Keep the redaction
salt outside the export.

Verify the export and required sessions:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.verify \
  --export-dir /absolute/artifacts/telemetry/export \
  --require-session-id ROOT-SESSION-ID
```

Unavailable runtime fields remain `not_emitted`; they are never inferred as
zero. Source rollout files are hashed before and after export and never written.

## Multi-root bundle

Export each fresh root separately, then create one immutable phase index and
aggregate only the usage values actually emitted by each export:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.bundle \
  --output /absolute/artifacts/telemetry/bundle \
  --run-id RUN-001 \
  --trajectory-id trajectory_name \
  --phase-export implement=/absolute/artifacts/telemetry/phases/implement \
  --phase-export verify=/absolute/artifacts/telemetry/phases/verify \
  --hooks-dir /absolute/artifacts/telemetry/hooks
```

The bundle does not rewrite or concatenate phase events. It records their
manifest/event/usage hashes, verified session sets, hook-chain result, and a
sum of emitted per-phase usage; missing values stay null.
