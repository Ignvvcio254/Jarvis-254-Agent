#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

import jarvis_doctor
from jarvis_core.policy import recommend_workflow
from jarvis_core.providers import (
    build_provider_plan,
    configured_provider_order,
    detect_providers,
)
from jarvis_core.sessions import SessionStore
from jarvis_core.telemetry import log_metric


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _cmd_doctor(args: argparse.Namespace) -> int:
    return jarvis_doctor.run_checks(repo_only=args.repo_only)


def _cmd_providers(args: argparse.Namespace) -> int:
    statuses = detect_providers()
    plan = build_provider_plan(preferred=args.preferred)
    order = configured_provider_order()
    print("Providers")
    for item in statuses:
        state = "READY" if item.configured else "MISSING"
        print(f"- {item.name}: {state} ({item.env_var})")
    print(f"Priority order: {', '.join(order)}")
    print(f"Selected: {plan.selected or 'none'}")
    print(f"Reason: {plan.reason}")
    print(f"Fallback chain: {', '.join(plan.fallbacks) if plan.fallbacks else 'none'}")
    print(f"Unavailable: {', '.join(plan.unavailable) if plan.unavailable else 'none'}")
    return 0 if plan.selected else 1


def _cmd_session_start(args: argparse.Namespace) -> int:
    store = SessionStore(_repo_root())
    session_id = store.start(goal=args.goal, metadata={"owner": args.owner})
    print(f"Session started: {session_id}")
    return 0


def _cmd_session_end(args: argparse.Namespace) -> int:
    store = SessionStore(_repo_root())
    store.end(session_id=args.session_id, metadata={"status": args.status})
    print(f"Session ended: {args.session_id}")
    return 0


def _cmd_session_list(args: argparse.Namespace) -> int:
    store = SessionStore(_repo_root())
    rows = store.list_recent(limit=args.limit)
    if not rows:
        print("No sessions found.")
        return 0
    print("Recent sessions")
    for row in rows:
        goal = row.goal if row.goal else "-"
        print(f"- {row.timestamp} | {row.event:5s} | {row.id} | {goal}")
    return 0


def _cmd_plan(args: argparse.Namespace) -> int:
    plan = recommend_workflow(args.intent)
    print(f"Track: {plan['track']}")
    print("Commands:")
    for command in plan["commands"]:
        print(f"- {command}")
    print("Read first:")
    for path in plan["read_first"]:
        print(f"- {path}")
    print(f"Next: {plan['next']}")
    return 0


def _cmd_memory_index(args: argparse.Namespace) -> int:
    from cerebro.search import cmd_index

    cmd_index(verbose=args.verbose)
    return 0


def _cmd_memory_query(args: argparse.Namespace) -> int:
    from cerebro.search import cmd_query

    cmd_query(term=args.term, area=args.area, limit=args.limit)
    return 0


def _cmd_memory_stats(_args: argparse.Namespace) -> int:
    from cerebro.search import cmd_stats

    cmd_stats()
    return 0


def _cmd_curator(args: argparse.Namespace) -> int:
    """Lifecycle curation of skills/ — mark stale, archive old. Safe by default (dry-run)."""
    from jarvis_core.skill_curator import SkillCurator

    curator = SkillCurator(
        _repo_root(),
        stale_days=args.stale_days,
        archive_days=args.archive_days,
    )
    if args.status:
        breakdown = curator.status()
        for state, names in breakdown.items():
            if names:
                print(f"{state} ({len(names)}): {', '.join(names[:5])}{'…' if len(names) > 5 else ''}")
        return 0

    report = curator.run(dry_run=args.dry_run)
    print(report.summary())
    if args.verbose:
        for entry in report.entries:
            if entry.action != "keep":
                print(f"  [{entry.action}] {entry.skill} — {entry.reason}")
    return 0


def _cmd_memory_search(args: argparse.Namespace) -> int:
    """FTS5-powered BM25 search over cerebro/ nodes (jarvis_core.cerebro_index)."""
    from jarvis_core.cerebro_index import CerebroIndex

    idx = CerebroIndex(_repo_root())
    results = idx.search(args.query, limit=args.limit)
    if not results:
        print("No results found.")
        return 0
    for r in results:
        print(f"\n[{r.path}]")
        print(f"  {r.snippet}")
    stats = idx.stats()
    print(f"\n({stats['indexed']} nodes indexed, {stats['db_size_kb']} KB)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Jarvis runtime-lite CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_doctor = sub.add_parser("doctor", help="Run setup diagnostics")
    p_doctor.add_argument("--repo-only", action="store_true", help="Skip checks in $HOME")
    p_doctor.set_defaults(func=_cmd_doctor)

    p_providers = sub.add_parser("providers", help="Show provider readiness")
    p_providers.add_argument("--preferred", default="", help="Preferred provider name")
    p_providers.set_defaults(func=_cmd_providers)

    p_session = sub.add_parser("session", help="Session lifecycle helpers")
    p_session_sub = p_session.add_subparsers(dest="session_cmd", required=True)

    p_session_start = p_session_sub.add_parser("start", help="Start session")
    p_session_start.add_argument("--goal", required=True, help="Session goal")
    p_session_start.add_argument("--owner", default="user", help="Owner label")
    p_session_start.set_defaults(func=_cmd_session_start)

    p_session_end = p_session_sub.add_parser("end", help="End session")
    p_session_end.add_argument("--session-id", required=True, help="Session id")
    p_session_end.add_argument("--status", default="done", help="Completion status")
    p_session_end.set_defaults(func=_cmd_session_end)

    p_session_list = p_session_sub.add_parser("list", help="List recent session events")
    p_session_list.add_argument("--limit", type=int, default=20, help="Max rows")
    p_session_list.set_defaults(func=_cmd_session_list)

    p_plan = sub.add_parser("plan", help="Recommend what to do and when")
    p_plan.add_argument("--intent", required=True, help="User intent or task")
    p_plan.set_defaults(func=_cmd_plan)

    p_memory = sub.add_parser("memory", help="Memory index/query/stats")
    p_memory_sub = p_memory.add_subparsers(dest="memory_cmd", required=True)

    p_memory_index = p_memory_sub.add_parser("index", help="Index memory nodes")
    p_memory_index.add_argument("--verbose", action="store_true", help="Verbose indexing")
    p_memory_index.set_defaults(func=_cmd_memory_index)

    p_memory_query = p_memory_sub.add_parser("query", help="Query indexed memory")
    p_memory_query.add_argument("--term", required=True, help="Search term")
    p_memory_query.add_argument("--area", default="", help="Optional area filter")
    p_memory_query.add_argument("--limit", type=int, default=10, help="Max results")
    p_memory_query.set_defaults(func=_cmd_memory_query)

    p_memory_stats = p_memory_sub.add_parser("stats", help="Show memory index stats")
    p_memory_stats.set_defaults(func=_cmd_memory_stats)

    p_memory_search = p_memory_sub.add_parser("search", help="FTS5 BM25 search over cerebro/ nodes")
    p_memory_search.add_argument("query", help="Search query")
    p_memory_search.add_argument("--limit", type=int, default=10, help="Max results")
    p_memory_search.set_defaults(func=_cmd_memory_search)

    p_curator = sub.add_parser("curator", help="Skill lifecycle curation (stale/archive)")
    p_curator.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    p_curator.add_argument("--execute", dest="dry_run", action="store_false", help="Apply changes")
    p_curator.add_argument("--status", action="store_true", help="Show skill state breakdown")
    p_curator.add_argument("--stale-days", type=int, default=60, help="Days before marking stale")
    p_curator.add_argument("--archive-days", type=int, default=120, help="Days stale before archive")
    p_curator.add_argument("--verbose", action="store_true", help="Show all non-keep actions")
    p_curator.set_defaults(func=_cmd_curator)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = _repo_root()
    command_name = args.command
    status = "ok"
    try:
        exit_code = int(args.func(args))
        if exit_code != 0:
            status = "error"
        return exit_code
    except Exception as exc:  # noqa: BLE001
        status = "exception"
        raise
    finally:
        log_metric(repo_root, command=command_name, status=status)


if __name__ == "__main__":
    raise SystemExit(main())
