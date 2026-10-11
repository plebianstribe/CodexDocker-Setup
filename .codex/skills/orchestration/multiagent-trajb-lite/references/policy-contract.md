# TrajB-Lite policy contract

## Purpose

The policy reduces root-token amplification by replacing one long-lived
Sol/xhigh coordinator with bounded, fresh Terra/medium phase roots. Expensive
reasoning is a narrow service, not persistent orchestration state.

## Phase boundaries

1. `implement`: owners work in parallel, exchange direct hash-bound reviews,
   correct only owned files, and produce a joined checkpoint.
2. `verify_and_judge`: a fresh coordinator gives a minimal artifact/evidence
   bundle to an independent Terra/high verifier and Sol/high final judge.
3. `appellate` (conditional): a fresh Sol/xhigh judge reviews only the frozen
   evidence packet when an override was used, the verifier and judge disagree,
   or the first verdict is conditional.
4. `finalize`: deterministic export, policy reconciliation, hashing, and sealing;
   do not keep an LLM root alive while polling or aggregating telemetry.

Do not resume a coordinator session across phase boundaries. A handoff contains
paths, hashes, commands/exits, decisions, unresolved risks, and no transcript
dump. Default guards are 24 coordinator turns per LLM phase, 100,000 input
tokens per coordinator turn, 2,000,000 input tokens per phase, eight total wait
calls, and two consecutive no-progress waits. Crossing a guard freezes the
checkpoint and starts a fresh phase root; it does not silently increase budget.

## Escalation triggers

Sol/xhigh override is allowed only when one of these is recorded:

- a blocking cross-component ambiguity affects at least two owned components;
- one owner correction plus deterministic rerun still fails for a reason not
  localized to one component;
- a novel architectural decision cannot be resolved from frozen contracts.

The override receives a bounded evidence bundle and returns a recommendation or
patch confined to explicit ownership. It cannot verify or judge that work.

The Sol/xhigh appellate judge is required when an override was used, when the
Terra/high verification disposition and Sol/high verdict disagree, or when the
first verdict is `CONDITIONAL PASS`. Otherwise it must not run.

## Evidence gates

Launch is blocked unless paths exist, the packet validates, ownership is
exclusive, the benchmark identity/comparability statement is explicit, and all
agent config files resolve. Completion is blocked unless runtime records attest
the requested model/effort/sandbox for every role, final capture includes each
phase terminal response, source telemetry hashes are stable, tests pass, and
the independent verdict chain is complete.
