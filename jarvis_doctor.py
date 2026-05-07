#!/usr/bin/env python3
"""Jarvis Doctor: quick health checks for portable setup.

Usage:
  python jarvis_doctor.py
  python jarvis_doctor.py --repo-only
"""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path


REPO_REQUIRED = [
    "CLAUDE.md",
    "README.md",
    "INSTALL.md",
    "CHANGELOG.md",
    "docs/commands.md",
    "docs/command-skill-matrix.md",
    "docs/rules-guide.md",
    "docs/saas-factory.md",
    "docs/sanitization.md",
    "cerebro/index.md",
    "cerebro/log.md",
    "cerebro/sources.md",
    "commands/memoria.md",
    "commands/consumo.md",
    "PRPs/prp-base.md",
]

HOME_REQUIRED = [
    ".claude/CLAUDE.md",
    ".claude/commands",
    ".claude/skills",
    ".claude/cerebro/index.md",
]


def check_path(base: Path, relative_path: str) -> tuple[bool, str]:
    target = base / relative_path
    return target.exists(), str(target)


def print_check(ok: bool, label: str, path: str) -> None:
    status = "OK" if ok else "MISSING"
    print(f"[{status}] {label}: {path}")


def run_repo_checks(repo_root: Path) -> int:
    print("== Repository Checks ==")
    missing = 0
    for rel in REPO_REQUIRED:
        ok, path = check_path(repo_root, rel)
        print_check(ok, rel, path)
        if not ok:
            missing += 1
    return missing


def run_home_checks() -> int:
    print("== Local Home Checks ==")
    home = Path.home()
    missing = 0
    for rel in HOME_REQUIRED:
        ok, path = check_path(home, rel)
        print_check(ok, rel, path)
        if not ok:
            missing += 1
    return missing


def print_runtime_info() -> None:
    print("== Runtime ==")
    print(f"Python: {platform.python_version()}")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Executable: {sys.executable}")


def run_checks(repo_only: bool = False) -> int:
    repo_root = Path(__file__).resolve().parent
    print("Jarvis Doctor")
    print(f"Repo root: {repo_root}")
    print_runtime_info()

    missing_total = 0
    missing_total += run_repo_checks(repo_root)

    if not repo_only:
        missing_total += run_home_checks()

    print("== Summary ==")
    if missing_total == 0:
        print("All checks passed.")
        return 0

    print(f"Detected {missing_total} missing item(s).")
    print("Recommendation: re-run INSTALL.md steps and then run this doctor again.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis portable setup diagnostics")
    parser.add_argument("--repo-only", action="store_true", help="skip checks under $HOME")
    args = parser.parse_args()

    return run_checks(repo_only=args.repo_only)


if __name__ == "__main__":
    raise SystemExit(main())
