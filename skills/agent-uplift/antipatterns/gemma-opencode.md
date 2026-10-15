# Anti-patterns · gemma (OpenCode default)

- [2026-06-09] · Ends the session without writing the deliverable on tasks over large files (>50 KB) · context exhausted reading the whole file · **COUNTERMEASURE:** "DO NOT read whole files: use targeted searches (grep) and read only the sections you need. Write the deliverable BEFORE any further analysis." + split the task if it touches >1 large file. Rescue: `opencode run -c "Finish now: <deliverable>"`.
