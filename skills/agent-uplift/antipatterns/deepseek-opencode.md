# Anti-patterns · deepseek flash free tier (OpenCode)

- [2026-06-10] · Extreme latency on the free tier (>15 min on a benchmark case a small model solves in ~2 min) · free-tier queueing/throttling · **ROUTER COUNTERMEASURE:** don't assign it critical-path or interactive tasks; only overnight batches or work without a deadline. Confirm with a benchmark score before discarding it (it may be slow but correct).
