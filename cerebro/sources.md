# Cerebro Sources — Pointers to Core Jarvis Files

> Quick reference for where important files live.

## Core Configuration

| File | Path | Purpose |
|------|------|---------|
| CLAUDE.md | `~/.claude/CLAUDE.md` | Main Jarvis configuration |
| Goals | `~/.claude/goals.md` | Persistent cross-session goals |
| Settings | `~/.claude/settings.json` | Claude Code settings |

## Cerebro Wiki

| File | Path | Purpose |
|------|------|---------|
| Index | `~/.claude/cerebro/index.md` | Node catalog (read first each session) |
| Log | `~/.claude/cerebro/log.md` | Append-only operations log |
| Search | `~/.claude/cerebro/search.py` | FTS5 BM25 search engine |
| Sessions | `~/.claude/cerebro/sessions/` | One .md per work session |

## Skills

All skills live in `~/.claude/skills/<name>/SKILL.md`.

## Commands

All slash commands live in `~/.claude/commands/<name>.md`.
