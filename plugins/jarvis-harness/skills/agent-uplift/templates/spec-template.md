# SPEC COMPILER template — turn any request into a perfect one-shot

> Fill this template BEFORE dispatching. Replace everything in {{ }}; delete empty sections.

---

{{EXECUTION PREFIX — ALWAYS include it if the task edits/creates files:}}
EXECUTION INSTRUCTION: this task is complete ONLY when you write files with your tools. Do not describe plans. Read the minimum necessary and execute right away.

{{COUNTERMEASURES for the target model — copy the applicable ones from antipatterns/<model>.md}}

## Context (verified, not assumed)
- Project: {{what it is, stack, main constraint}}
- Already exists (verified by grep): {{exact functions/contracts with real names}}
- DO NOT touch: {{files/systems out of scope}}

## Task — numbered points (each with an observable criterion)
1. {{action}} → verified by: {{expected evidence: file, function, test, grep pattern}}
2. ...
{{max 6 points for a cheap tier; if more → decompose before dispatching}}

## Output contract
- Exact files to create/edit: {{list}}
- Forbidden: extra files, new dependencies, console.log, modifying tests.
- When done reply ONLY: {{"DONE" | summary max N lines mapping each point}}

---

## Compiler checklist (before dispatching)
- [ ] Every function/file name cited was verified by grep in the real code.
- [ ] Every numbered point has ONE verifiable piece of evidence (assert/grep/test).
- [ ] Size matches the tier (cheap: ≤6 points, ≤1 large file, "don't read whole files").
- [ ] Target model's countermeasures injected.
- [ ] Runner checks `edited`/existence of every deliverable.
