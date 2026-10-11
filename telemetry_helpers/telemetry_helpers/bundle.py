#!/usr/bin/env python3
"""Bundle independently verified phase exports without rewriting their events."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from .hooks import verify_chain
from .verify import verify_export


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_phase(value: str) -> tuple[str, Path]:
    phase, separator, raw_path = value.partition("=")
    path = Path(raw_path)
    if not separator or not phase or not path.is_absolute() or not path.is_dir():
        raise ValueError("--phase-export must be PHASE=/absolute/existing/export")
    return phase, path.resolve()


def bundle(args: argparse.Namespace) -> dict[str, Any]:
    output = Path(args.output)
    if not output.is_absolute():
        raise ValueError("output must be absolute")
    phases = [parse_phase(value) for value in args.phase_export]
    names = [name for name, _ in phases]
    if len(names) != len(set(names)):
        raise ValueError("phase names must be unique")
    if output.exists() and any(output.iterdir()):
        raise ValueError("refusing to overwrite nonempty bundle output")
    if any(output.resolve() == path or output.resolve() in path.parents for _, path in phases):
        raise ValueError("bundle output must not equal or contain a phase export")
    entries = []
    totals: dict[str, int] = defaultdict(int)
    emitted: dict[str, bool] = defaultdict(bool)
    sessions: set[str] = set()
    for phase, path in phases:
        checked = verify_export(path, [])
        manifest = json.loads((path / "manifest.json").read_text())
        if manifest["benchmark_run_id"] != args.run_id or manifest["trajectory_id"] != args.trajectory_id:
            raise ValueError(f"phase {phase} run or trajectory identity mismatch")
        phase_sessions = set(checked["selected_sessions"])
        overlap = sorted(sessions & phase_sessions)
        if overlap:
            raise ValueError(f"phase {phase} reuses sessions already bundled: {overlap}")
        usage = json.loads((path / "usage.json").read_text())["aggregate"]
        for key, value in usage.items():
            if isinstance(value, int):
                totals[key] += value
                emitted[key] = True
        sessions.update(phase_sessions)
        entries.append({
            "phase": phase,
            "export_dir": str(path),
            "manifest_sha256": digest(path / "manifest.json"),
            "events_sha256": digest(path / "events.jsonl"),
            "usage_sha256": digest(path / "usage.json"),
            "event_count": checked["event_count"],
            "selected_sessions": checked["selected_sessions"],
        })
    hook_result = None
    if args.hooks_dir:
        hook_result = verify_chain(Path(args.hooks_dir))
        if hook_result["run_id"] != args.run_id or hook_result["trajectory_id"] != args.trajectory_id:
            raise ValueError("hook run or trajectory identity mismatch")
    aggregate = {key: totals[key] if emitted[key] else None for key in ("input", "cached_input", "output", "reasoning", "total")}
    manifest = {
        "schema_version": "telemetry-bundle/v1",
        "run_id": args.run_id,
        "trajectory_id": args.trajectory_id,
        "phase_exports": entries,
        "selected_sessions": sorted(sessions),
        "aggregate_usage": aggregate,
        "hook_verification": hook_result,
        "aggregation_policy": "sum emitted per-phase aggregates; preserve missing as null; phase events remain immutable",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "bundle_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (output / "usage.json").write_text(json.dumps({"aggregate": aggregate}, indent=2, sort_keys=True) + "\n")
    hashes = {name: digest(output / name) for name in ("bundle_manifest.json", "usage.json")}
    (output / "hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    return manifest


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--output", required=True)
    root.add_argument("--run-id", required=True)
    root.add_argument("--trajectory-id", required=True)
    root.add_argument("--phase-export", action="append", required=True)
    root.add_argument("--hooks-dir")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        value = bundle(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"telemetry bundle failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": args.output, "phase_count": len(value["phase_exports"]), "valid": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
