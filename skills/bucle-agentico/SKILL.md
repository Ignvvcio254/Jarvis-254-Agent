---
name: bucle-agentico
description: "Execute complex features phase by phase with just-in-time context mapping. Activate with: /bucle-agentico <PRP-ID> — or when a PRP is approved and ready to implement. Key innovation: subtasks are NOT pre-generated — they are mapped just-in-time from real codebase context."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Bucle Agéntico — Phase-by-Phase Agentic Execution

> Just-in-time context mapping. Auto-blindaje on errors.
> Never generate all subtasks at the start — map context before each phase.

---

## Core Innovation

Traditional planning generates ALL subtasks upfront from imagination.
Bucle Agéntico generates subtasks AFTER reading what actually exists in the codebase.

```
WRONG:  Plan everything → Execute (subtasks are fictional)
RIGHT:  Enter phase → Read real code → Generate subtasks → Execute
```

This eliminates "hallucinated file paths" and "assumed patterns that don't exist."

---

## Activation

```
/bucle-agentico PRP-XXX
```

1. Read `.claude/PRPs/PRP-XXX-<name>.md`
2. Verify status is `APROBADO` (refuse if still `PENDING`)
3. Update status to `IN_PROGRESS`
4. Begin Phase 1

---

## Execution Flow

### For Each Phase N:

```
STEP 1 — ENTER PHASE
  Announce: "=== Phase N: <name> ==="
  Update PRP: mark phase as IN_PROGRESS

STEP 2 — MAP CONTEXT (just-in-time)
  - Glob: find files relevant to this phase
  - Grep: find existing patterns, imports, conventions
  - Read: key files that will be touched or extended
  - Answer: "What exists? What patterns do I follow? What did Phase N-1 create?"
  - Build a mental model of the REAL state, not assumed state

STEP 3 — GENERATE SUBTASKS
  Only now, based on real context:
  - List concrete subtasks (file edits, new files, commands)
  - Each subtask references REAL file paths found in Step 2
  - No imaginary abstractions — only what the codebase actually uses

STEP 4 — EXECUTE SUBTASKS
  Use TodoWrite to track subtask progress:
  - [ ] Subtask 1
  - [ ] Subtask 2
  - [ ] Subtask 3
  Execute one by one, marking complete as done.

STEP 5 — AUTO-BLINDAJE (on any error)
  IF error occurs:
    a. Fix the error
    b. Run the test/build/lint to confirm fix
    c. Document in PRP Learnings section:
       "### Error N — <short description>
        What happened: [error message]
        Root cause: [why it happened]
        Fix applied: [what was changed]
        Never repeat: [rule to prevent recurrence]"
    d. Continue execution — do NOT stop for non-blocking errors

STEP 6 — PHASE VALIDATION
  Run the validation defined for this phase:
  - Build passes? (npm run build / cargo build / etc.)
  - Tests pass? (npm test / pytest / etc.)
  - Manual check: does the phase output exist and work?

STEP 7 — TRANSITION
  Mark phase DONE in PRP
  Announce: "Phase N complete. Output: <artifact>"
  Move to Phase N+1 (repeat from STEP 1)
```

---

## Progress Tracking with TodoWrite

At the start of each phase, create a todo list:

```
Phase 2: API Endpoint
[ ] Read existing route patterns in src/routes/
[ ] Create src/routes/feature.ts following existing pattern
[ ] Add route to src/routes/index.ts
[ ] Write unit test in src/routes/feature.test.ts
[ ] Run npm test -- --grep feature
```

Each item checked off as it completes. Never mark a phase done with unchecked items.

---

## Auto-Blindaje Protocol

Auto-blindaje means: errors are learning opportunities, not blockers.

```
Error detected
    ↓
Diagnose root cause (read error, check context)
    ↓
Apply fix
    ↓
Verify fix works (run the failing command again)
    ↓
Document in PRP Learnings/Gotchas
    ↓
Continue execution
```

The same error must NEVER occur twice in the same project.
If an error recurs, the Learnings section was not read at phase start.

**Rule:** At the start of each phase, READ the Learnings/Gotchas section of the PRP.

---

## Final Validation (after last phase)

```
1. Run full test suite
2. Run build
3. Run lint/typecheck
4. Verify ALL success criteria from PRP are met (binary check each one)
5. Update PRP status: IN_PROGRESS → DONE
6. Report to user:

   "=== Bucle Agéntico Complete ==="
   PRP-XXX: <title>
   Phases completed: N/N
   Criteria met: N/N
   Errors encountered: M (all fixed, documented in Learnings)
   Final state: [what was built]
```

---

## Safety Limits

- Never mark a phase DONE without running its validation
- Never skip the context-mapping step (Step 2) — it prevents hallucinated paths
- Never generate subtasks before reading the actual codebase
- If a phase fails 3 times: STOP and report to user with full error context
- Irreversible operations (db drops, force push): always confirm with user first
