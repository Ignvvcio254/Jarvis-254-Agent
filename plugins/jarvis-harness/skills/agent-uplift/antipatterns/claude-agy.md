# Anti-patterns · Claude Sonnet/Opus via another CLI in headless `-p` mode

- [2026-06-09] · Skips points of multi-point specs without saying so (5/6 delivered) · implicit prioritisation on long tasks · **COUNTERMEASURE:** "Before finishing, re-read points 1..N of the spec and check that EACH ONE has code written. If you skip any, say so explicitly in the summary."
- [2026-06-09] · Exits `-p` with code 0 after only READING (answers with a plan, doesn't execute; 3 times in a row) · print mode accepts a text answer as final · **COUNTERMEASURE (mandatory prefix):** "EXECUTION INSTRUCTION: this task is complete ONLY when you write code with your editing tools. Do not describe plans. Read the minimum and edit right away." + an `edited` check in the runner.
- [2026-06-10] · Silent degradation from a per-model-line quota (fast exit 0, no activity) · quotas are separate per model line · **COUNTERMEASURE:** switch model line in the CLI settings; smoke-test before critical phases.
