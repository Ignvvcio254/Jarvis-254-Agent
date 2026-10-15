---
name: verify-repair
description: OBJECTIVE verdict gate before reporting any delivery. A task is not done because the model says so, but because an executable signal confirms it (exit code, test, lint, grep, screenshot). Includes a repair loop with a critic separate from the generator. Activate when closing any code task, fix, build or verifiable deliverable.
---

# verify-repair — The verdict is not a model claim

> Core of the Jarvis harness. Ports the anti-gaming pattern of evolve-loop (`commit-gate`) and the
> verification order of prax-agent.
> Doctrine: *"The verdict is not a model claim — it's an exit code. The model writes prose but cannot game
> the predicate suite."*

## The principle (non-negotiable)

A task is **NOT complete because the agent says so**. It is complete when an **objective signal**
confirms it. The model can write prose; it cannot game the predicate.

Root cause this removes: reporting success without verifying (e.g. the `dayPhase` case — "it's done" was
reported, Playwright showed the feature did not exist).

## When it activates (mandatory)

Before reporting as complete ANY task of:
- new or edited code
- bug fix
- build / config / infra
- a worker's deliverable (other CLIs or subagents)
- refactor / delete

Does not apply to: conversational answers, pure research, design decisions.

## Equivalent gates + stamp (avoids verdict_guard false positives)

The gate writes `.verify/verdict.json`. Other gates are as strong or STRONGER and `verdict_guard`
recognises them:
- **Auto-recognised by the guard** (nothing needed): `.js/.mjs/.cjs` → `node --check`; `.py` → `py_compile`.
  The guard checks them itself and stays quiet if they pass.
- **Expensive ones (TS / build / deploy)**: if you verified with `tsc --noEmit` exit 0, `npm run build`, or a
  deployment reported READY, **stamp it** so the guard doesn't fire a false positive:
  `python ~/.claude/scripts/verdict_stamp.py <gate>` (e.g. `tsc`, `vercel-build`).
  Stamp ONLY after a REAL verification that passed; it is not a way to skip the gate.

## Verification order (adapted from prax-agent)

Run **only the checks the project supports**, in this order. Skip the inapplicable ones saying why (never
silently):

```
1. build / parse   → does it compile / parse without error?
2. typecheck       → tsc, pyright, mypy (if typed)
3. lint            → eslint, ruff, etc. (if configured)
4. test            → the project's suite, or the case verifier
5. behaviour       → grep for the expected pattern / playwright screenshot of the result
```

Rule: **use the project's existing entrypoint** (`npm test`, `pytest`, …). Don't invent commands. Report
ONLY real execution results.

## The engine: verify_gate.py (any OS) / verify-gate.ps1

`verify_gate.py` is the Python port, identical in checks and in `.verify/verdict.json`; runs on Windows,
macOS and Linux without PowerShell:

```bash
python ~/.claude/skills/verify-repair/verify_gate.py --path .
python ~/.claude/skills/verify-repair/verify_gate.py --path . --verifier "node verify.js"
python ~/.claude/skills/verify-repair/verify_gate.py --path . --must-contain dayPhase --file game.html
```

What the gate does:
- Auto-detects the project type (node / python / static web / generic)
- Runs the available checks
- Writes `.verify/verdict.json` with the result per check + `stateHash` (sha256 of the tree) + final verdict
- **Exit 0 only if everything applicable passes.** Exit 1 if anything fails, or if there was nothing to check.

The `stateHash` binds the verdict to the exact state of the code (evolve-loop pattern): if the code changes
afterwards, the previous verdict no longer counts → impossible to game.

PowerShell equivalent:
```powershell
pwsh ~/.claude/skills/verify-repair/verify-gate.ps1 -Path .
pwsh ~/.claude/skills/verify-repair/verify-gate.ps1 -Path . -Verifier "node verify.js"
pwsh ~/.claude/skills/verify-repair/verify-gate.ps1 -Path . -MustContain "dayPhase" -File "game.html"
```

## The repair loop (critic ≠ generator)

If the gate exits 1:

```
1. READ verdict.json → identify WHICH check failed and its real output
2. The CRITIC (a different role from the one that generated) diagnoses the root cause
   · NOT the same reasoning that produced the error (MAR: a single agent gets stuck)
   · if it was a worker, re-derive in a FRESH conversation (one-shot doctrine)
3. APPLY a fix aimed at the failing check
4. RE-RUN the gate
5. Repeat until exit 0 or MAX_REPAIR (default 3)
6. If it still fails after MAX_REPAIR → STOP and report to the user:
   what fails, what was tried, the objective output. Never report a false success.
```

Why a separate critic: research (MAR, arXiv 2512.20845) shows a single agent reflecting on its own error
**repeats the error**. The critic must attack from another angle: read the check's objective output, not
the previous reasoning.

## Anti-gaming (from evolve-loop)

- The verdict lives in `verdict.json`, bound to `stateHash`.
- If anyone (the model included) edits the code without re-verifying, the hash no longer matches → the verdict
  is invalid.
- The model must not write `verdict.json` by hand: the script writes it after running the real checks.

## Delegating to workers

When dispatching to other CLIs via `multi-cli`, include in the spec:
> "Your delivery is not accepted until the verify gate exits 0. Run the verification yourself before
>  marking `.done`."

The `multi-cli` runner runs the gate on the worker's output before accepting it. `edited=True` (size changed)
+ `verdict=pass` = valid delivery.

## Verifying this skill (meta)

On a project lacking a feature: `verify_gate.py --path . --must-contain "dayPhase" --file game.html` must exit 1
— proving the gate catches what a human report missed.

## Related

Part of the harness with [[token-router]] (which model), the spec compiler in `agent-uplift` (which
instruction) and `multi-cli` (how to delegate). An objective verdict is a prerequisite of the router: without
it, cheap models can't be trusted.
