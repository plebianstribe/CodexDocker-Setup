#!/usr/bin/env python3
"""Verify a portable telemetry export without modifying it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from .exporter import STATUSES, canonical, validate_schema

REQUIRED = {"events.jsonl", "calls.csv", "usage.json", "transcript.md", "manifest.json"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_export(export_dir: Path, required_sessions: list[str]) -> dict[str, Any]:
    if not export_dir.is_absolute() or not export_dir.is_dir():
        raise ValueError("export_dir must be an existing absolute directory")
    missing = sorted(name for name in REQUIRED if not (export_dir / name).is_file())
    if missing:
        raise ValueError(f"missing export files: {missing}")
    schema_dir = Path(__file__).resolve().parent / "schema"
    event_schema = json.loads((schema_dir / "event.schema.json").read_text())
    trajectory_schema = json.loads((schema_dir / "trajectory.schema.json").read_text())
    manifest = json.loads((export_dir / "manifest.json").read_text())
    validate_schema(manifest, trajectory_schema)
    events = [json.loads(line) for line in (export_dir / "events.jsonl").read_text().splitlines() if line.strip()]
    sessions: set[str] = set()
    for index, event in enumerate(events, 1):
        validate_schema(event, event_schema)
        if event["sequence"] != index:
            raise ValueError(f"event sequence mismatch at {index}")
        stable = dict(event)
        stable["event_id"] = ""
        stable["coverage"] = {}
        expected = hashlib.sha256(canonical(stable).encode()).hexdigest()[:24]
        if event["event_id"] != expected:
            raise ValueError(f"event hash mismatch at {index}")
        if not set(event["coverage"].values()) <= STATUSES:
            raise ValueError(f"invalid coverage status at {index}")
        sessions.add(event["topology"]["session_id"])
    if manifest["event_count"] != len(events):
        raise ValueError("manifest event_count mismatch")
    if set(manifest["selected_sessions"]) != sessions:
        raise ValueError("manifest selected_sessions mismatch")
    absent = sorted(set(required_sessions) - sessions)
    if absent:
        raise ValueError(f"required sessions absent: {absent}")
    for source in manifest["source_records"]:
        path = Path(source["path"])
        if not path.is_file() or digest(path) != source["sha256"]:
            raise ValueError(f"source record changed or absent: {path}")
    return {
        "valid": True,
        "benchmark_run_id": manifest["benchmark_run_id"],
        "trajectory_id": manifest["trajectory_id"],
        "event_count": len(events),
        "selected_sessions": sorted(sessions),
        "manifest_sha256": digest(export_dir / "manifest.json"),
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--export-dir", required=True)
    root.add_argument("--require-session-id", action="append", default=[])
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        result = verify_export(Path(args.export_dir), args.require_session_id)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"telemetry verification failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
