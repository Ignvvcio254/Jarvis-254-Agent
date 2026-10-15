---
name: agent-uplift
description: System that makes cheap/free models deliver frontier-class TASK RESULTS through a harness (compiled specs, generate→verify→repair loop, decomposition, evidence-based routing and per-model anti-patterns). Use when raising the quality of workers (other CLIs, subagents, gateway models), running an uplift benchmark, or closing the cheap-model vs frontier gap.
---

# AGENT-UPLIFT — frontier-class results with any model

## Thesis (honest)

You cannot turn a 26B model into a frontier model — the weights don't change. What you CAN match is the **task
result**: a cheap model inside a disciplined harness (perfect spec + objective verification + bounded repair
+ decomposition) produces outputs that pass the same review a frontier delivery would. The cheap-vs-frontier
gap on agentic tasks is mostly about **context, verification and retries** — not raw intelligence. That's
harness, and the harness is ours.

Seed evidence (benchmark on a real game codebase):
- A small model failed QA on a 71 KB file (session exhausted) → with session continuation + a deliverable
  check, it completed it.
- A top model delivered a full phase first time with a 6-point numbered spec.
- A mid model skipped 1 of 6 spec points → caught by a grep checklist → a bounded fix closed it.
→ The same model performs at different levels depending on the spec and the loop. That's the lever.

## Architecture (5 components)

### 1. SPEC COMPILER — compile the request into a perfect one-shot
> Working template: `templates/spec-template.md` (fill it + run the checklist before dispatching).
Every dispatch is compiled before it reaches the worker:
- **Minimum sufficient context**: what exists (exact functions/contracts with real names — verified by grep,
  never assumed), what NOT to touch.
- **Auditable numbered points** (1..N), each with an observable acceptance criterion.
- **Output contract**: exact files, format, "summary max N lines".
- **Execution prefix** for models that plan instead of executing: "this task is complete ONLY when you write
  code with your tools; do not describe plans".
- **Injected anti-patterns** of the target model (component 4).
- Budget: a cheap-model task has ≤ 6 points and ≤ 1 large file; if it exceeds → decompose (component 3).

### 2. VERIFY-REPAIR — generate→verify→repair loop
After each delivery, OBJECTIVE verifiers (not opinion):
- Deliverables exist / were edited (the `.done` signal of the multi-cli runner).
- Syntax: `node --check` / the language's linter.
- Grep checklist: one evidence pattern per numbered point.
- Functional: Playwright / curl / test runner depending on the type.
Result → verdict: ACCEPTED / REPAIR (one-shot repair with ONLY the failed points + failure evidence) / ESCALATE.
Max 2 repairs per task; the repair runs in a FRESH conversation (no contamination).

**Critic ≠ generator (MAR, arXiv 2512.20845):** whoever diagnoses and repairs must NOT be the same reasoning
that produced the error — a single agent reflecting on its own failure repeats it ("cognitive entrenchment").
Rules:
- The critic starts from the verifier's OBJECTIVE OUTPUT (which check failed, its real output), not from the
  generator's reasoning.
- If the generator was a worker → the repair goes to a fresh conversation, ideally a different model or a
  higher tier (evidence-based routing).
- If the generator was the main agent → explicitly take the critic role: read the [[verify-repair]]
  `verdict.json` and attack from another angle, don't re-justify.
- Engine: [[verify-repair]] provides the verdict; agent-uplift provides the repair policy (how many attempts,
  who repairs).

### 3. DECOMPOSE-ROUTE — decomposition and evidence-based routing
- Big task → subtasks sized for what the cheap tier solves well (benchmark data, not intuition).
- Router: task type × success history per model (a living table in `benchmark/results.md`).
- Integrating the pieces: always a high tier — integration is where cheap models fail.

### 4. ANTI-PATTERN CATALOG — "training" without touching weights
`~/.claude/skills/agent-uplift/antipatterns/<model>.md` — every observed failure is catalogued:
`[date] · symptom · cause · PROMPT COUNTERMEASURE (injectable text)`.
The spec compiler injects the target model's countermeasures into every spec. The catalog only grows → the
same model improves with every task without retraining. Starters:
- **Small models in agentic CLIs**: run out of session on files >50 KB → "don't read whole files; use targeted
  searches" + split the task.
- **Mid models on long specs**: skip points → "before finishing, re-read points 1..N and check each one".
- **Any model in headless `-p` mode**: answers with a plan without executing → execution prefix.

### 5. BENCHMARK — if you don't measure it, it didn't improve
Suite in `<project>/benchmark/`: ~10 reproducible tasks on a test codebase (bounded feature, fix with repro,
refactor, new module, QA, integration, edge cases, technical docs, test suite, a task with an
anti-instruction trap).
Rubric per task: % of spec points with evidence + syntax + functional + repairs used. Score 0-100.
Protocol: measure each model WITHOUT the harness (baseline) and WITH the full harness. Success metric:
**free tier with harness ≥ 90% of the top model's score without harness**. For behaviour (rules), use
`evals/jarvis-eval.mjs`.

## Iteration cycle (permanent agentic loop)

```
benchmark → worst gap → improve the responsible component
(spec? verifier? router? new anti-pattern?) → re-benchmark → repeat
```
Each iteration leaves: a new score in `benchmark/results.md` + new anti-patterns + one concrete change in a
component. Never two iterations without a measurement between them.

## Related skills
- `multi-cli`: the EXECUTION layer (terminals, runners, `.done`, notifications). agent-uplift is the QUALITY
  layer on top.
- `bucle-agentico`: governs the phases of a project (blueprint, just-in-time context).
- Ethical limits: this raises software-engineering capability. No safeguard evasion, offensive cyber or
  biology — out of scope by design.

## Harness integration (sibling skills)
- [[verify-repair]] provides the objective verdict (engine of component 2).
- [[token-router]] provides routing by difficulty (engine of component 3).
- [[scratchpad]] provides memory + correction detection (feeds component 4).
