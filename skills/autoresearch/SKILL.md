---
name: autoresearch
description: "Self-optimization of skills using Karpathy binary eval loop + Hermes Agent Curator pattern. Activate with: /autoresearch <skill-name> (Mode A: Karpathy loop), /autoresearch curator (Mode B: skill inventory management). Also triggers when the user says 'optimize this skill', 'improve X skill', 'clean up skills', 'audit skills'."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Autoresearch — Self-Optimizing Skill System

> Two-mode skill optimization: Karpathy binary eval loop (iterative improvement) + Hermes Agent Curator (inventory management).

---

## Mode A — Karpathy Loop (Single Skill Optimization)

Trigger: `/autoresearch <skill-name>`

### Philosophy

Binary evaluations (yes/no), one change per iteration, git commit before mutating, strict budget cap.
Based on Andrej Karpathy's principle: small, measurable, reversible improvements beat big rewrites.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_iterations` | 30 | Hard cap on optimization rounds |
| `budget` | $5 | Token/cost budget — stop if exceeded |
| `eval_criteria` | 3–6 | Binary yes/no questions per output |
| `target_score` | 0.85 | Stop when 85%+ criteria pass |

### Loop Protocol

```
FOR iteration = 1 to max_iterations:

  1. ANALYZE
     - Read current skill file
     - Run N sample prompts through it
     - Note failure modes: vague triggers, missing steps, wrong tool calls

  2. HYPOTHESIZE
     - Form ONE hypothesis: "If I change X, criterion Y will improve"
     - Never change multiple things at once (confounds the signal)

  3. MUTATE
     - Edit ONLY the skill body — never change YAML frontmatter
     - Keep the change minimal and targeted
     - git add + git commit -m "autoresearch: iter-N — <hypothesis>"
     - Record commit hash

  4. GENERATE
     - Run 3–5 test prompts through the mutated skill
     - Capture outputs

  5. EVALUATE (binary)
     For each criterion:
       - "Does the output correctly identify the trigger?" YES/NO
       - "Are all required steps present?" YES/NO
       - "Is tool usage correct and minimal?" YES/NO
       - "Is the output concise (no padding)?" YES/NO
       - [additional criteria specific to skill domain]
     Calculate score = (YES count) / (total criteria)

  6. DECIDE
     IF score > previous_score:
       KEEP mutation, continue
     ELSE:
       git reset --hard HEAD~1
       Revert to previous version

  7. RECORD
     Append to TSV log:
     iteration \t score \t hypothesis \t commit_hash \t kept(yes/no)

  IF score >= target_score: STOP (success)
  IF budget_exceeded: STOP (budget)
  IF 3 consecutive iterations with no improvement: STOP (plateau)
```

### TSV Log Format

Location: `~/.claude/skills/_autoresearch/<skill-name>/log.tsv`

```tsv
iteration	score	hypothesis	commit_hash	kept	timestamp
1	0.60	"Add explicit trigger phrases"	abc1234	yes	2025-01-01T10:00:00Z
2	0.75	"Split step 3 into substeps"	def5678	yes	2025-01-01T10:05:00Z
3	0.70	"Add tool hierarchy"	ghi9012	no	2025-01-01T10:10:00Z
```

### Termination Report

```
## Autoresearch Complete — <skill-name>
Iterations: N/30
Final score: X.XX (target: 0.85)
Commits kept: N | Reverted: M
Budget used: ~$X.XX
Status: SUCCESS / PLATEAU / BUDGET_EXCEEDED

Key improvements made:
- [improvement 1]
- [improvement 2]
```

---

## Mode B — Curator (Skill Inventory Management)

Trigger: `/autoresearch curator`

### Philosophy

Skills go stale without maintenance. The curator automatically transitions skill status and proposes merges/archives — but NEVER deletes. Based on Hermes Agent's curator pattern.

### Inventory Protocol

```
1. INVENTORY
   Glob: ~/.claude/skills/*/SKILL.md
   For each skill:
   - Extract frontmatter: name, description, last_modified
   - Check git log for last commit touching the file
   - Calculate age in days since last modification

2. AUTO-TRANSITION
   IF age > 60 days AND status = active:
     → Transition to: stale
     → Add note to frontmatter: "stale_since: YYYY-MM-DD"

   IF age > 120 days AND status = stale:
     → Propose archive to user (never auto-archive)
     → If user approves: move to ~/.claude/skills/_archived/YYYY-MM-DD-<name>/

3. CLUSTER ANALYSIS (LLM)
   Group skills by semantic similarity:
   - Read descriptions of all active skills
   - Identify clusters with overlapping functionality
   - Flag potential merges: "skill-A and skill-B both do X"

4. MERGE PROPOSAL
   For each merge candidate:
   - Show overlap analysis
   - Propose: "Merge skill-A into skill-B? skill-A would be archived."
   - Wait for user approval before executing

5. REPORT
   Present to user:
   - Total skills: N active | M stale | K archived
   - Transition candidates: [list]
   - Merge candidates: [list]
   - Recommended actions: [prioritized list]
```

### Archive Structure

```
~/.claude/skills/_archived/
└── YYYY-MM-DD-<skill-name>/
    ├── SKILL.md          ← original skill, preserved exactly
    ├── ARCHIVE_NOTE.md   ← why it was archived, what replaced it
    └── original_path.txt ← where it came from
```

### Rules

- NEVER delete skills — only archive
- NEVER auto-archive — always get user approval
- Merges preserve the better skill, archive the weaker one
- Archived skills can be restored with: `cp ~/.claude/skills/_archived/<name>/SKILL.md ~/.claude/skills/<name>/SKILL.md`

---

## Safety Limits

- Mode A: max 30 iterations, $5 budget hard cap
- Mode A: only mutates skill body — YAML frontmatter is immutable
- Mode A: every mutation is committed before evaluation (easy rollback)
- Mode B: curator is read-only until user approves actions
- Both modes: log all operations to `~/.claude/cerebro/log.md`
