#!/usr/bin/env python3
"""Deterministic, benchmark-scoped Codex rollout exporter.

Source records are opened read-only. Exports require explicit source files and
explicit benchmark/run/root identifiers; discovery never selects records.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.1.0-portable"
STATUSES = {"captured", "not_emitted", "redacted", "unresolved"}
SECRET_PATTERNS = [
    ("authorization", re.compile(r"(?i)(authorization\s*[:=]\s*)(?:bearer\s+)?[^\s,;\"']+")),
    ("api_key", re.compile(r"(?i)\b((?:api[_-]?key|token|secret|password)\s*[:=]\s*)[^\s,;\"']+")),
    ("credential_url", re.compile(r"(?i)\bhttps?://[^/\s:@]+:[^@\s/]+@[^\s]+")),
    ("provider_key", re.compile(r"\b(?:sk|rk|pk)-[A-Za-z0-9_-]{12,}\b")),
]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def redact_text(text: str, salt: str, redact_hashes: frozenset[str] = frozenset()) -> tuple[str, dict[str, Any]]:
    counts: dict[str, int] = defaultdict(int)
    hashes: list[str] = []
    out = text
    # Hash-targeted redaction closes the gap where a private scalar is present
    # in a command/JSON payload but has no sensitive key or `secret=` label.
    # Restrict in-text candidates to 64-hex tokens so ordinary prose is not
    # transformed merely because its complete text happens to be supplied.
    if hashlib.sha256(text.encode()).hexdigest() in redact_hashes:
        counts["sha256_value"] += 1
        return "<REDACTED:sha256_value>", {"count": 1, "classes": dict(counts), "salted_hashes": []}
    def redact_hash_match(match: re.Match[str]) -> str:
        raw = match.group(0)
        if hashlib.sha256(raw.encode()).hexdigest() not in redact_hashes:
            return raw
        counts["sha256_value"] += 1
        return "<REDACTED:sha256_value>"
    out = re.sub(r"\b[0-9A-Fa-f]{64}\b", redact_hash_match, out)
    for kind, pattern in SECRET_PATTERNS:
        def replace(match: re.Match[str]) -> str:
            raw = match.group(0)
            counts[kind] += 1
            hashes.append(hashlib.sha256((salt + raw).encode()).hexdigest())
            prefix = match.group(1) if match.lastindex else ""
            return f"{prefix}<REDACTED:{kind}>"
        out = pattern.sub(replace, out)
    return out, {"count": sum(counts.values()), "classes": dict(sorted(counts.items())), "salted_hashes": sorted(hashes)}


def redact(value: Any, salt: str, redact_hashes: frozenset[str] = frozenset()) -> tuple[Any, dict[str, Any]]:
    counts: dict[str, int] = defaultdict(int)
    hashes: list[str] = []
    sensitive = re.compile(
        r"(?i)^(authorization|api[_-]?key|token|access[_-]?token|auth[_-]?token|secret|password|credential(?:s)?|environment|env)$"
    )

    def hidden(raw: Any, kind: str) -> str:
        text = canonical(raw)
        counts[kind] += 1
        hashes.append(hashlib.sha256((salt + text).encode()).hexdigest())
        return f"<REDACTED:{kind}>"

    def walk(item: Any, parent_key: str = "") -> Any:
        if sensitive.search(parent_key) and item not in (None, "", [], {}):
            return hidden(item, "structured_secret")
        if isinstance(item, dict):
            return {key: walk(val, str(key)) for key, val in item.items()}
        if isinstance(item, list):
            return [walk(val, parent_key) for val in item]
        if isinstance(item, str):
            if parent_key in {"input", "arguments"}:
                try:
                    decoded = json.loads(item)
                except json.JSONDecodeError:
                    pass
                else:
                    if isinstance(decoded, (dict, list)):
                        return canonical(walk(decoded))
            text, meta = redact_text(item, salt, redact_hashes)
            for kind, count in meta["classes"].items():
                counts[kind] += count
            hashes.extend(meta["salted_hashes"])
            return text
        return item

    result = walk(value)
    return result, {"count": sum(counts.values()), "classes": dict(sorted(counts.items())), "salted_hashes": sorted(hashes)}


def utc(value: Any) -> str | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return None


def source_metadata(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path.resolve()),
        "sha256": sha256_bytes(path.read_bytes()),
        "size": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def coverage(value: Any, redactions: int = 0) -> str:
    if redactions:
        return "redacted"
    return "captured" if value not in (None, "", [], {}) else "not_emitted"


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the JSON-Schema subset used by the bundled S0 schemas."""
    kinds = schema.get("type")
    if kinds:
        kinds = [kinds] if isinstance(kinds, str) else kinds
        checks = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "null": lambda v: v is None,
        }
        if not any(checks[kind](value) for kind in kinds):
            raise ValueError(f"schema validation failed at {path}: expected {kinds}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"schema validation failed at {path}: value outside enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValueError(f"schema validation failed at {path}: string too short")
        if schema.get("pattern") and not re.search(schema["pattern"], value):
            raise ValueError(f"schema validation failed at {path}: pattern mismatch")
    if isinstance(value, int) and value < schema.get("minimum", value):
        raise ValueError(f"schema validation failed at {path}: below minimum")
    if isinstance(value, dict):
        missing = set(schema.get("required", [])) - set(value)
        if missing:
            raise ValueError(f"schema validation failed at {path}: missing {sorted(missing)}")
        properties = schema.get("properties", {})
        for key, child in value.items():
            child_schema = properties.get(key)
            if child_schema is None and isinstance(schema.get("additionalProperties"), dict):
                child_schema = schema["additionalProperties"]
            if child_schema:
                validate_schema(child, child_schema, f"{path}.{key}")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for index, child in enumerate(value):
            validate_schema(child, schema["items"], f"{path}[{index}]")


def flatten_text(payload: dict[str, Any]) -> str | None:
    content = payload.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts) if parts else None
    return None


def normalize(paths: list[Path], args: argparse.Namespace, salt: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[tuple[str, int, dict[str, Any]]] = []
    session_meta: dict[str, dict[str, Any]] = {}
    source_session: dict[str, str] = {}
    source_map = {str(p.resolve()): source_metadata(p) for p in paths}
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                if line.strip():
                    records.append((str(path.resolve()), line_no, json.loads(line)))
    for source, _, record in records:
        if record.get("type") == "session_meta":
            payload = record.get("payload", {})
            # Runtime child records may expose the parent-facing session_id and
            # the child's unique thread ID as id.
            sid = payload.get("id") or payload.get("session_id")
            if sid:
                session_meta[str(sid)] = payload
                source_session[source] = str(sid)
    if args.root_session_id not in session_meta:
        raise ValueError("root session ID is absent from explicitly selected source records")

    allowed = {args.root_session_id}
    changed = True
    while changed:
        changed = False
        for sid, meta in session_meta.items():
            if meta.get("parent_thread_id") in allowed and sid not in allowed:
                allowed.add(sid)
                changed = True

    turn_context: dict[str, dict[str, Any]] = {}
    output: list[dict[str, Any]] = []
    for source, line_no, record in records:
        payload = record.get("payload", {})
        emitted_run_id = record.get("benchmark_run_id") or payload.get("benchmark_run_id") or payload.get("run_id")
        if emitted_run_id not in (None, args.run_id):
            continue
        sid = payload.get("session_id") or source_session.get(source)
        if sid not in allowed:
            continue
        if record.get("type") == "turn_context":
            turn_context[sid] = payload
        meta = session_meta.get(sid, {})
        ctx = turn_context.get(sid, {})
        is_root = sid == args.root_session_id
        safe_payload, redaction = redact(payload, salt, frozenset(getattr(args, "redact_value_sha256", [])))
        event = {
            "benchmark_run_id": args.run_id,
            "trajectory_id": args.trajectory_id,
            "event_id": "",
            "sequence": 0,
            "source": {"path": source, "line": line_no, "sha256": source_map[source]["sha256"]},
            "topology": {
                "root_session_id": args.root_session_id,
                "session_id": sid,
                "parent_session_id": meta.get("parent_thread_id"),
                "agent_role": meta.get("agent_role"),
                "task_name": meta.get("agent_nickname") or meta.get("agent_path"),
            },
            "flow": {
                "stage": args.stage, "step": args.step, "group": args.group,
                "component": args.component, "branch": (meta.get("git") or {}).get("branch"),
                "worktree": meta.get("cwd"), "phase": args.phase,
                "parent_call_id": payload.get("call_id"),
            },
            "time": {"source": record.get("timestamp"), "utc": utc(record.get("timestamp"))},
            "event_type": record.get("type"),
            "payload_type": payload.get("type"),
            "communication": {
                "sender": payload.get("author") or payload.get("role"),
                "recipients": payload.get("recipient"),
                "message_type": payload.get("type"),
                "text": flatten_text(safe_payload) if isinstance(safe_payload, dict) else None,
            },
            "tool": {
                "name": payload.get("name"), "call_id": payload.get("call_id") or payload.get("id"),
                "arguments": (safe_payload.get("input") or safe_payload.get("arguments")) if isinstance(safe_payload, dict) else None,
                "result": safe_payload.get("output") if isinstance(safe_payload, dict) else None,
                "status": payload.get("status"),
            },
            "command": {"command": None, "cwd": None, "exit_status": None, "stdout_stderr": None},
            "runtime": {
                "requested_role": args.requested_role if is_root else None, "resolved_role": meta.get("agent_role"),
                "requested_model": args.requested_model if is_root else None, "resolved_model": ctx.get("model"),
                "requested_effort": args.requested_effort if is_root else None, "resolved_effort": ctx.get("effort"),
                "requested_sandbox": args.requested_sandbox if is_root else None, "resolved_sandbox": ctx.get("sandbox_policy"),
                "concurrency_slot": None, "service_tier": None,
            },
            "usage": {"input": None, "cached_input": None, "output": None, "reasoning": None, "total": None},
            "redaction": redaction,
            "coverage": {},
            "raw": safe_payload,
        }
        if payload.get("type") == "token_count":
            info = payload.get("info") or {}
            usage = info.get("last_token_usage") or info.get("total_token_usage") or info
            event["usage"] = {
                "input": usage.get("input_tokens"), "cached_input": usage.get("cached_input_tokens"),
                "output": usage.get("output_tokens"), "reasoning": usage.get("reasoning_output_tokens"),
                "total": usage.get("total_tokens"),
            }
        if payload.get("name") in {"functions.exec_command", "exec_command"} and isinstance(safe_payload, dict):
            try:
                inp = json.loads(safe_payload.get("input") or safe_payload.get("arguments") or "{}")
            except (TypeError, json.JSONDecodeError):
                inp = {}
            event["command"]["command"] = inp.get("cmd")
            event["command"]["cwd"] = inp.get("workdir")
        if payload.get("type") in {"custom_tool_call_output", "function_call_output"} and isinstance(safe_payload, dict):
            value = safe_payload.get("output")
            if isinstance(value, str):
                match = re.search(r"(?:exit_code|Process exited with code)\D+(-?\d+)", value)
                event["command"]["exit_status"] = int(match.group(1)) if match else None
                event["command"]["stdout_stderr"] = value
        output.append(event)
    output.sort(key=lambda e: (e["time"]["utc"] or "", e["source"]["path"], e["source"]["line"]))
    for seq, event in enumerate(output, 1):
        event["sequence"] = seq
        stable = dict(event)
        stable["event_id"] = ""
        event["event_id"] = sha256_bytes(canonical(stable).encode())[:24]
        fields = {
            "timestamp": event["time"]["utc"], "session_id": event["topology"]["session_id"],
            "parent_id": event["topology"]["parent_session_id"], "message_text": event["communication"]["text"],
            "tool_call_id": event["tool"]["call_id"], "resolved_model": event["runtime"]["resolved_model"],
            "resolved_effort": event["runtime"]["resolved_effort"],
            "resolved_sandbox": event["runtime"]["resolved_sandbox"],
            **{f"usage_{k}": v for k, v in event["usage"].items()},
        }
        for group in ("topology", "flow", "time", "communication", "tool", "command", "runtime", "usage"):
            for key, value in event[group].items():
                fields.setdefault(f"{group}.{key}", value)
        event["coverage"] = {key: coverage(value, event["redaction"]["count"] if key == "message_text" else 0) for key, value in fields.items()}
    attestations = []
    for sid in sorted(allowed):
        meta, ctx = session_meta.get(sid, {}), turn_context.get(sid, {})
        resolved_sandbox = ctx.get("sandbox_policy")
        sandbox_name = resolved_sandbox.get("type") if isinstance(resolved_sandbox, dict) else resolved_sandbox
        checks = {
            "role": (args.requested_role if sid == args.root_session_id else None, meta.get("agent_role")),
            "model": (args.requested_model if sid == args.root_session_id else None, ctx.get("model")),
            "effort": (args.requested_effort if sid == args.root_session_id else None, ctx.get("effort")),
            "sandbox": (args.requested_sandbox if sid == args.root_session_id else None, sandbox_name),
        }
        result = {}
        for key, (requested, resolved) in checks.items():
            status = "not_emitted" if resolved is None else ("match" if requested is None or requested == resolved else "mismatch")
            result[key] = {"requested": requested, "resolved": resolved, "status": status}
            if status == "mismatch":
                raise ValueError(f"policy attestation mismatch for session {sid}: {key}")
        attestations.append({"session_id": sid, "checks": result})
    return output, {"sources": list(source_map.values()), "selected_sessions": sorted(allowed), "policy_attestations": attestations}


def write_exports(events: list[dict[str, Any]], meta: dict[str, Any], args: argparse.Namespace) -> None:
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    schema_dir = Path(__file__).resolve().parent / "schema"
    event_schema = json.loads((schema_dir / "event.schema.json").read_text())
    for event in events:
        validate_schema(event, event_schema)
    jsonl = "".join(canonical(event) + "\n" for event in events)
    (out / "events.jsonl").write_text(jsonl, encoding="utf-8")
    with (out / "calls.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sequence", "session_id", "tool", "call_id", "status"])
        writer.writeheader()
        for event in events:
            if event["tool"]["call_id"]:
                writer.writerow({"sequence": event["sequence"], "session_id": event["topology"]["session_id"],
                                 "tool": event["tool"]["name"], "call_id": event["tool"]["call_id"],
                                 "status": event["tool"]["status"]})
    totals = defaultdict(int)
    emitted = defaultdict(bool)
    by_agent: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_phase: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for event in events:
        for key, value in event["usage"].items():
            if isinstance(value, int):
                totals[key] += value
                emitted[key] = True
                by_agent[event["topology"]["session_id"]][key] += value
                by_phase[event["flow"]["phase"] or "not_emitted"][key] += value
    usage = {key: totals[key] if emitted[key] else None for key in ("input", "cached_input", "output", "reasoning", "total")}
    (out / "usage.json").write_text(canonical({
        "aggregate": usage,
        "per_agent": {key: dict(value) for key, value in sorted(by_agent.items())},
        "per_phase": {key: dict(value) for key, value in sorted(by_phase.items())},
        "per_trajectory": {args.trajectory_id: usage},
    }) + "\n", encoding="utf-8")
    transcript = [f"# Transcript: {args.run_id}", ""]
    for event in events:
        text = event["communication"]["text"]
        if text:
            transcript.extend([f"## {event['sequence']} · {event['time']['utc']} · {event['topology']['session_id']}", "", text, ""])
    (out / "transcript.md").write_text("\n".join(transcript), encoding="utf-8")
    manifest = {
        "exporter_version": VERSION, "benchmark_run_id": args.run_id,
        "trajectory_id": args.trajectory_id, "root_session_id": args.root_session_id,
        "selection_predicate": "explicit source paths AND root session plus descendants present in selected records",
        "source_records": meta["sources"], "selected_sessions": meta["selected_sessions"],
        "policy_attestations": meta["policy_attestations"],
        "event_count": len(events), "exported_at_utc": args.export_time,
    }
    validate_schema(manifest, json.loads((schema_dir / "trajectory.schema.json").read_text()))
    (out / "manifest.json").write_text(canonical(manifest) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--source", action="append", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--root-session-id", required=True)
    p.add_argument("--trajectory-id", default="setup_fixture")
    p.add_argument("--stage", default="S0")
    p.add_argument("--step", default="MAE-SETUP-01")
    p.add_argument("--group", default="G0A")
    p.add_argument("--component", default="telemetry")
    p.add_argument("--phase", default="setup")
    p.add_argument("--requested-role")
    p.add_argument("--requested-model")
    p.add_argument("--requested-effort")
    p.add_argument("--requested-sandbox")
    p.add_argument("--redaction-salt", required=True)
    p.add_argument("--redact-value-sha256", action="append", default=[], metavar="SHA256",
                   help="Repeatable SHA-256 proof for scalar/text values to redact without storing their raw value.")
    p.add_argument("--export-time", default="1970-01-01T00:00:00Z",
                   help="Stable timestamp for reproducible exports; caller records real audit time separately.")
    return p


def main() -> int:
    args = parser().parse_args()
    if any(not re.fullmatch(r"[0-9a-fA-F]{64}", value) for value in args.redact_value_sha256):
        print("export failed: --redact-value-sha256 must be a SHA-256 hex digest", file=sys.stderr)
        return 2
    paths = [Path(value).resolve() for value in args.source]
    output = Path(args.output).resolve()
    generated = {output / name for name in ("events.jsonl", "calls.csv", "usage.json", "transcript.md", "manifest.json")}
    if any(path == output or path in generated for path in paths):
        print("export failed: output would overwrite a source record", file=sys.stderr)
        return 2
    before = {str(path): sha256_bytes(path.read_bytes()) for path in paths}
    try:
        events, meta = normalize(paths, args, args.redaction_salt)
        write_exports(events, meta, args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"export failed: {exc}", file=sys.stderr)
        return 2
    after = {str(path): sha256_bytes(path.read_bytes()) for path in paths}
    if before != after:
        print("source mutation detected", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
