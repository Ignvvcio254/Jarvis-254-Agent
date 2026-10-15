---
name: bucle-agentico
description: "Agentic loop: execute complex features in phases, mapping the real context BEFORE each phase. The key idea: DON'T generate every subtask up front — map context just in time and generate subtasks from the system's actual state. Activate when the task touches multiple coordinated files, needs DB + code + UI changes, has phases that depend on each other, or when an approved PRP must be implemented."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# BLUEPRINT mode of the agentic loop

> "Don't plan what you don't understand. Map the context, then plan."

BLUEPRINT mode is for complex systems built in phases with just-in-time context mapping.

---

## When to use

- The task needs several coordinated components
- It involves DB + code + UI changes
- It has phases that depend on each other
- You need to understand context before implementing
- A PRP was approved and must be executed

---

## The idea: just-in-time context mapping

### Traditional approach (BAD)

Receive the problem → generate ALL tasks and subtasks → execute linearly.
Problem: subtasks are generated from ASSUMPTIONS, not real context.

### BLUEPRINT approach (RIGHT)

```
Receive the problem → generate only PHASES (no subtasks)
    |
ENTER Phase 1 → MAP the real context
    |
GENERATE subtasks from REAL context → execute Phase 1
    |
ENTER Phase 2 → MAP context (including what Phase 1 built)
    |
GENERATE Phase 2 subtasks → execute → ... repeat ...
```

Each phase is planned with REAL information about the system's current state.

---

## The BLUEPRINT flow: 5 steps

### STEP 1: SPLIT INTO PHASES

- Understand the complete FINAL problem
- Break it into chronologically ordered PHASES
- Identify dependencies between phases
- DON'T generate subtasks yet
- Track the phases with the todo list

### STEP 2: ENTER PHASE N — MAP CONTEXT

BEFORE generating subtasks, explore:

**Codebase:** Which related files/components exist? Which patterns does the project use? What can be reused?

**System state:** What did earlier phases build? What can I assume exists? What constraints do I have?

AFTER mapping, generate specific subtasks and update the todo list.

### STEP 3: EXECUTE THE PHASE'S SUBTASKS

```
WHILE subtasks pending in the current phase:
  1. Mark the subtask in_progress
  2. Execute it
  3. Use tools as judgement dictates (playwright, build, grep, ...)
  4. Validate the result (verify-repair gate)
     - Error → SELF-HARDENING (step 3.5)
     - OK    → mark completed
  5. Next subtask
The phase is complete when every subtask is done.
```

### STEP 3.5: SELF-HARDENING (when something fails)

1. FIX the code
2. TEST that it works
3. DOCUMENT the learning:

```markdown
### [YYYY-MM-DD]: [Short title]
- **Error**: [What exactly failed]
- **Fix**: [How it was fixed]
- **Applies to**: [Where else this knowledge applies]
```

| Kind of error | Where to document |
|---------------|-------------------|
| Specific to this feature | Current PRP (Learnings section) |
| Applies to several features | The relevant skill in ~/.claude/skills/ |
| Applies to the WHOLE project | The project's CLAUDE.md |
| A general engineering law | The `field-lessons` skill |

Knowledge persists. The same error NEVER happens twice.

### STEP 4: MOVE TO THE NEXT PHASE

- Confirm the current phase is REALLY complete
- DON'T assume everything went as planned
- Back to STEP 2 with the next phase
- The context now INCLUDES what was built

### STEP 5: FINAL VALIDATION

- End-to-end testing of the whole system
- Visual validation if applicable (playwright)
- Confirm the ORIGINAL problem is solved
- Report to the user what was built, with the verification evidence

---

## Common mistakes

**Mistake 1: generating every subtask up front**
```
BAD:  Phase 1: DB schema → 10 detailed subtasks
      Phase 2: APIs → 8 subtasks (based on ASSUMPTIONS)

GOOD: Phase 1: DB schema (no subtasks)
      Phase 2: APIs (no subtasks)
      → Enter Phase 1 → MAP context → GENERATE subtasks → execute
      → Enter Phase 2 → MAP real context → GENERATE subtasks
```

**Mistake 2: not re-mapping context between phases**
```
BAD:  Phase 1 done → straight into executing Phase 2
GOOD: Phase 1 done → MAP Phase 2 context → generate subtasks → execute
```

---

## Per-phase checklist

Before marking a phase complete:
- [ ] Are all subtasks really finished?
- [ ] Does the functionality do what was expected (verified, not assumed)?
- [ ] Are errors documented (self-hardening)?

Before moving to the next phase:
- [ ] Did I map the updated context?
- [ ] Do the new subtasks account for what ALREADY exists?

---

## BLUEPRINT principles

1. Phases first, subtasks later — only generate subtasks when entering the phase
2. Mandatory mapping — always map the real context before generating subtasks
3. Live todo list — keep progress visible
4. Validation per phase — confirm each phase is complete before moving on
5. Cumulative context — each phase inherits the previous ones' context
6. Self-hardening — every error is documented so it doesn't repeat

---

*"Precision comes from mapping reality, not imagining the future."*
*"A system that hardens itself keeps getting harder to break."*
