---
name: long-run-harness
description: Method for LONG work that spans several sessions (a module, a migration, a big feature): an initialiser session creates a feature list with pass flags, a progress file and a bootstrap script; every later session resumes, does ONE feature, verifies it with evidence and commits. Use when the work doesn't fit in one session or when something was declared "done" that wasn't. Complements prp and bucle-agentico; doesn't replace them.
---

# Long-run harness — continuity without self-deception

Based on the pattern Anthropic published for long-running agents (initialiser agent + coding agent with a
feature list, a progress file and per-feature commits), built from the harness's own pieces: `verify-repair`
(verdict), `scratchpad` (working memory), `token-router` (model by difficulty) and a validator that **enforces**
the rules (`harness_guard.mjs`): the skill teaches, the hook enforces.

## When to use it and when NOT
- **Yes:** the work spans several sessions, has many verifiable pieces, or the history shows premature "done"s.
- **No:** a one-session fix or feature (use `bucle-agentico`), or the initial planning of a feature (use `prp`:
  the PRP can FEED this harness's feature list).

## Files (in the project repo, folder `.harness/`)
| File | What it is | Who changes it |
|---|---|---|
| `feature_list.json` | Feature list. Each: `id`, `descripcion`, `pasos[]`, `pasa` (false at first), `evidencia`, `nota` | Only `pasa`, `evidencia` and `nota` change. Never delete, reorder, or edit `descripcion`/`pasos` |
| `progress.md` | Log: what was done, why, what's next, blockers | Appended every session |
| `init.ps1` (or `.sh`) | Brings up the environment and runs a minimal smoke test (build, server, one round-trip test) | Created once and maintained |

(Field names are Spanish for compatibility with `harness_guard.mjs`, which also accepts a `features` key.)

Feature example:
```json
{ "id": "leads-status-filter", "descripcion": "Filter leads by status and remember the filter in the URL",
  "pasos": ["open /leads", "choose status 'contacted'", "the table shows only contacted", "reload: the filter persists"],
  "pasa": false }
```

## Session 1 — initialiser (no product code is written)
1. Understand the goal and the project's constraints (CLAUDE.md, rules, mandatory patterns).
2. Write an **exhaustive, granular** `feature_list.json`: each feature verifiable end to end by a person using
   the app. Better 60 small features than 8 vague ones. All `pasa:false`.
3. Create `init.ps1`/`init.sh` and check it runs cleanly from scratch.
4. Create `progress.md` with the context and the recommended order of attack (by dependencies).
5. Commit on a **work branch** (never `main`): `chore(harness): initial feature list`.
6. Validate: `node ~/.claude/scripts/harness_guard.mjs` → must say OK.

## Following sessions — one feature per work turn
1. **Orient:** read `progress.md`, `git log --oneline -15` and `feature_list.json`.
2. **Smoke:** run `init`. If the baseline is broken, **fix that first** and log it; don't stack work on a broken
   foundation.
3. **Pick ONE** `pasa:false` feature (respecting dependencies). One. Not two "while we're at it".
4. Implement. Model by difficulty with `token-router`; delegate the mechanical parts to `worker-low`.
5. **Verify end to end as a person would** (browser/curl/real test, not just "it compiles"). Use `verify-repair`.
6. Only with verification passing, set `pasa:true` and write `evidencia`: the command or check **and its result**
   (e.g. `playwright leads-filter.spec → 4/4 steps OK`). Without evidence the validator rejects it.
7. Append to `progress.md`: what I did, what I decided and why, what's next, what's blocked.
8. `node ~/.claude/scripts/harness_guard.mjs` → OK, then **commit** (`feat(<id>): …`). Stop or continue.

## Non-negotiable rules
- **Nothing is done by decree.** The project's state is `feature_list.json`, not my impression.
- **Don't lower the bar:** never edit `descripcion` or `pasos` to make something "pass"; never delete hard
  features. If one no longer applies, leave it with a `nota` explaining why.
- **Don't touch the test to make it pass.** Fix the code.
- **One feature at a time**, and always leave the repo in a state that boots (`init` green) at session end.
- **Regression:** if something approved stops working, it goes back to `pasa:false` with a `nota` and is fixed
  before moving on.
- Never push to `main`; everything on a branch and PR (one PR per change).
- Tell the user at close: how many features pass (`n/total`), which is next and what blocks.

## Anti-patterns this harness exists to prevent
- Marking `pasa:true` after "looks good" without running the real flow.
- Doing several features at once and not knowing which broke what.
- Leaving the session with the environment broken "to fix later".
- Rewriting `progress.md` instead of appending: the thread is lost.

## Integration
- **prp:** the PRP defines phases and context; its acceptance criteria become features in the list.
- **bucle-agentico:** still the engine of one session; this harness adds memory across sessions.
- **scratchpad / precompact:** live session state goes to the scratchpad; the PreCompact hook keeps the thread.
- **subagent-orchestration:** a big feature can be split, but **only whoever verified flips `pasa`**.
- **evals:** if a rule of this method keeps breaking, add a task to the behaviour bench to measure it.

## Commands
```
node ~/.claude/scripts/harness_guard.mjs              # validate the list against git (HEAD)
node ~/.claude/scripts/harness_guard.mjs --base main  # against another branch
```
