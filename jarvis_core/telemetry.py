from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


def log_metric(repo_root: Path, command: str, status: str, details: dict[str, str] | None = None) -> None:
    metrics_path = repo_root / "cerebro" / "runtime_metrics.jsonl"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "status": status,
        "details": details or {},
    }
    with metrics_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")
