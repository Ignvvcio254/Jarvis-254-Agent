#!/usr/bin/env python3
"""Builds plugins/jarvis-harness/ (a Claude Code plugin) from the repo sources.

The repo keeps ONE source of truth (skills/, agents/, hooks/); the plugin is a generated
copy so it can be installed with:

    /plugin marketplace add Ignvvcio254/Jarvis-254-Agent
    /plugin install jarvis-harness@jarvis-254

Usage:  python scripts/build_plugin.py          # rebuild
        python scripts/build_plugin.py --check  # exit 1 if the plugin is out of date (CI)
"""
from __future__ import annotations

import filecmp
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "plugins" / "jarvis-harness"
VERSION = "0.3.0"

CORE_SKILLS = ["verify-repair", "token-router", "scratchpad", "agent-uplift", "multi-cli",
               "subagent-orchestration", "long-run-harness", "jarvis-evolve", "prp", "bucle-agentico"]
HOOK_FILES = ["run-py.sh", "session_boot.py", "archetype_router.py", "correction_detector.py",
              "destructive_guard.py", "precompact_checkpoint.py", "verdict_guard.py", "verdict_stamp.py",
              "token_ledger.py", "harness_guard.mjs"]
COMMANDS = ["memoria.md", "consumo.md", "doctor.md"]

# event -> [(matcher, script, timeout)]  (same wiring as install.py)
HOOKS = {
    "SessionStart": [("", "session_boot.py", 10)],
    "UserPromptSubmit": [("", "archetype_router.py", 10), ("", "correction_detector.py", 10)],
    "PreToolUse": [("Bash|PowerShell|mcp__.*__(delete|buy|merge|sign|submit|cancel|terminate|reset|rollback).*",
                    "destructive_guard.py", 5)],
    "PreCompact": [("", "precompact_checkpoint.py", 15)],
    "Stop": [("", "verdict_guard.py", 10)],
}


def hooks_json() -> dict:
    out: dict = {"description": "Jarvis harness autopilot: session resume, archetype router, "
                                "correction capture, destructive guard, pre-compact checkpoint, verdict guard",
                 "hooks": {}}
    for event, entries in HOOKS.items():
        out["hooks"][event] = [{
            "matcher": matcher,
            "hooks": [{"type": "command", "timeout": timeout,
                       "command": f'sh "${{CLAUDE_PLUGIN_ROOT}}/hooks/run-py.sh" "${{CLAUDE_PLUGIN_ROOT}}/hooks/{script}"'}],
        } for matcher, script, timeout in entries]
    return out


def build(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    (dest / ".claude-plugin").mkdir(parents=True)
    (dest / ".claude-plugin" / "plugin.json").write_text(json.dumps({
        "name": "jarvis-harness",
        "version": VERSION,
        "description": "Objective verdicts (verify-repair), autopilot hooks, token routing, subagent "
                       "orchestration and self-improvement for Claude Code.",
        "author": {"name": "Jarvis-254-Agent contributors"},
        "homepage": "https://github.com/Ignvvcio254/Jarvis-254-Agent",
        "license": "MIT",
        "keywords": ["harness", "verification", "hooks", "subagents", "orchestration", "skills"],
    }, indent=2) + "\n", encoding="utf-8")
    for s in CORE_SKILLS:
        shutil.copytree(REPO / "skills" / s, dest / "skills" / s,
                        ignore=shutil.ignore_patterns("__pycache__", ".verify"))
    shutil.copytree(REPO / "agents", dest / "agents")
    (dest / "commands").mkdir()
    for c in COMMANDS:
        shutil.copy2(REPO / "commands" / c, dest / "commands" / c)
    (dest / "hooks").mkdir()
    for h in HOOK_FILES:
        shutil.copy2(REPO / "hooks" / h, dest / "hooks" / h)
    (dest / "hooks" / "hooks.json").write_text(json.dumps(hooks_json(), indent=2) + "\n", encoding="utf-8")


def same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    return not mismatch and not errors and all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def main() -> int:
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / "jarvis-harness"
            build(fresh)
            if not OUT.exists() or not same_tree(fresh, OUT):
                print("plugins/jarvis-harness is out of date: run python scripts/build_plugin.py")
                return 1
        print("plugin up to date")
        return 0
    build(OUT)
    print(f"built {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
