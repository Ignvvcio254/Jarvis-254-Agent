---
name: background
description: "Run prompts asynchronously while the conversation continues without interruption. Activate with: /background <prompt>, /bg <prompt>, /btw <prompt> — or when the user says 'run this in parallel', 'do it in the background', 'don't block me'. Do NOT use for tasks that require user confirmation before continuing."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# Background — Non-Blocking Async Tasks

> Inspired by the `/background` system of Hermes Agent (NousResearch).
> Launch subtasks while the main conversation continues without interruption.

---

## When to Use

| Situation | Use background |
|-----------|---------------|
| Long build (> 30 seconds) | Yes |
| Web crawl / fetch multiple URLs | Yes |
| Heavy report generation | Yes |
| Indexing / search across large codebase | Yes |
| Simple task < 5 seconds | No — run directly |
| Task that requires user confirmation | No — run interactively |

---

## Execution Protocol

### Activation

Trigger phrases:
- `/background <prompt>` — launch immediately
- `/bg <prompt>` — short alias
- `/btw <prompt>` — "by the way, do this while..."
- "run this in the background", "execute this in parallel", "don't block me with this"

### Step 1 — Acknowledge Immediately

Before launching the task, respond:
```
Launching in background: [short description]
Continue the conversation — I'll notify you when it's done.
```

### Step 2 — Launch Subtask

Use the `Agent` tool with `run_in_background: true`:

```
Agent({
  description: "Background: [description]",
  prompt: "[complete prompt with all context needed — worker starts cold]",
  run_in_background: true
})
```

**Critical rule:** The worker has no conversation context. The prompt must be completely self-contained:
- Include absolute file paths
- Include the expected final output
- Include relevant constraints (don't delete, don't push, etc.)

### Step 3 — Continue Main Conversation

After launching, continue responding to the user normally. Do not block waiting for results.

### Step 4 — Notify on Completion

When the background Agent completes, the notification arrives automatically. Then:
- Send a new reply: "Background task complete: [description]\n\n[summary of results]"
- If the result is long, attach as a `.md` file

---

## /queue — Prompt Queue

`/queue <prompt>` or `/q <prompt>`: Enqueue a prompt to run on the **next turn**, without interrupting the current turn.

**Use:** When the user wants to add a task to run after the current one finishes.

**Implementation:** Save the prompt as a note at the end of the current response:
```
[QUEUE: {prompt}]
At the start of the next turn, execute this prompt before responding to the new message.
```

---

## /steer — Mid-Conversation Injection

`/steer <message>`: Adjust the agent's direction after the next tool call, without interrupting the current flow.

**Use:** When the user wants to correct direction without stopping execution in progress.

**Implementation:** After completing the tool call in progress, insert the steer message as additional context before generating the next response.

---

## Safety Limits

- **Never** run destructive tasks in background (delete, force-push, drop table)
- **Always** include complete context in the worker prompt — it starts cold
- **Maximum 3 background tasks simultaneously**
- If the worker fails → notify with the error, never silently fail
- Log to `~/.claude/cerebro/log.md`: `[date] background: [description] — [OK/FAIL]`
