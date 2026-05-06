#!/usr/bin/env python3
"""FTS5 SQLite BM25 search for Jarvis cerebro wiki — inspired by Hermes Agent memory layer."""
import sqlite3, os, sys, re, json
from pathlib import Path
from datetime import datetime, timezone

CEREBRO_DIR = Path(__file__).parent
DB_PATH = CEREBRO_DIR / "cerebro.db"
SESSIONS_DIR = CEREBRO_DIR / "sessions"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DATE_FROM_FILENAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS nodes USING fts5(
            node_id,
            title,
            area,
            tags,
            date,
            body,
            tokenize='porter unicode61'
        );
        CREATE TABLE IF NOT EXISTS nodes_meta (
            node_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            indexed_at TEXT NOT NULL
        );
    """)
    conn.commit()

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    body = text[m.end():]
    return fm, body


def _node_id_from_path(path: Path) -> str:
    return path.stem


def _date_from_path(path: Path) -> str:
    m = DATE_FROM_FILENAME_RE.search(path.stem)
    return m.group(1) if m else ""


def cmd_index(verbose: bool = False) -> None:
    """Index all markdown nodes in cerebro/ into FTS5 database."""
    conn = _get_db()
    _init_schema(conn)

    md_files: list[Path] = list(CEREBRO_DIR.glob("*.md"))
    if SESSIONS_DIR.exists():
        md_files.extend(SESSIONS_DIR.glob("*.md"))

    now_iso = datetime.now(timezone.utc).isoformat()
    indexed = 0
    skipped = 0

    for path in md_files:
        if path.name in ("index.md", "sources.md"):
            continue
        node_id = _node_id_from_path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            skipped += 1
            continue

        fm, body = _parse_frontmatter(text)
        title = fm.get("title", path.stem.replace("-", " ").title())
        area = fm.get("area", "")
        tags = fm.get("tags", "")
        date = fm.get("date", _date_from_path(path))

        conn.execute("DELETE FROM nodes WHERE node_id = ?", (node_id,))
        conn.execute(
            "INSERT INTO nodes(node_id, title, area, tags, date, body) VALUES (?,?,?,?,?,?)",
            (node_id, title, area, tags, date, body.strip()),
        )
        conn.execute(
            "INSERT OR REPLACE INTO nodes_meta(node_id, file_path, indexed_at) VALUES (?,?,?)",
            (node_id, str(path), now_iso),
        )
        indexed += 1
        if verbose:
            print(f"  ✓ {node_id}")

    conn.commit()
    conn.close()
    print(f"cerebro/search: indexed {indexed} nodes ({skipped} skipped) → {DB_PATH.name}")


def cmd_query(term: str, area: str = "", limit: int = 10) -> None:
    """Full-text search with BM25 ranking and snippet excerpts."""
    if not DB_PATH.exists():
        print("No index found. Run: python search.py index")
        sys.exit(1)

    conn = _get_db()
    _init_schema(conn)

    escaped = term.replace('"', '""')
    if area:
        sql = """
            SELECT node_id, title, area, date,
                   snippet(nodes, 5, '»', '«', '…', 32) AS excerpt,
                   rank
            FROM nodes
            WHERE nodes MATCH ? AND area = ?
            ORDER BY rank
            LIMIT ?
        """
        rows = conn.execute(sql, (f'"{escaped}"', area, limit)).fetchall()
    else:
        sql = """
            SELECT node_id, title, area, date,
                   snippet(nodes, 5, '»', '«', '…', 32) AS excerpt,
                   rank
            FROM nodes
            WHERE nodes MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        rows = conn.execute(sql, (f'"{escaped}"', limit)).fetchall()

    conn.close()

    if not rows:
        print(f"No results for: {term}")
        return

    print(f"\n🔍 Results for \"{term}\"{f' [{area}]' if area else ''} — {len(rows)} found\n")
    for r in rows:
        date_str = f" ({r['date']})" if r['date'] else ""
        area_str = f" [{r['area']}]" if r['area'] else ""
        print(f"  📄 {r['title']}{area_str}{date_str}")
        print(f"     {r['excerpt']}")
        print(f"     → {r['node_id']}\n")


def cmd_stats() -> None:
    """Show index statistics."""
    if not DB_PATH.exists():
        print("No index found. Run: python search.py index")
        return

    conn = _get_db()
    _init_schema(conn)

    total = conn.execute("SELECT COUNT(*) FROM nodes_meta").fetchone()[0]
    areas = conn.execute(
        "SELECT area, COUNT(*) as n FROM nodes WHERE area != '' GROUP BY area ORDER BY n DESC"
    ).fetchall()
    last = conn.execute("SELECT MAX(indexed_at) FROM nodes_meta").fetchone()[0]

    conn.close()

    print(f"\n📊 cerebro index stats")
    print(f"   Nodes indexed : {total}")
    print(f"   DB path       : {DB_PATH}")
    print(f"   Last indexed  : {last or 'never'}\n")
    if areas:
        print("   Areas:")
        for row in areas:
            print(f"     {row['area']:12s} {row['n']} nodes")
    print()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage:")
        print("  python search.py index              — index all cerebro nodes")
        print("  python search.py query <term>       — full-text BM25 search")
        print("  python search.py query <term> --area <area>")
        print("  python search.py stats              — show index info")
        return

    cmd = args[0]

    if cmd == "index":
        cmd_index(verbose="--verbose" in args or "-v" in args)
    elif cmd == "query":
        if len(args) < 2:
            print("Error: query requires a search term")
            sys.exit(1)
        term = args[1]
        area = ""
        if "--area" in args:
            idx = args.index("--area")
            if idx + 1 < len(args):
                area = args[idx + 1]
        cmd_query(term, area=area)
    elif cmd == "stats":
        cmd_stats()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
