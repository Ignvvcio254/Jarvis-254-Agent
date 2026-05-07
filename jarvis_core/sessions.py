from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SessionEvent:
    id: str
    event: str
    goal: str
    timestamp: str
    metadata: dict[str, str]


class SessionStore:
    def __init__(self, repo_root: Path) -> None:
        self.file_path = repo_root / "cerebro" / "runtime_sessions.jsonl"

    def append(self, event: SessionEvent) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(event), ensure_ascii=True) + "\n")

    def start(self, goal: str, metadata: dict[str, str] | None = None) -> str:
        session_id = str(uuid.uuid4())
        self.append(
            SessionEvent(
                id=session_id,
                event="start",
                goal=goal,
                timestamp=_utc_now(),
                metadata=metadata or {},
            )
        )
        return session_id

    def end(self, session_id: str, metadata: dict[str, str] | None = None) -> None:
        self.append(
            SessionEvent(
                id=session_id,
                event="end",
                goal="",
                timestamp=_utc_now(),
                metadata=metadata or {},
            )
        )

    def list_recent(self, limit: int = 20) -> list[SessionEvent]:
        if not self.file_path.exists():
            return []
        rows: list[SessionEvent] = []
        with self.file_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                rows.append(
                    SessionEvent(
                        id=obj.get("id", ""),
                        event=obj.get("event", ""),
                        goal=obj.get("goal", ""),
                        timestamp=obj.get("timestamp", ""),
                        metadata=obj.get("metadata", {}),
                    )
                )
        return rows[-limit:]
