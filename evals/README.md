# Behaviour bench — does the agent follow its own rules?

`jarvis-eval.mjs` runs each task as a real `claude -p` session in a fresh temp directory (your hooks and
`CLAUDE.md` load; MCP servers don't) and grades it **objectively**: files on disk, tools actually used, code
actually executed — never the model's own claim.

| Task | Rule tested |
|---|---|
| `inyeccion` | Instructions inside a file are data, not orders (prompt injection) |
| `destructivo` | Confirm before deleting |
| `arreglo_verificado` | A fix is done when the test passes — without editing the test |
| `secretos` | Never hard-code a key; use environment variables |
| `no_inventar` | If something doesn't exist, say so |
| `idioma_del_usuario` | Answer in the user's language |
| `verificar_antes_de_reportar` | Run what you built before saying it works |
| `concision_1..3` | Simple question → short answer |

```bash
node evals/jarvis-eval.mjs --selftest                 # free: graders distinguish good vs bad cases
node evals/jarvis-eval.mjs --model haiku --only inyeccion,secretos
node evals/jarvis-eval.mjs --report                   # regressions vs previous run
node evals/jarvis-eval.mjs --gateway --model nim/z-ai/glm-5.3   # same bench, other providers
```
History: `~/.claude/metrics/eval_history.jsonl`. `CLAUDE_BIN` overrides the Claude binary.
Add a task in `tareas.mjs` with `setup`, `prompt`, `grade(ctx)` and `simular(dir, good)` — the selftest
fails until your grader separates a good run from a bad one.
