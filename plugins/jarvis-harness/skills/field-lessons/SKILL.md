---
name: field-lessons
description: Field-tested engineering laws distilled from real production incidents of an AI agent working 24/7 (verification, silent failures, deploys, migrations, hooks, security, diagnosis). Load BEFORE claiming something is done/verified/deployed, when debugging a "works but doesn't" symptom, writing guards/installers/fallbacks, merging PRs, applying DB migrations, or killing processes. Leyes de ingeniería aprendidas en incidentes reales.
---

# Field lessons — laws paid for with real incidents

Each law below exists because breaking it caused a real, costly failure. They are short on purpose:
read the law, check the trigger, apply the test.

## A. Verification — "done" means the system confirms it

1. **Verify the effect, not the configuration.** A hook in `settings.json`, a key in a `.env`, a row in a
   config table prove nothing. The proof is the observable effect: the audit-log line, the denied command,
   the HTTP body. *Incident:* a security hook was configured, documented and commented as active for weeks;
   nothing ever invoked it. Suspect every guard that has never written a log line.
2. **Verifying the mechanism is not verifying the cause.** When you test a conditional fix, also test where the
   flag comes from. *Incident:* a "quota exhausted" alert fired perfectly — on an account at 0% usage, because
   the detector regex matched the field *name* `rate_limit_event` in raw JSON.
3. **Never detect state with substrings over raw JSON.** Field names, UUIDs and timestamps match too. Parse it
   and read the field.
4. **A label you wrote is not a signal.** Writing `.active`, a profile name or an expiry proves you wrote a file,
   not that the system changed behaviour. Ask: *which signal of the real system confirms it?*
5. **Test both directions.** "Hidden rows don't show" and "visible rows do show". A broken filter on empty data
   and a correct filter look identical (zero rows).
6. **Verify as the real role.** DB editors run as the table owner and bypass RLS; check with `SET ROLE anon`
   (or the real service identity), never as admin.
7. **Verify where the service actually lives.** Testing from the repo folder reads the repo's `.env`; the
   deployed process may run elsewhere without that key. Reproduce in the deployed environment.
8. **A name is a statement of intent, not evidence.** Branch names, PR titles and commit messages are written
   before the work. Check the artifact.
9. **"Merged" ≠ "in main" ≠ "in production".** Stacked PRs can merge into an already-merged base and never
   reach main; production may serve an old deployment. Check `git ls-tree origin/main <path>` and look for a
   string unique to the change in the served bundle.
10. **"Closing" ≠ "closed".** Never announce someone else's task as finished without evidence.

## B. Silent failure — the most expensive bug class

11. **No silent fallback for required config.** A test phone number left as a default sent real customers'
    personal data to a stranger for weeks because the env var was never set. Missing config must fail loudly.
12. **Optimistic fallback = structural lie.** A function that returns `"Done."` when no result arrived made a
    voice agent confirm actions that never happened. Without a real result, say so.
13. **No mute rejection.** An `error` status with an empty result is undiagnosable and looks like a crash.
    Every rejection carries a human-readable reason and states that nothing was executed.
14. **Split-brain memory goes unnoticed.** Two processes reading/writing different embedding columns kept
    returning plausible-but-stale results for weeks. Add a probe that compares freshness across stores.
15. **A metric that worsens when the system improves teaches people to ignore alarms.** For every probe ask:
    what action does its colour trigger? If none, it is decoration.
16. **An agent without the tool must say "I can't", not "done".** Give it a real, verifiable capability or an
    explicit refusal path.

## C. Changes, deploys and data

17. **Signed fields are immutable.** Annotating a signed payload invalidated the signature and silently killed
    the very messages the rescue path was meant to save. Annotations travel outside the signed payload.
18. **Migrations go in before the merge.** Deploy happens on merge, manual migrations later: in that gap new
    code talks to the old schema and can take down the whole app. Put the SQL in the PR body, apply first.
19. **New code must tolerate the old schema** during rollout (feature-detect, degrade, don't crash the page).
20. **A PR merges the commits that exist at that moment.** If work continues on the branch after approval,
    open a new PR; otherwise the fix never ships and debugging gets poisoned.
21. **GRANT before policy.** Postgres checks table privileges before RLS; without the GRANT the policy never
    runs and the error (`42501`) never mentions RLS.
22. **Realtime "SUBSCRIBED" proves nothing.** Probe each table with a real insert while listening; a table not
    in the publication subscribes fine and never emits.
23. **Web SQL editors mangle long scripts** (single transaction, cut dollar-quotes, appended comments). Prefer
    `$fn$` delimiters, small batches, and the CLI/migrations tool.

## D. Tools, processes and environments

24. **Installers merge, never `if [ ! -f ] && cp`.** The conditional copy is a silent no-op the day the file
    already exists (it usually does).
25. **Kill by PID, never by image name.** `taskkill /IM node.exe` / `pkill node` killed hundreds of MCP servers
    mid-session.
26. **Access denied is not absence.** An empty listing from an unprivileged shell does not mean the folder is
    empty; re-check elevated before concluding (and before deleting anything).
27. **Pass non-ASCII text by stdin or UTF-8 end to end, never argv through a legacy console.** The corruption
    happens in the parent before your process starts; no decode can recover it.
28. **A summary log lists everything; it doesn't point at the failure.** Read the first error and its state
    handler, not the performance summary.
29. **A restriction plus a request that needs what it forbids = a loop.** If a sandboxed/plan-mode agent must
    produce an external effect, let the infrastructure perform the effect from the agent's final answer.
30. **Write guards by intent, not by mechanism.** "Never answer bots" also silenced the teammate bots; the
    intent was "never answer yourself" (compare against your own id).
31. **Docs in the repo describe the infrastructure on the day they were written.** Confirm live state before
    building an argument on a DEPLOY.md.
32. **Perceived latency is UX.** 3.5 s with no progress signal feels broken; acknowledge slow actions before
    starting them and show a live counter.
33. **Read the code before hyping or dismissing a tool.** Two confident verdicts without reading were both
    wrong; the third, after reading every file, was right.
34. **Confirm who operates the feature** (a human by hand or an automation) before designing it or warning about
    risks — it changes both.

## How to use this skill

- Before saying *done / verified / deployed / fixed*: walk section A and name the real signal you checked.
- When something "works but doesn't": walk section B first — the failure is usually silent, not absent.
- Before merging/deploying/migrating: section C. Before killing, deleting or installing: section D.
- When you learn a new law the hard way, add it here with the incident in one line. Knowledge that only lives
  in a conversation is dead knowledge.
