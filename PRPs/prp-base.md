# PRP system (Product Requirements Proposal)

> **Jarvis blueprints** — the human-AI contract before writing code

---

## What a PRP is

A PRP is the **blueprint of a feature**. It defines WHAT to build before a single line of code.

| Section | Purpose | Owner |
|---------|---------|-------|
| **Goal** | What gets built (end state) | Human defines |
| **Why** | Business value | Human defines |
| **What** | Behaviour + success criteria | Human + AI |
| **Context** | Docs, references, existing code | AI researches |
| **Blueprint** | Implementation phases (no subtasks) | AI generates |
| **Learnings** | Self-hardening — errors and fixes | AI updates |

---

## Workflow

```
1. Human: "I need [feature]"
2. AI: researches context and feasibility
3. AI: generates PRP-XXX-name.md from this template
4. Human: reviews and approves
5. AI: executes the blueprint phase by phase (/bucle-agentico skill)
6. AI: documents learnings in the PRP (self-hardening)
```

---

## Naming

- Files: `PRP-[NUMBER]-[kebab-description].md`
- States: `PENDING` → `APPROVED` → `IN PROGRESS` → `DONE`

---

# PRP TEMPLATE

```markdown
# PRP-XXX: [Title]

> **Status**: PENDING
> **Date**: YYYY-MM-DD
> **Project**: [name]

---

## Goal

[What gets built — desired end state in 1-2 sentences]

## Why

| Problem | Solution |
|---------|----------|
| [User pain] | [How this feature solves it] |

**Business value**: [Measurable impact — conversions, time, money]

## What

### Success criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

### Expected behaviour
[Description of the main flow — happy path]

---

## Context

### References
- `src/features/[existing]/` — pattern to follow

### Proposed architecture (feature-first)
src/features/[new-feature]/
├── components/
├── hooks/
├── services/
└── types/

### Data model (if applicable)
CREATE TABLE [table] (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
> Migrations are applied BEFORE merging; put the SQL in the PR body (field-lessons #18).

---

## Blueprint (assembly line)

> IMPORTANT: only define PHASES. Subtasks are generated when entering each phase
> with the /bucle-agentico skill (map context → generate subtasks → execute)

### Phase 1: [Name]
**Goal**: [What is achieved when this phase is complete]
**Validation**: [How to verify it is complete]

### Phase 2: [Name]
**Goal**: [What is achieved]
**Validation**: [How to verify]

### Phase N: Final validation
**Goal**: system working end to end
**Validation**:
- [ ] verify gate exits 0 (build, typecheck, lint, tests)
- [ ] Playwright screenshot confirms the UI
- [ ] Success criteria met, each with its evidence

---

## Learnings (self-hardening)

> This section GROWS with every error found during implementation.
> The same error NEVER happens twice.

### [YYYY-MM-DD]: [Learning title]
- **Error**: [What failed]
- **Fix**: [How it was fixed]
- **Applies to**: [Where else this knowledge applies]

---

## Gotchas

- [ ] [Gotcha 1]
- [ ] [Gotcha 2]

## Anti-patterns

- DON'T create new patterns when the existing ones work
- DON'T ignore TypeScript errors
- DON'T hard-code values

---

*PRP pending approval. No code has been modified.*
```
