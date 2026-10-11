---
name: multiagent-trajb-lite
description: Scaffold and validate thin-coordinator multi-agent trajectories that use direct sibling review, fresh stage roots, bounded Sol/xhigh escalation, independent verification, and separate final/appellate judges. Use for setting up or auditing a TrajB-Lite rollout on an existing goal without executing it implicitly.
---

# Multiagent TrajB-Lite

Create a reproducible rollout packet that prevents a high-cost root context from
growing across implementation, verification, judgment, and finalization.

## Workflow

1. Read the project agent instructions plus the named goal, tracker, and task
   specification. Do not start a rollout merely because this skill was loaded.
2. Decide whether the task reuses a frozen benchmark exactly. If any task input,
   expected output, seed, threshold, or test changes, assign a new benchmark ID
   and explicitly mark the run non-comparable to the old benchmark.
3. Run `scripts/scaffold_trajb_lite.py create` with explicit absolute project,
   goal, tracker, task-spec, and output paths. Never target an existing nonempty
   packet directory.
4. Run `scripts/scaffold_trajb_lite.py validate` on the packet before launch.
5. Inspect `launch_commands.md`. Execute its phases only when the user explicitly
   authorizes the rollout. Each phase is a fresh root invocation; never resume a
   prior phase's coordinator session.
6. After execution, export only the declared root sessions and descendants,
   reconcile requested versus resolved runtime settings, and apply the project's
   sealing/isolation contract.

## Shared Telemetry Interface

Use `/workspace/telemetry_helpers/` for every live TrajB-Lite run. Read its
`README.md`, initialize `telemetry_helpers.hooks` before phase 1, and record the
fresh-root phase boundaries, frozen checkpoints, direct-review join,
override/correction events, verification, first verdict, conditional appellate
verdict, and terminal completion. Invoke helpers with:

```bash
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.hooks
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.exporter
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.verify
PYTHONPATH=/workspace/telemetry_helpers python -m telemetry_helpers.bundle
```

After each phase's actual terminal response, export its explicit root session
and descendants beneath the run artifact root, verify it, then use
`telemetry_helpers.bundle` to index all executed phase exports. Never resume a prior phase root.
Hooks store metadata and artifact hashes only; the immutable rollout JSONL is the
authoritative message/tool source. Missing runtime fields remain `not_emitted`.

## Required Topology

- Coordinator: `gpt-5.6-terra` / `medium`, one fresh root per phase.
- Component owners: `gpt-5.6-terra` / `medium`, exclusive files, direct sibling
  checkpoint/review/correction messages. The coordinator cannot relay required
  sibling edges.
- Verifier: fresh `gpt-5.6-terra` / `high`, independent from implementation.
- Final judge: fresh `gpt-5.6-sol` / `high`, independent from implementation and
  verification.
- Override specialist: fresh, bounded `gpt-5.6-sol` / `xhigh`; invoke only on a
  recorded trigger and never let it issue a verdict on its own work.
- Appellate judge: fresh `gpt-5.6-sol` / `xhigh`; invoke only when an override was
  used, verifier and judge disagree, or the first verdict is conditional.

Read [references/policy-contract.md](references/policy-contract.md) before
changing defaults or launch phases. Validate packet shape against
[references/run-spec.schema.json](references/run-spec.schema.json).

## Commands

Create a packet:

```bash
python /workspace/.codex/skills/multiagent-trajb-lite/scripts/scaffold_trajb_lite.py create \
  --project-root /absolute/project \
  --execution-start-commit 0123456789abcdef0123456789abcdef01234567 \
  --goal-id EXAMPLE-LITE-01 \
  --run-id EXAMPLE-LITE-001 \
  --trajectory-id example_trajb_lite \
  --goal-file /absolute/project/EXAMPLE_GOALS.md \
  --tracker-file /absolute/project/EXAMPLE_TRACKER.md \
  --task-spec /absolute/project/path/to/task_spec.md \
  --output-dir /absolute/control/scaffolds/example_trajb_lite \
  --artifact-dir /absolute/control/artifacts/trajb_lite/example_trajb_lite
```

Validate without mutation:

```bash
python /workspace/.codex/skills/multiagent-trajb-lite/scripts/scaffold_trajb_lite.py validate \
  --packet-dir /absolute/project/artifacts/trajb_lite/example_trajb_lite
```

## Safety and Status Rules

- Packet creation is setup, not rollout execution and not completion evidence.
- Preserve dirty worktrees and unrelated user changes. Use a recorded clean
  baseline or isolated worktree for execution.
- Treat unavailable runtime telemetry as `not_emitted`, never zero or inferred.
- Stop a phase at its turn/input/wait guard and hand off through hashed artifacts.
- Keep source telemetry immutable; redact secrets only in derived exports.
- Never update a goal/tracker to completed without functional evidence,
  independent verification, required judgment, and runtime policy attestation.
