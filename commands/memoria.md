---
name: memoria
description: "Jarvis cerebro wiki management — session ingest, knowledge query, index lint. Slash command: /memoria [ingest|query <term>|lint|stats]"
---

# /memoria — Cerebro Wiki Management

> The cerebro wiki is Jarvis's long-term memory: session nodes, decision records, and accumulated technical context.

## Commands

### `/memoria ingest`

Creates a session node from the current conversation. Run at the end of significant work sessions.

**Process:**
1. Review the conversation — what was worked on, what decisions were made, what files were modified
2. Create `~/.claude/cerebro/sessions/YYYY-MM-DD-<slug>.md` with frontmatter:
   ```markdown
   ---
   title: <descriptive session title>
   date: YYYY-MM-DD
   area: <jarvis|ops|dev|design|personal>
   tags: tag1, tag2, tag3
   status: complete
   ---
   ```
3. Body includes: Summary, Key Decisions, Files Modified, Lessons Learned, Next Steps
4. Update `~/.claude/cerebro/index.md` — add node to catalog
5. Append to `~/.claude/cerebro/log.md`
6. Run `python ~/.claude/cerebro/search.py index` to update FTS5 index
7. Confirm: "Session node created: YYYY-MM-DD-<slug>"

### `/memoria query <term>`

Search accumulated knowledge using FTS5 BM25 ranking.

**Process:**
1. Run `python ~/.claude/cerebro/search.py query "<term>"`
2. Present results with title, area, date, and excerpt
3. For the most relevant result, offer to open and read the full node

### `/memoria lint`

Verify cerebro wiki health.

**Checks:**
- `index.md` exists and has node entries
- `log.md` exists and is readable
- All nodes referenced in `index.md` exist as files
- `search.py` runs without errors
- FTS5 database is up to date

Output: PASS / WARN / FAIL with specific issues.

### `/memoria stats`

Show cerebro wiki statistics (delegates to `python search.py stats`).

## Session Node Template

```markdown
---
title: <What was worked on>
date: YYYY-MM-DD
area: <jarvis|ops|dev|design|personal>
tags: tag1, tag2, tag3
status: complete
---

## Summary

<2-3 sentence summary of what was accomplished>

## Key Decisions

- Decision 1: [what was decided and why]
- Decision 2: [what was decided and why]

## Files Modified

- `path/to/file.ts` — what changed
- `path/to/config.json` — what changed

## Lessons Learned

- What worked well
- What to avoid next time
- Non-obvious discoveries

## Next Steps

- [ ] Pending task 1
- [ ] Pending task 2
```
