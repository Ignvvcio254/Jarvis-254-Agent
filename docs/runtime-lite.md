# Runtime Lite Guide

`jarvis_runtime.py` is the executable layer that turns this repo from docs-only into an operational agent ecosystem.

## Why this exists

- Reduce setup friction for fresh clones.
- Add "know what to do and when" behavior through workflow recommendations.
- Add session lifecycle and basic telemetry.
- Keep everything portable and provider-agnostic.

## Commands

```bash
python jarvis_runtime.py doctor [--repo-only]
python jarvis_runtime.py providers [--preferred anthropic|openai|gemini]
python jarvis_runtime.py plan --intent "fix api timeout bug"
python jarvis_runtime.py session start --goal "ship onboarding flow"
python jarvis_runtime.py session list --limit 20
python jarvis_runtime.py session end --session-id <id> --status done
python jarvis_runtime.py memory index
python jarvis_runtime.py memory query --term "PRP"
python jarvis_runtime.py memory stats
```

## Files written at runtime

- `cerebro/runtime_sessions.jsonl` - session start/end events.
- `cerebro/runtime_metrics.jsonl` - command-level telemetry.
- `cerebro/cerebro.db` - FTS index for memory search.

These are generated and ignored by git.

## Provider strategy

- The runtime checks env keys only (no vendor lock-in in code path).
- Supported keys:
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY`
- Selection behavior:
  - Use preferred provider when configured.
  - Otherwise, first configured provider in priority order.
- Optional order override:
  - `JARVIS_PROVIDER_ORDER="openai,anthropic,gemini"`
  - Invalid names are ignored, duplicates are removed.
- `providers` output includes:
  - selected provider,
  - fallback chain (configured alternatives),
  - unavailable providers,
  - reason for selection.

## Design limits (intentional)

- No hard dependency on external SDKs for bootstrap checks.
- No credential storage in repository files.
- No automatic user-specific file mutation beyond runtime logs in `cerebro/`.
