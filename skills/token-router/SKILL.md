---
name: token-router
description: Decide the MINIMUM sufficient model for each task/subtask before executing or delegating. Token savings by difficulty — never default to the most powerful model. Trivial→Haiku/free model, standard→Sonnet, complex→Opus. Activate when planning work, delegating to workers (other CLIs, subagents), or on any task with meaningful token cost.
---

# token-router — The minimum sufficient model, not the most powerful

> Jarvis harness. Ports the CostAwareRouter of `grind` (Opus plans, Haiku executes, 3-5× savings) plus the
> test-time-scaling evidence (small model + verification = frontier level; arXiv 2408.03314, 2502.06703).

## The principle

Don't use the most powerful model by default. Use the **minimum sufficient** for the real difficulty of the
task. The harness's big savings live here.

It works because the [[verify-repair]] gate backs the cheap model: if it fails, the objective verdict catches
it and it gets repaired. Without verify-repair, cheap model = risk. With it, cheap model = cheap AND reliable.
**The router depends on the gate.**

## The two routing dimensions

`hooks/model_router.py` (optional UserPromptSubmit hook) adapts the session's BEHAVIOUR (brevity/depth).
This skill covers the other dimension: **who to DELEGATE the execution to** (the main agent or a worker, and
with which model).

| Dimension | Handled by | Decides |
|---|---|---|
| Session behaviour | `model_router.py` (hook) | Brevity vs depth |
| **Work delegation** | **this skill** | **Main agent vs worker, and which model** |

## Decision matrix (difficulty → engine → cost)

| Level | Task signals | Engine | Relative cost |
|---|---|---|---|
| **Trivial** | rename, formatting, lookup, 1-3 line edit, search, parse | Haiku / **free model via the gateway** | ~1× |
| **Standard** | new function, CRUD, scoped fix, single-file refactor, unit test | Sonnet | ~12× Haiku |
| **Complex** | architecture, multi-file debugging, long task, chained reasoning, design decision | Opus | ~60× Haiku |

Check current per-token prices on the provider's pricing page; the ratios are what matter.

## Classifying difficulty

Go up a level ONLY on a real signal. COMPLEX signals (any one is enough):
- Touches ≥3 coordinated files
- Needs >3 steps of chained reasoning
- Architectural decision or trade-off
- Long / multi-phase task
- Root-cause debugging that isn't obvious

TRIVIAL signals (all must hold):
- 1 file, bounded change
- No design decision
- Result mechanically verifiable (lint/grep/parse)

Default when torn between two levels: the LOWER one + verify-repair. If the gate fails and repair doesn't
converge in 2 attempts → go up one level (escalate on evidence, not out of caution).

## Routing to workers (with multi-cli / subagents)

| Task | Worker + model |
|---|---|
| Trivial parallel batch (formatting, repetitive generation) | subagent `worker-low`, or a free model via the gateway |
| Standard module against an interface contract | Sonnet subagent or another CLI |
| Complex component / delicate refactor | Opus |

Golden rule: **every worker delivers with the verify gate at exit 0**, whatever its model. The gate is what
lets you trust the cheap model.

## Success metric

Tokens spent per successfully completed task. Success = "works (gate pass) AND cost less than doing it with
Opus outright". Record in the task scratchpad: assigned level, engine used, first-try gate pass, repair
attempts — or log it with `python ~/.claude/scripts/token_ledger.py log …`.

## Anti-pattern

"Just in case, use Opus" → wastes 60× tokens on trivial tasks. The right caution is not the expensive model:
it is the verify-repair gate on top of the cheap one.

## Related

Depends on [[verify-repair]] (without an objective gate you can't step down a model). Integrates with
`multi-cli` (delegation) and the spec compiler of `agent-uplift` (a clean spec makes the cheap model perform
like an expensive one).
