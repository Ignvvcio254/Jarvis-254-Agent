---
name: subagent-orchestration
description: Orchestrate subagents (Agent/Task) with a context firewall, the fan-out→synthesize pattern and a rubric grader (Performance Outcomes). Use when a task is massively parallel, long, or benefits from isolated context windows — multi-source research, multi-file refactors, multi-perspective review, benchmarking N combinations. Complements multi-cli (external CLIs) with internal Claude subagents.
---

# subagent-orchestration — Parallelism with isolation and a grader

> Jarvis harness (frontier extension). Ports Anthropic's dynamic-workflow and Performance Outcomes patterns
> and the subagent "context firewall".

## The 4-layer doctrine

| Layer | Component | Role | When |
|---|---|---|---|
| 1 | CLAUDE.md | rules/memory | always |
| 2 | Skills | reusable inline procedure | repeatable task in the same context |
| 3 | Hooks | deterministic enforcement | a rule that must ALWAYS fire |
| 4 | **Subagents** | isolation + parallelism | work that would pollute the main context |

Decision rule: **"Skill teaches · Hook enforces · Subagent isolates"**. They combine.

## When to use a subagent (not inline)

Use `Agent`/`Task` when:
- The task would generate noise you won't look at again (searches, logs, mass reads) → **context firewall**:
  the main agent only sees the summary.
- It is massively parallel (N sources, N files, N combinations).
- Each step benefits from a clean context window (no cross-contamination).
- It is adversarial (generating vs verifying must be separate — see grader).

Do NOT use a subagent for small edits, single-file tasks, or anything where coordination costs more than doing
it inline. 3-5 concurrent subagents is the sweet spot; beyond that you spend more merging than you save.

## Pattern 1 — Fan-out → Synthesize

```
LEAD (strong model)
  ├─ fan-out: N cheap Explore subagents in parallel
  │    each: one source / one module / one hypothesis · its own context window
  ├─ barrier: wait for ALL
  └─ synthesize: one strong subagent (or the lead) merges the structured summaries
```

Model routing ([[token-router]]): explore = cheap (Haiku/free, parallel); synthesize = strong (where reasoning
pays off). Real savings: the bulk of the work runs on the cheap tier.

Examples: multi-source research, mapping a large codebase, refactoring N independent files, benchmarking N
models × prompts.

## Pattern 2 — Rubric grader (Performance Outcomes)

The objective verify-repair gate (exit code) covers binary tasks. For gradable quality add a **separate grader**:

```
GENERATOR (subagent A) → produces the deliverable
        ↓
GRADER (subagent B, different) → scores it against an explicit RUBRIC
        ↓
  passes? → accept
  no?     → back to the generator with the specific gap → revise (max N)
```

Rules:
- The grader is a DIFFERENT subagent from the generator (MAR: the same one gets stuck).
- The rubric is explicit and written FIRST: e.g. "all tests pass · no new TODOs · no public API changes ·
  coverage ≥ 80%".
- Wherever possible the rubric is anchored on an objective signal ([[verify-repair]]): the grader runs the gate
  and reads the verdict, it doesn't opine.

## Pattern 3 — SubagentStop gate

When a subagent finishes, its output is NOT accepted without passing the gate:
- Code task → run the verify gate on its output (exit 0 mandatory).
- Failure → re-dispatch the subagent with the gap; don't accept the summary.
- It is the subagent equivalent of multi-cli's `edited` + verdict check.

## Harness integration

| Skill | Role in orchestration |
|---|---|
| [[token-router]] | cheap model for fan-out, strong for synthesis — the savings |
| [[verify-repair]] | objective signal for the grader and the SubagentStop gate |
| `agent-uplift` spec compiler | each subagent gets a compiled one-shot spec |
| [[scratchpad]] | records which subagent did what + corrections |
| `multi-cli` | external sibling: other providers' CLIs in visible terminals instead of Claude subagents |

## Subagent vs multi-cli

- **Subagent** (`Agent`/`Task`): Claude work that needs a context firewall, inside the session. The lead only
  sees the summary.
- **multi-cli**: delegate to OTHER providers' models in visible terminals the user supervises; multi-provider
  resilience.

## Verifying this skill

- A research task: 3 parallel Explore subagents + 1 synthesis → a cited report.
- A code task with a grader: generator + separate grader running the verify gate.

## Anti-pattern

Spawning >5 subagents for everything "to parallelise": merging summaries costs more than it saves. Massive
fan-out only when the task genuinely opens up (N sources/files).
