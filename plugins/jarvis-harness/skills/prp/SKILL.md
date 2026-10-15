---
name: prp
description: "Plan a complex feature before implementing it. Generates a PRP (Product Requirements Proposal) with goal, expected behaviour, data model and implementation phases. Activate ALWAYS before bucle-agentico, when the task involves multiple coordinated files/phases, or when the user says: plan this, give me a plan, I want to add something big, I need a system for X, blueprint this."
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Skill: Generate a PRP (Product Requirements Proposal)

> Generate a PRP for: $ARGUMENTS

---

## What a PRP is

A PRP is the **blueprint of a piece of software**. It defines WHAT to build before a single line of code.

It is the human-AI contract. The human defines the goal and the why. The agent researches the context,
proposes the architecture and generates the phase plan. Together they validate before executing.

**Without a PRP**: vibe coding, spaghetti code, features that don't fit.
**With a PRP**: clear architecture, defined phases, learnings that persist (self-hardening).

---

## Process

### Step 1: Read the base template

```
~/.claude/PRPs/prp-base.md   (or PRPs/prp-base.md in the Jarvis repo)
```

### Step 2: Interview if context is missing

If `$ARGUMENTS` lacks detail, ask directly:

1. **Goal**: What do you want to build? (end state in 1-2 sentences)
2. **Why**: What problem does it solve? What's the value?
3. **Success criteria**: How do you know it's done? (3-5 measurable checkboxes)
4. **Constraints**: Anything it must NOT do, or a critical dependency?

Don't ask all 4 if the user already gave enough context.

### Step 3: Research the codebase

Before writing the PRP:
- **Grep/Glob**: find existing code related to the feature
- **Read**: read relevant files to understand current patterns
- Look for similar features already implemented to reuse their patterns

### Step 4: Generate the PRP

Create the PRP following `prp-base.md`:

**File name**: `.claude/PRPs/PRP-XXX-{feature-name}.md` — `XXX` sequential, `{feature-name}` in kebab-case.

**Mandatory content**:
- Goal (1-2 sentences)
- Why (problem/solution table + value)
- Success criteria (measurable checkboxes)
- Expected behaviour (happy path)
- Context (references, proposed architecture, data model if applicable)
- Blueprint (ONLY phases, no subtasks — bucle-agentico generates those)
- Empty sections for Learnings, Gotchas, Anti-patterns

### Step 5: Present it to the user

Summarise: goal, number of phases, key architecture decisions — and ask whether to adjust before approving.

**Implement NOTHING yet.** The PRP must be approved before executing.

---

## After the PRP

Once approved, implementation runs with `/bucle-agentico`, which uses the PRP as its guide, phase by phase with
just-in-time context mapping. For work spanning several sessions, turn the success criteria into a
`long-run-harness` feature list.

Learnings discovered during implementation are written back into the PRP (Learnings section) — **active
self-hardening**.

---

## Rules

- ALWAYS read `prp-base.md` before generating
- NEVER generate subtasks inside the phases (bucle-agentico does that)
- NEVER implement code in this skill (only the document)
- ALWAYS research the codebase before proposing architecture
- The PRP is created in `PENDING` state until the user approves
- PRPs live in `.claude/PRPs/` inside the current project
