---
name: jarvis-evolve
description: Permanent self-improvement loop — audits signals (project logs, anti-patterns, memory, session failures, local skills, eval bench), diagnoses gaps, proposes improvements to the user, applies the approved ones and measures. Includes the "frontier-level reasoning through context" doctrine to lift any Claude model. Invoke when closing significant sessions, when an error repeats, or with /jarvis-evolve.
---

# JARVIS-EVOLVE — the agent that improves itself

## Doctrine: frontier-level reasoning through context

A model isn't improved by touching weights — it's lifted by **distilling knowledge into injectable documents**.
The reasoning of a good session doesn't die with the session: it's captured as reusable context, and any Claude
model (Haiku, Sonnet, Opus) that starts with that context reasons from that level in that domain.

The four distilleries (where each kind of knowledge is captured):

| Kind of knowledge | Destination | Consumed by |
|---|---|---|
| How to operate (verified protocols) | Core skills (`multi-cli`, `agent-uplift`, `field-lessons`, this one) | The agent in any session/model |
| What fails and its countermeasure | `agent-uplift/antipatterns/<model>.md` | The spec compiler → workers |
| Project decisions and state | Persistent memory + `cerebro/` + `workspace/LEARNINGS.md` | The agent when resuming |
| Identity and arbitration rules | `CLAUDE.md` (compact — it's a fixed cost per session) | Every session |

Golden rule: **knowledge that only lives in the conversation is dead knowledge.** If it was expensive to discover,
distil it before closing.

## The loop (6 steps)

1. **SENSE — collect signals.** Project logs (`LEARNINGS.md`), `antipatterns/`, project memory, repeated failures
   this session, `/eval-jarvis --report`, benchmark scores, friction (which task cost more than it should have?).
2. **DIAGNOSE — rank gaps by impact.** Missing skill? Skill out of date vs verified reality? Obsolete or missing
   CLAUDE.md rule? Anti-pattern without a countermeasure? Undistilled knowledge? Prioritise by frequency × cost.
3. **PROPOSE — to the user.** Compact table: gap · proposed improvement · file affected · risk. The user approves
   or declines (principle: propose, don't execute — unless self-improvement was explicitly authorised).
4. **APPLY — apply what was approved.** Surgical edits: core skills, CLAUDE.md (always COMPACT: every line is paid
   for in every session — prefer moving detail into skills and leaving pointers), templates, anti-patterns.
5. **MEASURE — check the improvement improves.** The next task of the same kind must show the effect (fewer
   retries, cleaner review, higher bench score). No measurable effect after 2 uses → revert or reformulate.
6. **RECORD — distil.** Persistent memory (and your config backup/sync, if you keep one). Bump CLAUDE.md's version
   on rule changes.

## Curating a large skill library

- Keyword discovery BEFORE coding; evolve closes the loop:
- **Repeated failure with no skill covering it** → catalogue gap → look in the community (`npx skills find`) or
  write your own (PROPOSE).
- **A skill that contradicts verified reality** → note it in memory as unreliable for that case; the verified
  truth goes into the core.
- **Never delete** third-party skills you might need: archive, don't destroy optionality — but don't install
  what you don't use either (each description costs context every session; see `install.py --skills`).
- CORE skills (multi-cli, agent-uplift, bucle-agentico, prp, field-lessons, jarvis-evolve) get active maintenance:
  every session that hits friction with them should leave at least one improvement candidate.

## Triggers

- Closing a significant session (together with `/memoria ingest`).
- The same error twice in any context.
- The user asks to raise capability ("make it better", "improve yourself").
- The eval bench or a benchmark shows a regression.

## Invariants (never self-modified)

Respectful address of the user · security > accessibility > correctness > aesthetics > performance · confirmation
before destructive actions · propose-before-executing for identity/rule changes · agent-uplift's ethical limits.
