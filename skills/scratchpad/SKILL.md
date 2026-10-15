---
name: scratchpad
description: The agent's working memory — its own notes during long tasks + detection of user corrections + propagation to the right memory layer. Fixes fragmentation (knowledge that lives in only one place). Activate on multi-phase tasks, when the user corrects you, or when closing a significant session.
---

# scratchpad — Own notes + correction detection + propagation

> Jarvis harness. Replicates the "improves its outputs using its own notes" capability (a reported 3× gain)
> and ports correction detection from prax-agent. Fixes memory fragmentation at the root.

## The three functions

### 1. Task scratchpad (own notes during long work)

On every multi-phase task keep a living notes file at `.scratch/task.md` in the project. It is not for the
user — it is the agent's working memory.

What to record (append, never rewrite):
- Decisions taken and why
- What was tried and failed (so it isn't repeated in the same task)
- Current state: what's done, what's left
- Context findings (key files, project patterns)

Why: on long tasks the model re-derives context it already knew → wastes tokens and makes mistakes. Re-reading
its own notes avoids both. When resuming after an interruption, read `.scratch/task.md` FIRST (the
`session_boot` hook injects it automatically).

### 2. Correction detection (when the user corrects you)

Triggers — the user says something like:
- "no, actually…", "that's wrong", "not like that", "you got it wrong"
- "I already told you…", "the same thing again", "remember that…"
- "don't do X", "always do Y", "I prefer Z"
- corrects an output, reverts something, repeats an earlier instruction

(The `correction_detector` hook flags these in English and Spanish.)

On a correction:
1. Extract the **problem → solution** pattern (what I did wrong, what I should have done)
2. Classify its scope (table below) and save it in the right layer
3. Confirm briefly, in the user's language: "Noted: [rule]."

NEVER leave a correction only in the conversation. Conversation = dead knowledge.

### 3. Propagation (the fix for fragmentation)

Each kind of knowledge has ONE home layer. Don't write everywhere; write to the right one:

| Kind of knowledge | Home layer | How |
|---|---|---|
| Working notes of the current task | `.scratch/task.md` | append |
| Behaviour correction (how to work) | auto-memory, type `feedback` | new memory + index line |
| Anti-pattern of a model/worker | `agent-uplift/antipatterns/` | append to that model's file |
| Decision/output of a significant session | `cerebro/` via `/memoria ingest` | session node + index |
| Durable entity/relation (system, skill, project) | knowledge-graph MCP, if installed | entities + relations |
| Project fact not derivable from the code | auto-memory, type `project` | new memory + index line |
| An engineering law learned the hard way | `field-lessons` skill | one law + one-line incident |

Golden rule: **when closing a significant session, walk the matrix** and make sure every new piece of knowledge
reached its home layer.

## Degradation

If a memory MCP is down → write to the file layers (`.scratch`, auto-memory, `cerebro/`), which never fail.
Never block on a dead MCP. Note in the session node which layer is pending.

## Integration with verify-repair

The scratchpad records the [[verify-repair]] result per task: model level used ([[token-router]]), first-try
gate pass, number of repair attempts. That feeds the economy metric (tokens per successful task) and the
anti-patterns (a model repeatedly failing the same check → anti-pattern).

## Verifying this skill

- Create `.scratch/task.md`, append 2 notes, confirm they persist and `session_boot` injects them next session.
- Simulate a correction → check a `feedback` memory is created and indexed.

## Related

Closes the harness with [[verify-repair]] and [[token-router]]. Its output feeds `agent-uplift` (anti-patterns)
and `jarvis-evolve` (self-improvement). Uses the existing `/memoria` system for the cerebro layer.
