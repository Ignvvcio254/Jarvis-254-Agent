# Installation — Jarvis-254-Agent

> Everything here is **idempotent** and **non-destructive**: re-running is safe and your existing
> `CLAUDE.md`, `settings.json`, `~/.claude.json` and model profiles are never overwritten.

## Requirements

| Tool | Needed for |
|---|---|
| [Claude Code](https://claude.com/claude-code) | Everything (other agents: see `AGENTS.md`) |
| Python 3.8+ | Installer, hooks, verify gate, memory wiki (stdlib only) |
| Git | Bootstrap / updates |
| Node.js 18+ | Optional: multi-model gateway |
| PowerShell 7 | Optional: `verify-gate.ps1`, `multi-cli` templates (Python equivalents exist) |

## Option A — Claude Code plugin (harness only)

```
/plugin install jarvis-harness --marketplace Ignvvcio254/Jarvis-254-Agent
```
Older Claude Code:
```
/plugin marketplace add Ignvvcio254/Jarvis-254-Agent
/plugin install jarvis-harness@jarvis-254
```
Installs the core skills (verify-repair, token-router, scratchpad, agent-uplift, multi-cli,
subagent-orchestration, long-run-harness, jarvis-evolve, prp, bucle-agentico), 9 subagents, the
`/memoria`, `/consumo`, `/doctor` commands and the autopilot hooks. Update with `/plugin update`,
remove with `/plugin uninstall jarvis-harness`.

> Use A **or** B for hooks, not both, or each hook runs twice.

## Option B — Everything, one line

```bash
curl -fsSL https://raw.githubusercontent.com/Ignvvcio254/Jarvis-254-Agent/main/scripts/bootstrap.sh | sh   # macOS/Linux/WSL
```
```powershell
irm https://raw.githubusercontent.com/Ignvvcio254/Jarvis-254-Agent/main/scripts/bootstrap.ps1 | iex       # Windows
```
Clones to `~/.jarvis-254` (`JARVIS_HOME` to change it), runs `install.py` and `jarvis_doctor.py`.
Run it again to update.

## Option C — Manual

```bash
git clone https://github.com/Ignvvcio254/Jarvis-254-Agent.git
cd Jarvis-254-Agent
python install.py --dry-run          # preview
python install.py                    # install
python install.py --no-hooks         # files only, settings.json untouched
python install.py --claude-dir PATH  # another Claude config dir
```

What `install.py` does:

| Source | Destination | Overwrites? |
|---|---|---|
| `skills/`, `agents/`, `commands/`, `rules/` | `~/.claude/...` | yes (repo files only; your other files stay) |
| `hooks/*`, `models/*` | `~/.claude/scripts/` | yes |
| `models/profiles/*.example.json` | `~/.claude/profiles/gateway.json`, `multi.settings.json` | **no** — only if absent |
| `CLAUDE.md` | `~/.claude/CLAUDE.md` | **no** — only if absent |
| hooks wiring | `~/.claude/settings.json` | **merged**, with a timestamped backup |

## After installing

1. **Personalize `~/.claude/CLAUDE.md`** — replace `{{YOUR_NAME}}`, `{{YOUR_OS}}`, `{{YOUR_SHELL}}`. If you
   already had a `CLAUDE.md`, compare it with the repo's and merge the sections you want.
2. **Memory wiki (optional)**
   ```bash
   mkdir -p ~/.claude/cerebro/sessions
   cp -n cerebro/*.md cerebro/search.py ~/.claude/cerebro/
   python ~/.claude/cerebro/search.py index
   ```
3. **MCP servers (optional)** — `mcp/mcp.template.json` lists recommended servers. **Merge** the entries you
   want into the `mcpServers` of `~/.claude.json` (or use `claude mcp add`); never copy the template over it.
   Keys go in environment variables (`mcp/env.example`).
4. **More models (optional)** — see [`docs/models.md`](docs/models.md).

## Verify

```bash
python jarvis_doctor.py                                         # installation health
python ~/.claude/skills/verify-repair/verify_gate.py --path .   # objective verdict on a project
```
In Claude Code, `/hooks` lists the installed hooks; a new session should show the `[session-boot]` context
when a `.scratch/task.md` exists in the project.

## Uninstall

- Plugin: `/plugin uninstall jarvis-harness`.
- Manual: restore the `settings.json.bak-*` backup (or delete the Jarvis hook entries) and remove the copied
  folders you don't want.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Hooks never fire | `/hooks` in Claude Code; check Python is on PATH (`python --version` / `python3 --version`). On Windows, disable the Store `python3` alias if it is a stub. |
| `verdict_guard` keeps asking for a verdict | Run `verify_gate.py --path .`; for tsc/build-only checks: `python ~/.claude/scripts/verdict_stamp.py tsc`. |
| Gateway models error | Keys missing: `~/.claude/.env` or env vars; `node ~/.claude/scripts/salud-modelos.mjs`. |
| Skills don't trigger | Confirm `~/.claude/skills/<name>/SKILL.md` exists; restart Claude Code. |
| Memory search fails | `python ~/.claude/cerebro/search.py index`. |
