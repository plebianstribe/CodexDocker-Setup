#!/usr/bin/env python3
"""Create and validate a deterministic TrajB-Lite rollout packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = "trajb-lite/v1"
AGENT_DIR = Path("/workspace/.codex/agents")
TELEMETRY_ROOT = Path("/workspace/telemetry_helpers")
TELEMETRY_FILES = [
    TELEMETRY_ROOT / "README.md",
    TELEMETRY_ROOT / "pyproject.toml",
    TELEMETRY_ROOT / "telemetry_helpers" / "exporter.py",
    TELEMETRY_ROOT / "telemetry_helpers" / "bundle.py",
    TELEMETRY_ROOT / "telemetry_helpers" / "hooks.py",
    TELEMETRY_ROOT / "telemetry_helpers" / "verify.py",
    TELEMETRY_ROOT / "telemetry_helpers" / "schema" / "event.schema.json",
    TELEMETRY_ROOT / "telemetry_helpers" / "schema" / "trajectory.schema.json",
]
SKILL_ROOT = Path("/workspace/.codex/skills/multiagent-trajb-lite")
SKILL_FILES = [
    SKILL_ROOT / "SKILL.md",
    SKILL_ROOT / "scripts" / "scaffold_trajb_lite.py",
    SKILL_ROOT / "references" / "policy-contract.md",
    SKILL_ROOT / "references" / "run-spec.schema.json",
]
ROLE_FILES = {
    "implementation_worker_comms": AGENT_DIR / "trajb-lite-implementation-worker.toml",
    "override_specialist": AGENT_DIR / "trajb-lite-override-specialist.toml",
    "verification_worker": AGENT_DIR / "verification-worker.toml",
    "final_judge": AGENT_DIR / "trajb-lite-final-judge.toml",
    "appellate_judge": AGENT_DIR / "trajb-lite-appellate-judge.toml",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], text=True, capture_output=True
    )
    if result.returncode:
        raise ValueError(f"git {' '.join(args)} failed in {root}: {result.stderr.strip()}")
    return result.stdout.strip()


def absolute_existing(value: str, label: str, *, directory: bool = False) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise ValueError(f"{label} must be absolute: {path}")
    if not path.exists():
        raise ValueError(f"{label} does not exist: {path}")
    if directory and not path.is_dir():
        raise ValueError(f"{label} must be a directory: {path}")
    if not directory and not path.is_file():
        raise ValueError(f"{label} must be a file: {path}")
    return path.resolve()


def role_policy() -> dict:
    return {
        "ultra_allowed": False,
        "coordinator": {"model": "gpt-5.6-terra", "effort": "medium", "sandbox": "danger-full-access", "fresh_root_per_phase": True},
        "implementation_worker_comms": {"model": "gpt-5.6-terra", "effort": "medium", "sandbox": "danger-full-access", "direct_sibling_review": True},
        "override_specialist": {"model": "gpt-5.6-sol", "effort": "xhigh", "sandbox": "danger-full-access", "bounded": True, "may_judge_own_work": False},
        "verification_worker": {"model": "gpt-5.6-terra", "effort": "high", "sandbox": "workspace-write", "independent": True},
        "final_judge": {"model": "gpt-5.6-sol", "effort": "high", "sandbox": "danger-full-access", "independent": True},
        "appellate_judge": {
            "model": "gpt-5.6-sol", "effort": "xhigh", "sandbox": "danger-full-access", "independent": True,
            "only_if": ["override_used", "verifier_judge_disagreement", "conditional_verdict"],
        },
        "guards": {
            "coordinator_turns_per_phase": 24,
            "coordinator_input_tokens_per_turn": 100000,
            "coordinator_input_tokens_per_phase": 2000000,
            "wait_calls_total": 8,
            "consecutive_no_progress_waits": 2,
        },
        "override_triggers": [
            "cross_component_ambiguity",
            "post_correction_deterministic_failure",
            "novel_architecture_not_resolved_by_frozen_contract",
        ],
        "telemetry": {
            "helper_root": str(TELEMETRY_ROOT),
            "hooks_required": True,
            "explicit_source_export_required": True,
            "missing_runtime_value": "not_emitted",
        },
    }


def toml_overrides() -> list[str]:
    values = ["agents.max_concurrent_threads_per_session=3"]
    descriptions = {
        "implementation_worker_comms": "TrajB-Lite component owner and direct sibling reviewer.",
        "override_specialist": "Bounded Sol/xhigh implementation override specialist; never a judge of its own work.",
        "verification_worker": "Independent Terra/high verifier for TrajB-Lite.",
        "final_judge": "Independent Sol/high final judge for TrajB-Lite.",
        "appellate_judge": "Conditional independent Sol/xhigh appellate judge for TrajB-Lite.",
    }
    for role, path in ROLE_FILES.items():
        values.append(f'agents.{role}.description={json.dumps(descriptions[role])}')
        values.append(f'agents.{role}.config_file={json.dumps(str(path))}')
    return values


def codex_command(project_root: Path, prompt: str) -> str:
    args = [
        "codex", "exec", "-C", str(project_root), "--strict-config",
        "--dangerously-bypass-approvals-and-sandbox", "-m", "gpt-5.6-terra",
        "-c", 'model_reasoning_effort="medium"',
    ]
    for override in toml_overrides():
        args.extend(["-c", override])
    args.append(prompt)
    separator = " " + "\\" + "\n  "
    return separator.join(shlex.quote(item) for item in args)


def build_launch(spec: dict) -> str:
    instruction_text = ", ".join(spec.get("instruction_files", [])) or "the project instruction files"
    common = (
        f"Run {spec['goal_id']} for {spec['run_id']} using {spec['goal_file']}, "
        f"{spec['tracker_file']}, {spec['task_spec']}, and packet {spec['output_dir']}. "
        f"Read and obey {instruction_text}. "
        f"Write run artifacts only under {spec['artifact_dir']}. Use $multiagent-trajb-lite. "
        f"Invoke telemetry hooks and exporters from {TELEMETRY_ROOT}. "
        "Attest resolved roles and obey packet guards."
    )
    prompts = [
        common + " Execute only phase implement. Owners communicate directly; root relay is prohibited. Freeze a hash-bound join checkpoint, then stop.",
        common + " Start a fresh root and execute only phase verify_and_judge from the frozen join checkpoint. Run independent verification and the Sol/high final judge, then stop.",
        common + " Start a fresh root and execute phase appellate only if its recorded trigger is true; otherwise record skipped. Never let an override actor judge its own work, then stop.",
    ]
    lines = [
        "# Generated TrajB-Lite launch commands", "",
        "Run these commands sequentially. Never use `codex exec resume` between phases.", "",
    ]
    for index, (phase, prompt) in enumerate(zip(("implement", "verify_and_judge", "appellate_if_triggered"), prompts), 1):
        if phase == "appellate_if_triggered":
            lines.extend([
                "The deterministic phase-2 disposition must prove an appellate trigger before this command is run. If no trigger exists, do not launch a third root; record the phase as skipped during finalization.",
                "",
            ])
        lines.extend([f"## {index}. {phase}", "", "```bash", codex_command(Path(spec["project_root"]), prompt), "```", ""])
    lines.extend([
        "## 4. finalize", "",
        "Use the repository's deterministic telemetry exporter with the explicit root session IDs from all executed phases. Do not keep an LLM coordinator alive to poll, aggregate, hash, or seal records.", "",
    ])
    return "\n".join(lines)


def validate_packet(packet_dir: Path) -> list[str]:
    errors: list[str] = []
    required = ["run_spec.json", "policy.json", "input_hashes.json", "launch_commands.md"]
    for name in required:
        if not (packet_dir / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        return errors
    try:
        spec = json.loads((packet_dir / "run_spec.json").read_text())
        policy = json.loads((packet_dir / "policy.json").read_text())
        hashes = json.loads((packet_dir / "input_hashes.json").read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return [f"invalid JSON: {exc}"]
    if spec.get("schema_version") != SCHEMA_VERSION:
        errors.append("unexpected schema_version")
    if spec.get("status") != "ready_to_launch":
        errors.append("packet status must be ready_to_launch")
    artifact = Path(str(spec.get("artifact_dir", "")))
    project = Path(str(spec.get("project_root", "")))
    if not artifact.is_absolute() or artifact == Path(str(spec.get("output_dir", ""))):
        errors.append("artifact_dir must be absolute and distinct from packet output_dir")
    elif artifact == project or artifact in project.parents:
        errors.append("artifact_dir must not equal or contain project_root")
    try:
        if git_output(project, "rev-parse", "HEAD") != spec.get("execution_start_commit"):
            errors.append("execution worktree HEAD does not match execution_start_commit")
        if git_output(project, "status", "--porcelain", "--untracked-files=all"):
            errors.append("execution worktree is not clean")
        submodules = git_output(project, "submodule", "status", "--recursive")
        if any(line.startswith(("-", "+", "U")) for line in submodules.splitlines()):
            errors.append("execution worktree submodules are not at recorded pins")
    except ValueError as exc:
        errors.append(str(exc))
    phases = spec.get("phases", [])
    if [p.get("id") for p in phases] != ["implement", "verify_and_judge", "appellate_if_triggered", "finalize"]:
        errors.append("phase sequence is not canonical")
    if not all(p.get("fresh_root") is True for p in phases[:3]):
        errors.append("all LLM phases must use fresh roots")
    if policy.get("ultra_allowed") is not False:
        errors.append("Ultra must be prohibited")
    roles = ["coordinator", "implementation_worker_comms", "override_specialist", "verification_worker", "final_judge", "appellate_judge"]
    if any(role not in policy for role in roles):
        errors.append("role policy is incomplete")
    if policy.get("override_specialist", {}).get("may_judge_own_work") is not False:
        errors.append("override specialist must not judge own work")
    if policy.get("appellate_judge", {}).get("only_if") != ["override_used", "verifier_judge_disagreement", "conditional_verdict"]:
        errors.append("appellate trigger set changed")
    for key in ("goal_file", "tracker_file", "task_spec"):
        path = Path(str(spec.get(key, "")))
        if not path.is_absolute() or not path.is_file():
            errors.append(f"{key} is not an existing absolute file")
        elif hashes.get(key) != digest(path):
            errors.append(f"{key} hash mismatch")
    identity_hashes = hashes.get("identity_files", {})
    for value in spec.get("identity_files", []):
        path = Path(value)
        if not path.is_absolute() or not path.is_file():
            errors.append(f"identity file is not an existing absolute file: {value}")
        elif identity_hashes.get(value) != digest(path):
            errors.append(f"identity file hash mismatch: {value}")
    instruction_hashes = hashes.get("instruction_files", {})
    for value in spec.get("instruction_files", []):
        path = Path(value)
        if not path.is_absolute() or not path.is_file():
            errors.append(f"instruction file is not an existing absolute file: {value}")
        elif instruction_hashes.get(value) != digest(path):
            errors.append(f"instruction file hash mismatch: {value}")
    for role, path in ROLE_FILES.items():
        if not path.is_file():
            errors.append(f"missing agent config for {role}: {path}")
        elif hashes.get("agent_configs", {}).get(role) != digest(path):
            errors.append(f"agent config hash mismatch for {role}")
    for path in TELEMETRY_FILES:
        key = str(path)
        if not path.is_file():
            errors.append(f"missing telemetry helper: {path}")
        elif hashes.get("telemetry_helpers", {}).get(key) != digest(path):
            errors.append(f"telemetry helper hash mismatch: {path}")
    for path in SKILL_FILES:
        key = str(path)
        if not path.is_file():
            errors.append(f"missing TrajB-Lite skill file: {path}")
        elif hashes.get("skill_files", {}).get(key) != digest(path):
            errors.append(f"TrajB-Lite skill hash mismatch: {path}")
    if spec.get("comparable_to") and not spec.get("frozen_task_reused_exactly"):
        errors.append("comparability requires exact frozen task reuse")
    if spec.get("comparable_to") and len(spec.get("identity_files", [])) < 4:
        errors.append("comparability requires at least four hashed identity files")
    return errors


def create(args: argparse.Namespace) -> int:
    root = absolute_existing(args.project_root, "project_root", directory=True)
    goal = absolute_existing(args.goal_file, "goal_file")
    tracker = absolute_existing(args.tracker_file, "tracker_file")
    task = absolute_existing(args.task_spec, "task_spec")
    identity_files = [absolute_existing(value, "identity_file") for value in args.identity_file]
    instruction_files = [absolute_existing(value, "instruction_file") for value in args.instruction_file]
    output = Path(args.output_dir)
    if not output.is_absolute():
        raise ValueError("output_dir must be absolute")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"refusing to overwrite nonempty packet directory: {output}")
    artifact = Path(args.artifact_dir)
    if not artifact.is_absolute():
        raise ValueError("artifact_dir must be absolute")
    artifact = artifact.resolve()
    if artifact == output.resolve() or artifact == root or artifact in root.parents:
        raise ValueError("artifact_dir must be distinct and must not contain project_root")
    head = git_output(root, "rev-parse", "HEAD")
    if head != args.execution_start_commit:
        raise ValueError(f"project_root HEAD {head} does not match --execution-start-commit")
    if git_output(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("project_root must be a clean isolated execution worktree")
    submodules = git_output(root, "submodule", "status", "--recursive")
    if any(line.startswith(("-", "+", "U")) for line in submodules.splitlines()):
        raise ValueError("project_root submodules must be initialized at recorded pins")
    output.mkdir(parents=True, exist_ok=True)
    spec = {
        "schema_version": SCHEMA_VERSION,
        "goal_id": args.goal_id,
        "run_id": args.run_id,
        "trajectory_id": args.trajectory_id,
        "project_root": str(root),
        "execution_start_commit": args.execution_start_commit,
        "source_baseline_commit": args.source_baseline_commit,
        "goal_file": str(goal),
        "tracker_file": str(tracker),
        "task_spec": str(task),
        "output_dir": str(output.resolve()),
        "artifact_dir": str(artifact),
        "status": "ready_to_launch",
        "benchmark_id": args.benchmark_id,
        "comparable_to": args.comparable_to,
        "frozen_task_reused_exactly": bool(args.frozen_task_reused_exactly),
        "telemetry": {
            "helper_root": str(TELEMETRY_ROOT),
            "hook_run_dir": str(artifact / "telemetry" / "hooks"),
            "phase_export_root": str(artifact / "telemetry" / "phases"),
            "required_hook_events": [
                "run_started", "phase_started", "checkpoint_frozen",
                "direct_review_joined", "phase_completed",
                "verification_completed", "verdict_issued", "run_completed",
            ],
        },
        "phases": [
            {"id": "implement", "fresh_root": True},
            {"id": "verify_and_judge", "fresh_root": True},
            {"id": "appellate_if_triggered", "fresh_root": True, "conditional": True},
            {"id": "finalize", "fresh_root": False, "deterministic": True},
        ],
    }
    if spec["comparable_to"] and not spec["frozen_task_reused_exactly"]:
        raise ValueError("--comparable-to requires --frozen-task-reused-exactly")
    if spec["comparable_to"] and len(identity_files) < 4:
        raise ValueError("--comparable-to requires at least four --identity-file values")
    spec["identity_files"] = [str(path) for path in identity_files]
    spec["instruction_files"] = [str(path) for path in instruction_files]
    payloads = {
        "run_spec.json": spec,
        "policy.json": role_policy(),
        "input_hashes.json": {
            "goal_file": digest(goal),
            "tracker_file": digest(tracker),
            "task_spec": digest(task),
            "identity_files": {str(path): digest(path) for path in identity_files},
            "instruction_files": {str(path): digest(path) for path in instruction_files},
            "agent_configs": {role: digest(path) for role, path in ROLE_FILES.items()},
            "telemetry_helpers": {str(path): digest(path) for path in TELEMETRY_FILES},
            "skill_files": {str(path): digest(path) for path in SKILL_FILES},
        },
    }
    for name, value in payloads.items():
        (output / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    (output / "launch_commands.md").write_text(build_launch(spec))
    errors = validate_packet(output)
    if errors:
        raise ValueError("created packet failed validation: " + "; ".join(errors))
    print(json.dumps({"packet_dir": str(output), "status": "ready_to_launch"}, sort_keys=True))
    return 0


def validate(args: argparse.Namespace) -> int:
    packet = absolute_existing(args.packet_dir, "packet_dir", directory=True)
    errors = validate_packet(packet)
    result = {"packet_dir": str(packet), "valid": not errors, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    make = commands.add_parser("create")
    for name in ("project_root", "goal_id", "run_id", "trajectory_id", "goal_file", "tracker_file", "task_spec", "output_dir", "artifact_dir"):
        make.add_argument("--" + name.replace("_", "-"), required=True)
    make.add_argument("--benchmark-id", default="trajb-lite-v1")
    make.add_argument("--execution-start-commit", required=True)
    make.add_argument("--source-baseline-commit")
    make.add_argument("--comparable-to")
    make.add_argument("--frozen-task-reused-exactly", action="store_true")
    make.add_argument("--identity-file", action="append", default=[])
    make.add_argument("--instruction-file", action="append", default=[])
    make.set_defaults(handler=create)
    check = commands.add_parser("validate")
    check.add_argument("--packet-dir", required=True)
    check.set_defaults(handler=validate)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
