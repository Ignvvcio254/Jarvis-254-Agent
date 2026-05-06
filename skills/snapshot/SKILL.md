---
name: snapshot
description: "Create and restore checkpoints of Jarvis configuration and active project state. Activate with: /snapshot create, /snapshot list, /snapshot restore <id>, /snap create — or before any destructive operation. Inspired by the Hermes Agent snapshot/rollback system."
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Snapshot — State Checkpoints

> Inspired by the `/snapshot` + `/rollback` system of Hermes Agent (NousResearch).
> Safety net before risky operations. Never deletes snapshots automatically.

---

## When to Create a Snapshot

Create automatically (without the user asking) before:
- Modifying `~/.claude/CLAUDE.md` or `~/.claude/settings.json`
- Running curator or skill merges
- Database migrations or schema changes
- Force-push or rebase on shared branches
- Any operation marked as destructive

---

## Commands

### `/snapshot create [name]` or `/snap`

```
1. Generate ID: YYYY-MM-DD-HH-MM-SS (UTC timestamp)
2. Create directory: ~/.claude/snapshots/<id>/
3. Capture configuration files:
   - ~/.claude/CLAUDE.md
   - ~/.claude/settings.json
   - ~/.claude/goals.md (if it exists)
   - ~/.claude/cerebro/index.md
   - ~/.claude/cerebro/log.md
4. Capture git state of the active project:
   - git log --oneline -10 > git-log.txt
   - git diff HEAD > git-diff.txt
   - git status > git-status.txt
5. Create metadata.json
6. Confirm: "Snapshot created: <id>"
```

**Snapshot structure:**
```
~/.claude/snapshots/YYYY-MM-DD-HH-MM-SS/
├── metadata.json
├── CLAUDE.md
├── settings.json
├── goals.md
├── cerebro-index.md
├── cerebro-log.md
├── git-log.txt
├── git-diff.txt
└── git-status.txt
```

### `/snapshot list`

```
1. Glob ~/.claude/snapshots/*/metadata.json
2. Show table: ID | Date | Project | Reason
3. Sort by most recent first
```

### `/snapshot restore <id>`

```
CONFIRM with the user before executing

1. Verify the snapshot exists
2. Show what will be restored
3. Wait for explicit confirmation
4. On confirm:
   a. Create snapshot of CURRENT state first (pre-restore backup)
   b. Copy config files to destination
   c. Report: "Restored from <id>"
```

### `/snapshot prune [--keep N]`

```
1. Default: keep the last 30 snapshots
2. Delete the oldest ones that exceed the limit
3. NEVER delete snapshots with "pinned": true in metadata.json
```

---

## metadata.json — Structure

```json
{
  "id": "YYYY-MM-DD-HH-MM-SS",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "project": "project-name",
  "project_path": "/absolute/path/to/project",
  "reason": "description of why it was created",
  "pinned": false,
  "files_captured": ["CLAUDE.md", "settings.json", "goals.md"]
}
```

---

## `/rollback [N]` — Git Rollback

```
/rollback         → show last 10 commits with restore option
/rollback 3       → show what would be lost by git reset --soft HEAD~3
/rollback apply N → execute git reset --soft HEAD~N (confirm before)
```

**Rule:** `/rollback apply` always creates a snapshot before executing.

---

## Safety Limits

- Snapshots are never deleted automatically
- `restore` always creates a pre-restore backup before restoring
- Do not include tokens or API keys in snapshots (sanitize automatically)
- Maximum 50 snapshots before requiring `/snapshot prune`
