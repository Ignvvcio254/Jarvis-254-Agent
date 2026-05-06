---
name: goal
description: "Persistent objectives that guide agent behavior across sessions. Activate with: /goal <objective>, /goal list, /goal clear <id>, /goal done <id> — or when the user says 'remember that...', 'my goal is...', 'don't forget that...'. Goals persist in ~/.claude/goals.md between conversations."
allowed-tools: Read, Write, Edit, Glob
---

# Goal — Persistent Cross-Session Objectives

> Inspired by the `/goal` system of Hermes Agent (NousResearch).
> Goals persist between sessions and guide agent behavior without repeating them each time.

---

## Concept

A **goal** is an objective that:
1. Persists between sessions in `~/.claude/goals.md`
2. Is loaded at the start of each session alongside `cerebro/index.md`
3. Orients agent decisions without {{YOUR_NAME}} needing to repeat it
4. Has states: `active` / `paused` / `done` / `cleared`

**Difference from memory:**
- Memory = accumulated knowledge from the past
- Goal = objective that guides actions toward the future

---

## Persistence File

**Path:** `~/.claude/goals.md`

**Structure:**
```markdown
# Goals — Jarvis

## Active

### goal-001
- **Status:** active
- **Objective:** [goal description]
- **Progress:** [progress notes — updated each session]
- **Created:** YYYY-MM-DD HH:MM
- **Deadline:** YYYY-MM-DD (optional)

---

## Completed

### goal-000
- **Status:** done
- **Objective:** [description]
- **Completed:** YYYY-MM-DD HH:MM
- **Result:** [how it was achieved]
```

---

## Commands

### `/goal <objective>` — Create goal

```
1. Read ~/.claude/goals.md (create if it doesn't exist)
2. Generate ID: goal-XXX (next available number)
3. Add under ## Active with status: active
4. Respond: "Goal registered (goal-XXX): [objective]"
```

### `/goal list` — List goals

```
1. Read ~/.claude/goals.md
2. Show only status: active and paused
3. Format: ID | Status | Objective | Days active
```

### `/goal done <id>` — Complete goal

```
1. Locate goal by ID
2. Change status to: done
3. Add completion timestamp + brief result in "Result"
4. Move entry to ## Completed section
5. Celebrate briefly: "Goal completed: [objective]"
```

### `/goal pause <id> [reason]` — Pause goal

```
1. Change status to: paused
2. Add "Pause reason: [reason]"
3. The goal does not guide actions while paused
```

### `/goal clear <id>` — Clear goal

```
1. Change status to: cleared (NEVER delete — permanent audit trail)
2. The goal disappears from /goal list but remains in the file
```

---

## Automatic Integration in Sessions

**At the start of each session** (additional step to the CLAUDE.md protocol):

```
1. Check if ~/.claude/goals.md exists
2. If it exists → read goals with status: active
3. If there are active goals → show: "Active goals: [short list]"
4. Orient session actions toward the goals
```

**During the session:** If an architectural decision impacts an active goal → mention it.

---

## Example Usage

```
{{YOUR_NAME}}: /goal Reach 85% autonomous capability by June 2026

Agent: Goal registered (goal-001):
       "85% autonomous — deadline: 2026-06-30"
       I'll load this automatically each session and orient sprints toward it.
```

In the next session, without {{YOUR_NAME}} repeating it:
```
Agent: Active goal: "85% autonomous — 55 days remaining"
       Today's sprint advances toward: FTS5 cerebro + unified gateway (+7%)
```

---

## Safety Limits

- `~/.claude/goals.md` **is never deleted** — only status changes
- Goals with `pinned: true` are immune to automatic `/goal clear`
- Maximum 5 active goals simultaneously — if exceeded, suggest consolidating
- Do not create contradictory goals — check for conflicts before registering
