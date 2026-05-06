---
name: insights
description: "Generate activity reports and analytics from Jarvis sessions. Activate with: /insights, /insights --days 30, /insights --area jarvis — or when the user asks for 'stats', 'activity summary', 'what have we done', 'how much progress'. Inspired by Hermes Agent's analytics system."
allowed-tools: Read, Glob, Bash
---

# Insights — Session Analytics

> Read-only analytics over the cerebro wiki. Reports activity, areas worked, session patterns, and goal velocity.

---

## Commands

- `/insights` — Full report (last 30 days by default)
- `/insights --days N` — Report for last N days
- `/insights --area <area>` — Filter by area (jarvis, ops, dev, design, personal)

---

## Generation Protocol

### Step 1 — Gather Data

```
1. Read ~/.claude/cerebro/log.md
   - Parse entries: ## [YYYY-MM-DD HH:MM] operation | slug
   - Filter by requested day range

2. Glob ~/.claude/cerebro/sessions/*.md
   - Read frontmatter: title, area, date, tags, status

3. Read ~/.claude/cerebro/index.md
   - Extract: total nodes, active areas, last update

4. Read ~/.claude/goals.md (if exists)
   - Load active goals to compute progress
```

### Step 2 — Compute Metrics

| Metric | How to compute |
|--------|----------------|
| Total sessions | Count of files in sessions/ within period |
| Most active areas | Frequency of `area` in session frontmatter |
| Frequent tags | Top 10 tags across all sessions in period |
| Operations in log | Count by type: ingest, update, curator, lint |
| Active streak | Consecutive days with at least 1 session |
| Nodes created | Count of `ingest` operations in log.md |

### Step 3 — Generate Report

**Terminal format:**
```
## 📊 Insights — Last 30 days
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 Sessions: 12
📝 Cerebro nodes: 8 sessions
🗓️  Period: YYYY-MM-DD → YYYY-MM-DD

### Most active areas
1. jarvis    ████████████ 6 sessions (50%)
2. ops       ████████     4 sessions (33%)
3. dev       ████         2 sessions (17%)

### Operations in log
- ingest: 8 | update: 4 | curator: 0 | lint: 1

### Frequent tags
hermes-agent, jarvis, gsap, skills, memory

### Active goals
🎯 goal-001: "Ship v1.0 — 55 days remaining"
   Current progress: 63% | Velocity: ~0.5%/day ✅

### Current streak
🔥 3 consecutive active days
```

---

## Velocity Analysis

For each active goal with a deadline:
```
Goal: [goal text]
Current progress: X%
Days remaining: N
Required velocity: ~X% per day
Actual velocity (last 2 weeks): ~Y% per day
Status: ✅ on track / ⚠️ behind
```

## Proactive Suggestion

Always include at the end of the report:
```
💡 Highest impact next: [highest-value pending task from cerebro/sessions/]
```

---

## Limits

- Read-only — never modifies cerebro files
- If cerebro/ doesn't exist → "No session data yet. Use /memoria ingest to begin."
- For periods > 90 days, warn that data may be incomplete
