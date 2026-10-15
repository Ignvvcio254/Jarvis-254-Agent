---
description: Measure the agent against objective tests of its own rules (prompt injection, destructive actions, secrets, verify-before-report, no hallucination, concision)
---

# /eval-jarvis

Behaviour bench in `~/.claude/evals/` (source: `evals/` in the Jarvis-254-Agent repo). Argument: `$ARGUMENTS`

Each task is a full `claude -p` session in a temp dir with no MCP servers: it costs tokens.

1. No argument or `selftest`: `node ~/.claude/evals/jarvis-eval.mjs --selftest` (free; checks every grader tells the good case from the bad one).
2. `list`: `node ~/.claude/evals/jarvis-eval.mjs --list`.
3. `report`: `node ~/.claude/evals/jarvis-eval.mjs --report` (compares the last two runs and flags regressions).
4. `run` (optionally `--model haiku|sonnet|opus`, `--only id1,id2`, `--gateway` to test non-Claude models): ask the user to confirm before a real run.
5. Present the result as a short table. On a REGRESSION, say what changed since the previous run (hooks, CLAUDE.md, skills) before proposing fixes.

The verdict comes from the bench (disk state, tools used, real execution), never from your opinion.
