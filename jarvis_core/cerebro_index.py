"""FTS5-based index for cerebro/ wiki nodes.

Provides BM25 full-text search over all markdown files in cerebro/
using SQLite FTS5 — zero external dependencies beyond the stdlib.

Usage:
    from jarvis_core.cerebro_index import CerebroIndex

    idx = CerebroIndex(repo_root)
    idx.build()                          # index all nodes (or rebuild)
    results = idx.search("token budget") # ranked by BM25
    for r in results:
        print(r.path, r.snippet)
"""
from __future__ import annotations

import sqlite3
import textwrap
from dataclasses import dataclass
from pathlib import Path

_DB_NAME = "cerebro/cerebro_fts.db"
_SKIP_FILES = {"cerebro_fts.db"}


@dataclass
class SearchResult:
    path: str
    snippet: str
    rank: float


class CerebroIndex:
    """SQLite FTS5 index over cerebro/ markdown nodes."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.cerebro_dir = self.repo_root / "cerebro"
        self.db_path = self.repo_root / _DB_NAME

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, force: bool = False) -> int:
        """Index all .md files in cerebro/. Returns count of indexed docs."""
        if force and self.db_path.exists():
            self.db_path.unlink()

        con = self._connect()
        self._ensure_schema(con)
        count = self._index_all(con)
        con.close()
        return count

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Full-text search with BM25 ranking. Returns up to `limit` results."""
        if not self.db_path.exists():
            self.build()

        con = self._connect()
        try:
            rows = con.execute(
                """
                SELECT path, snippet(cerebro_fts, 1, '[', ']', '…', 20), rank
                FROM cerebro_fts
                WHERE cerebro_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            con.close()
            return []

        con.close()
        return [SearchResult(path=r[0], snippet=r[1], rank=r[2]) for r in rows]

    def stats(self) -> dict:
        """Return index stats: doc count and db size."""
        if not self.db_path.exists():
            return {"indexed": 0, "db_size_kb": 0}
        con = self._connect()
        count = con.execute("SELECT COUNT(*) FROM cerebro_fts").fetchone()[0]
        con.close()
        return {
            "indexed": count,
            "db_size_kb": round(self.db_path.stat().st_size / 1024, 1),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _ensure_schema(self, con: sqlite3.Connection) -> None:
        con.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS cerebro_fts
            USING fts5(path, content, tokenize='porter unicode61')
            """
        )
        con.commit()

    def _index_all(self, con: sqlite3.Connection) -> int:
        if not self.cerebro_dir.exists():
            return 0

        md_files = [
            p for p in self.cerebro_dir.rglob("*.md")
            if p.name not in _SKIP_FILES
        ]

        con.execute("DELETE FROM cerebro_fts")
        rows = []
        for md in md_files:
            try:
                text = md.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = str(md.relative_to(self.repo_root))
            rows.append((rel, text))

        con.executemany("INSERT INTO cerebro_fts(path, content) VALUES (?, ?)", rows)
        con.commit()
        return len(rows)


# ------------------------------------------------------------------
# Context compressor — protect_first_n / protect_last_n contract
# (Adopted from NousResearch/hermes-agent context_engine.py pattern)
# ------------------------------------------------------------------

class ContextCompressor:
    """Minimal context compression following the Hermes protect_n contract.

    Rules:
      - protect_first_n: never compress the first N messages (system context).
      - protect_last_n:  never compress the last N messages (active context).
      - threshold:       only compress when usage >= threshold * max_tokens.

    Provider-agnostic — operates on plain string lists, calls no LLM itself.
    """

    def __init__(
        self,
        protect_first_n: int = 3,
        protect_last_n: int = 6,
        threshold: float = 0.75,
    ) -> None:
        self.protect_first_n = protect_first_n
        self.protect_last_n = protect_last_n
        self.threshold = threshold

    def should_compress(self, used_tokens: int, max_tokens: int) -> bool:
        return used_tokens / max_tokens >= self.threshold

    def compressible_range(self, messages: list) -> tuple[int, int]:
        """Return (start, end) indices of messages eligible for compression."""
        start = self.protect_first_n
        end = max(start, len(messages) - self.protect_last_n)
        return start, end

    def compress(self, messages: list, summarizer=None) -> list:
        """Return compressed message list. Middle messages get a placeholder
        summary unless `summarizer(messages) -> str` is provided."""
        start, end = self.compressible_range(messages)
        if end <= start:
            return messages

        middle = messages[start:end]
        if summarizer:
            summary_text = summarizer(middle)
        else:
            total = sum(len(str(m)) for m in middle)
            summary_text = (
                f"[{len(middle)} messages summarized — ~{total} chars of context]"
            )

        summary_msg = {"role": "system", "content": summary_text}
        return messages[:start] + [summary_msg] + messages[end:]

    def describe(self) -> str:
        return textwrap.dedent(f"""
            ContextCompressor
              protect_first_n : {self.protect_first_n}
              protect_last_n  : {self.protect_last_n}
              threshold       : {self.threshold * 100:.0f}% of context window
        """).strip()
