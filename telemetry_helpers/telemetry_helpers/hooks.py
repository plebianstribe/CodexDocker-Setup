#!/usr/bin/env python3
"""Append-only, hash-chained lifecycle hooks for multi-agent trajectories."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "telemetry-hooks/v1"
EVENT_TYPES = {
    "run_started", "phase_started", "checkpoint_frozen", "direct_review_joined",
    "override_triggered", "correction_applied", "phase_completed",
    "verification_completed", "verdict_issued", "appellate_verdict", "run_completed",
}
STATUSES = {"started", "completed", "pass", "fail", "blocked", "skipped", "not_emitted"}
UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def required_absolute_file(value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute() or not path.is_file():
        raise ValueError(f"{label} must be an existing absolute file: {path}")
    return path.resolve()


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "hook_manifest.json"


def log_path(run_dir: Path) -> Path:
    return run_dir / "hooks.jsonl"


def load_manifest(run_dir: Path) -> dict[str, Any]:
    try:
        value = json.loads(manifest_path(run_dir).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid hook manifest: {exc}") from exc
    if value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported hook manifest schema")
    return value


def load_events(run_dir: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        lines = log_path(run_dir).read_text().splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read hook log: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid hook JSON at line {line_number}: {exc}") from exc
    return events


def verify_chain(run_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(run_dir)
    events = load_events(run_dir)
    previous = None
    sessions: set[str] = set()
    for index, event in enumerate(events, 1):
        if event.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"event {index} has unsupported schema")
        if event.get("run_id") != manifest["run_id"] or event.get("trajectory_id") != manifest["trajectory_id"]:
            raise ValueError(f"event {index} identity mismatch")
        if event.get("sequence") != index:
            raise ValueError(f"event {index} sequence mismatch")
        if event.get("previous_event_hash") != previous:
            raise ValueError(f"event {index} hash-chain predecessor mismatch")
        claimed = event.get("event_hash")
        stable = dict(event)
        stable["event_hash"] = ""
        calculated = digest_bytes(canonical(stable).encode())
        if claimed != calculated:
            raise ValueError(f"event {index} hash mismatch")
        previous = claimed
        if event.get("root_session_id") != "not_emitted":
            sessions.add(event["root_session_id"])
        for path, expected in event.get("artifact_hashes", {}).items():
            artifact = Path(path)
            if not artifact.is_file() or digest_file(artifact) != expected:
                raise ValueError(f"event {index} artifact hash mismatch: {path}")
    return {
        "valid": True,
        "run_id": manifest["run_id"],
        "trajectory_id": manifest["trajectory_id"],
        "event_count": len(events),
        "root_session_ids": sorted(sessions),
        "terminal_event_hash": previous,
    }


def init_run(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        raise ValueError("run_dir must be absolute")
    artifact_root = Path(args.artifact_root)
    if not artifact_root.is_absolute():
        raise ValueError("artifact_root must be absolute")
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = manifest_path(run_dir)
    log = log_path(run_dir)
    if manifest.exists() or log.exists():
        raise ValueError("refusing to overwrite an existing hook manifest or log")
    if not UTC_PATTERN.fullmatch(args.created_at_utc):
        raise ValueError("created_at_utc must be an explicit UTC timestamp ending in Z")
    sources = [required_absolute_file(value, "source") for value in args.source]
    value = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "trajectory_id": args.trajectory_id,
        "artifact_root": str(artifact_root.resolve()),
        "created_at_utc": args.created_at_utc,
        "source_records_at_init": {str(path): digest_file(path) for path in sources},
        "content_policy": "metadata_and_artifact_hashes_only",
    }
    with manifest.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    log.open("x", encoding="utf-8").close()
    print(canonical({"run_dir": str(run_dir), "status": "initialized"}))
    return 0


def record(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        raise ValueError("run_dir must be absolute")
    manifest = load_manifest(run_dir)
    if args.event_type not in EVENT_TYPES or args.status not in STATUSES:
        raise ValueError("unsupported event_type or status")
    if not UTC_PATTERN.fullmatch(args.timestamp_utc):
        raise ValueError("timestamp_utc must be an explicit UTC timestamp ending in Z")
    artifacts = [required_absolute_file(value, "artifact") for value in args.artifact]
    lock_path = run_dir / ".telemetry-hooks.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        events = load_events(run_dir)
        previous = events[-1]["event_hash"] if events else None
        event = {
            "schema_version": SCHEMA_VERSION,
            "run_id": manifest["run_id"],
            "trajectory_id": manifest["trajectory_id"],
            "sequence": len(events) + 1,
            "timestamp_utc": args.timestamp_utc,
            "event_type": args.event_type,
            "phase": args.phase,
            "status": args.status,
            "root_session_id": args.root_session_id,
            "agent_session_id": args.agent_session_id,
            "role": args.role,
            "runtime": {
                "requested_model": args.requested_model,
                "resolved_model": args.resolved_model,
                "requested_effort": args.requested_effort,
                "resolved_effort": args.resolved_effort,
                "requested_sandbox": args.requested_sandbox,
                "resolved_sandbox": args.resolved_sandbox,
            },
            "artifact_hashes": {str(path): digest_file(path) for path in artifacts},
            "previous_event_hash": previous,
            "event_hash": "",
        }
        event["event_hash"] = digest_bytes(canonical(event).encode())
        with log_path(run_dir).open("a", encoding="utf-8") as handle:
            handle.write(canonical(event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    print(canonical({"event_hash": event["event_hash"], "sequence": event["sequence"]}))
    return 0


def verify(args: argparse.Namespace) -> int:
    result = verify_chain(Path(args.run_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--run-dir", required=True)
    init.add_argument("--run-id", required=True)
    init.add_argument("--trajectory-id", required=True)
    init.add_argument("--artifact-root", required=True)
    init.add_argument("--created-at-utc", required=True)
    init.add_argument("--source", action="append", default=[])
    init.set_defaults(handler=init_run)
    item = commands.add_parser("record")
    item.add_argument("--run-dir", required=True)
    item.add_argument("--event-type", required=True, choices=sorted(EVENT_TYPES))
    item.add_argument("--phase", required=True)
    item.add_argument("--status", required=True, choices=sorted(STATUSES))
    item.add_argument("--timestamp-utc", required=True)
    item.add_argument("--root-session-id", default="not_emitted")
    item.add_argument("--agent-session-id", default="not_emitted")
    item.add_argument("--role", default="not_emitted")
    item.add_argument("--requested-model", default="not_emitted")
    item.add_argument("--resolved-model", default="not_emitted")
    item.add_argument("--requested-effort", default="not_emitted")
    item.add_argument("--resolved-effort", default="not_emitted")
    item.add_argument("--requested-sandbox", default="not_emitted")
    item.add_argument("--resolved-sandbox", default="not_emitted")
    item.add_argument("--artifact", action="append", default=[])
    item.set_defaults(handler=record)
    check = commands.add_parser("verify")
    check.add_argument("--run-dir", required=True)
    check.set_defaults(handler=verify)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"telemetry hook failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
