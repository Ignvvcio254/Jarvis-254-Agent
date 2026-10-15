# AGENTS.md — Jarvis-254 operating contract (any coding agent)

This file is read by agents that follow the AGENTS.md convention (Codex, OpenCode, Cursor, Gemini CLI,
Claude Code via `CLAUDE.md`). It is the portable core of Jarvis; the full contract lives in `CLAUDE.md`.

## Non-negotiable rules
1. **Objective verdict.** A task is done when a check confirms it, not when you say so. Before reporting
   code as done run `python skills/verify-repair/verify_gate.py --path <project>` (exit 0 = pass).
   No applicable checks → write a verifier (`--verifier "…"`) or a behaviour check (`--must-contain … --file …`).
2. **Verify the effect, not the configuration.** A setting in a file proves nothing; its observable result does.
3. **No silent failure.** Never report success on empty results, swallowed errors or optimistic fallbacks.
4. **Confirm before irreversible actions:** deleting, force-pushing, deploying, paying, sending messages.
5. **Never commit secrets.** Keys come from environment variables (`env:NAME` in configs).
6. **Branch + PR.** Never push to the default branch directly.

## Working method
- Classify the task (BUILD · FIX · DESIGN · RESEARCH · TEST · DEPLOY · AUTOMATE · DATA) and load the
  matching skill from `skills/` before coding (`skills/<name>/SKILL.md`).
- Search before reading: grep for the symbol, then open only the relevant range.
- Multi-phase work: keep notes in `.scratch/task.md`; long features: `.harness/feature_list.json`
  (see `skills/long-run-harness`).
- Use the cheapest model that can do the job (`skills/token-router`); lift it with a precise spec and the
  verify-repair loop (`skills/agent-uplift`).
- When the user corrects you, extract the rule and persist it — never leave it only in the conversation.

## Repo map
| Path | What |
|---|---|
| `skills/` | 1400+ procedural skills; core harness: verify-repair, token-router, scratchpad, agent-uplift, multi-cli, subagent-orchestration, long-run-harness, jarvis-evolve |
| `agents/` | Subagent definitions (planner, reviewers, TDD, silent-failure hunter, cheap worker) |
| `hooks/` | Claude Code autopilot hooks (Python, stdlib only) |
| `models/` | Local gateway: any provider/model in Claude Code's `/model` |
| `plugins/jarvis-harness/` | Generated Claude Code plugin (`python scripts/build_plugin.py`) |
| `tests/` | `python -m pytest tests` · `node --test hooks/*.test.mjs models/*.test.mjs` |

## Contributing changes to this repo
Run `python -m pytest tests -q`, the node tests and `python scripts/build_plugin.py --check` before a PR.
Never add personal paths, names or credentials (a test enforces it).
