# Harness — objective verdicts, cheap models, self-improvement

> **Skill teaches · Hook enforces · Subagent isolates.**
> A task is done when the system confirms it (exit code, test, grep, screenshot) — never because the model says so.

Install as a plugin (`/plugin install jarvis-harness --marketplace Ignvvcio254/Jarvis-254-Agent`) or run
`python install.py`, which installs everything below and merges the hooks into `~/.claude/settings.json`
(backup first, no duplicates, your own hooks untouched).

## 1. Core skills (`skills/`)

| Skill | Use it when |
|---|---|
| `verify-repair` | Before reporting ANY code/fix/build. `verify_gate.py` (any OS; `verify-gate.ps1` on PowerShell) auto-detects the project, runs parse/typecheck/lint/test/behaviour checks and writes `.verify/verdict.json` bound to a hash of the tree. Repair loop with a critic separate from the generator. |
| `token-router` | Before executing or delegating: pick the *minimum* sufficient model per difficulty (trivial → Haiku/free, standard → Sonnet, hard → Opus). |
| `scratchpad` | Multi-phase tasks (`.scratch/task.md`), capturing user corrections, and propagating learnings to memory at session close. |
| `subagent-orchestration` | Massively parallel / long / adversarial work: fan-out → synthesize, rubric graders, `SubagentStop` gates. The main context only sees summaries. |
| `agent-uplift` | Make cheap models deliver frontier-grade results: spec compiler, verify-repair, per-model anti-patterns, benchmark. |
| `multi-cli` | Dispatch work to other agent CLIs (Antigravity, OpenCode, Codex…) in visible terminals with `.done` signals. |
| `long-run-harness` | Features that span many sessions: `.harness/feature_list.json` + `hooks/harness_guard.mjs` (a feature can only flip to `pasa:true` with evidence; descriptions are immutable). |
| `jarvis-evolve` | Self-improvement loop: SENSE → DIAGNOSE → PROPOSE → APPLY → MEASURE → RECORD. Always proposes, never applies without approval. |

## 2. Autopilot hooks (`hooks/` → `~/.claude/scripts/`)

| Event | Script | What it automates |
|---|---|---|
| SessionStart | `session_boot.py` | Restores the active scratchpad ("where were we") at startup. |
| UserPromptSubmit | `archetype_router.py` | Classifies the task (BUILD/FIX/DESIGN/…) and injects which skills to activate. |
| UserPromptSubmit | `correction_detector.py` | Detects user corrections and reminds the model to save the pattern. |
| PreToolUse | `destructive_guard.py` | Mass/recursive deletes and irreversible MCP calls (delete, buy, merge, rollback…) ask for confirmation. |
| PreCompact | `precompact_checkpoint.py` | Saves a checkpoint (last requests, touched files, pending work) before context compaction. |
| Stop | `verdict_guard.py` | If code was edited without a passing verdict, blocks the stop and asks for `verify-gate`. |
| (manual) | `token_ledger.py` | Logs model + difficulty + gate + repairs: `python ~/.claude/scripts/token_ledger.py report`. |
| (optional) | `model_router.py` | UserPromptSubmit hook that suggests haiku/sonnet/opus per message. Not installed by default. |

Disable any hook by removing its entry from `settings.json`; nothing else depends on it.

## 3. Subagents (`agents/` → `~/.claude/agents/`)

`planner`, `architect`, `tdd-guide`, `code-reviewer`, `security-reviewer`, `silent-failure-hunter`,
`build-error-resolver`, `doc-updater`, `worker-low` (cheap Sonnet executor for fully specified, mechanical tasks).

## 4. Doctrines

- **One-shot dispatch:** every hand-off to a worker is self-contained (numbered spec + context verified by grep, never assumed).
- **Fresh context over patching:** if a delivery misses by more than a detail, re-derive in a fresh conversation.
- **Verify the effect, not the config:** a hook in the JSON proves nothing; its line in the log does.
- **No silent failure:** an empty result with an `error` is undiagnosable. If something is rejected, say why.
- **Installers merge, never overwrite** (that's why `install.py` exists).
