---
name: prp
description: "Generate PRPs (Product Requirements Proposals) before implementing complex features. Activate with: /prp <feature-description> — or when the user says 'plan this', 'give me a plan', 'before we code this', 'create a blueprint'. DO NOT implement — only generate the planning document."
allowed-tools: Read, Write, Glob, Grep, Bash
---

# PRP — Product Requirements Proposal Generator

> Blueprint-first engineering. Generate a structured plan before touching any code.
> PRPs live in `.claude/PRPs/` of the active project.

---

## When to Generate a PRP

Use this skill when the task:
- Touches multiple files in a coordinated way
- Requires changes in DB + code + UI
- Has phases that depend on each other
- Is a significant new feature (not a small bug fix)
- The user explicitly requests a plan

---

## Protocol

### Step 1 — Context Gathering

```
1. Read the user's description carefully
2. If context is insufficient, ask clarifying questions:
   - "What is the expected user-facing behavior?"
   - "Are there existing patterns in the codebase to follow?"
   - "What is the acceptance criteria?"
   - "Any hard constraints (performance, backwards compat, deadline)?"
3. Do NOT start generating until you have enough context
```

### Step 2 — Codebase Research

```
Before writing the PRP, research the actual codebase:
- Glob: find relevant files (components, routes, schemas, tests)
- Grep: find existing patterns for similar features
- Read: key files that the feature will touch or extend
- Identify: tech stack, naming conventions, existing abstractions

This research shapes the Blueprint section — the PRP must reflect
REAL codebase structure, not generic patterns.
```

### Step 3 — Generate PRP File

**File naming:** `.claude/PRPs/PRP-XXX-<feature-slug>.md`
(XXX = next sequential number, padded to 3 digits)

**Template:**

```markdown
---
id: PRP-XXX
title: <Feature Title>
status: PENDING
created: YYYY-MM-DD
author: {{YOUR_NAME}}
area: <frontend | backend | fullstack | infra | data>
---

# PRP-XXX — <Feature Title>

## Objective

One paragraph. What is being built and why.

## Why

- Business/product reason this matters
- What problem it solves for the user
- What happens if we don't build it

## Success Criteria

- [ ] Criterion 1 (measurable, binary)
- [ ] Criterion 2
- [ ] Criterion 3

## Expected Behavior

Describe the feature from the user's perspective. What does it do?
Include edge cases and error states.

## Context

### Relevant Files
- `path/to/file.ts` — description of what it does and why it's relevant
- `path/to/schema.sql` — existing schema this feature extends

### Existing Patterns
- How similar features are implemented in this codebase
- Naming conventions to follow
- Libraries already available

### Constraints
- Performance requirements
- Backwards compatibility requirements
- Platform/browser constraints

## Blueprint

### Phase 1 — <Phase Name>
> Subtasks are generated just-in-time when entering this phase (not now)

**Goal:** What this phase delivers
**Output:** Concrete artifact (file, endpoint, schema, component)
**Depends on:** (none | Phase N)

### Phase 2 — <Phase Name>

**Goal:** ...
**Output:** ...
**Depends on:** Phase 1

### Phase 3 — <Phase Name>

**Goal:** ...
**Output:** ...
**Depends on:** Phase 2

## Learnings / Gotchas

> Populated during implementation — errors are documented here so they never repeat.

*(empty — filled during /bucle-agentico execution)*
```

### Step 4 — Present to User

```
After writing the file, present a summary:

"PRP-XXX created: .claude/PRPs/PRP-XXX-<slug>.md

Summary:
[2-3 sentence description of the plan]

Phases:
1. Phase 1 — <name>: <one-liner>
2. Phase 2 — <name>: <one-liner>
3. Phase 3 — <name>: <one-liner>

Next step:
When ready to implement, run: /bucle-agentico PRP-XXX"
```

---

## Rules

- **DO NOT implement** — the PRP skill only generates the document
- PRP starts as `status: PENDING` — it becomes `APROBADO` when the user approves
- Subtasks are NOT generated at PRP time — they are generated just-in-time in each phase
- Phases should be logical units of work, not individual file edits
- Learnings/Gotchas section must stay empty until implementation begins
- If a PRP already exists for the feature, UPDATE it instead of creating a duplicate

---

## PRP Status Lifecycle

```
PENDING     → User reviews the plan
APROBADO    → User approved, ready for /bucle-agentico
IN_PROGRESS → /bucle-agentico is executing
DONE        → All phases complete, all criteria met
CANCELLED   → Feature dropped
```
