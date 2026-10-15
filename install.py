#!/usr/bin/env python3
"""Jarvis 254 Agent — instalador idempotente.

Copia skills, agentes, comandos, hooks y el gateway multi-modelo a ~/.claude y
FUSIONA los hooks en ~/.claude/settings.json (nunca reemplaza la config existente:
respaldo + merge sin duplicados).

Uso:
  python install.py                 # instala todo
  python install.py --dry-run       # muestra lo que haría, sin escribir
  python install.py --no-hooks      # copia archivos pero no toca settings.json
  python install.py --claude-dir X  # otro directorio de Claude Code
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent

# event -> [(matcher, script, timeout)]
HOOKS = {
    "SessionStart": [("", "session_boot.py", 10)],
    "UserPromptSubmit": [("", "archetype_router.py", 10), ("", "correction_detector.py", 10)],
    "PreToolUse": [(
        "Bash|PowerShell|mcp__.*__(delete|buy|merge|sign|submit|cancel|terminate|reset|rollback).*",
        "destructive_guard.py", 5,
    )],
    "PreCompact": [("", "precompact_checkpoint.py", 15)],
    "Stop": [("", "verdict_guard.py", 10)],
}

# (source in the repo, destination relative to ~/.claude, overwrite)
COPIES = [
    ("agents", "agents", True),
    ("commands", "commands", True),
    ("rules", "rules", True),
    ("hooks", "scripts", True),
    ("models", "scripts", True),
    ("evals", "evals", True),
    ("output-styles", "output-styles", True),
    ("models/profiles/gateway.example.json", "profiles/gateway.json", False),
    ("models/profiles/multi.settings.example.json", "profiles/multi.settings.json", False),
]


def copy_item(src: Path, dst: Path, overwrite: bool, dry: bool) -> int:
    if src.is_file():
        if dst.exists() and not overwrite:
            print(f"  = {dst} (already exists, kept)")
            return 0
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return 1
    n = 0
    for f in src.rglob("*"):
        if f.is_file() and "__pycache__" not in f.parts and f.name != "profiles":
            if f.parent.name == "profiles" and src.name == "models":
                continue  # profiles are installed separately, never overwritten
            n += copy_item(f, dst / f.relative_to(src), overwrite, dry)
    return n


def install_skills(home: Path, profile: str, dry: bool) -> int:
    """core = harness only · dev = core + curated engineering pack (default) · all = every skill."""
    src = REPO / "skills"
    if profile == "all":
        names = sorted(p.name for p in src.iterdir() if (p / "SKILL.md").exists())
    else:
        profiles = json.loads((src / "PROFILES.json").read_text(encoding="utf-8"))
        names = profiles["core"] + (profiles["dev"] if profile == "dev" else [])
    n = 0
    for name in names:
        if (src / name).is_dir():
            n += copy_item(src / name, home / "skills" / name, True, dry)
    print(f"  + skills ({profile}): {len(names)} skill(s), {n} file(s)")
    return n


def hook_command(script: Path) -> str:
    exe = "python" if sys.platform == "win32" else "python3"
    return f'{exe} "{script.as_posix()}"'


def merge_hooks(settings: dict, scripts_dir: Path) -> int:
    hooks = settings.setdefault("hooks", {})
    added = 0
    for event, entries in HOOKS.items():
        groups = hooks.setdefault(event, [])
        existing = {h.get("command", "") for g in groups for h in g.get("hooks", [])}
        for matcher, script, timeout in entries:
            if any(script in c for c in existing):
                continue
            groups.append({"matcher": matcher, "hooks": [{
                "type": "command", "command": hook_command(scripts_dir / script), "timeout": timeout,
            }]})
            added += 1
    return added


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--claude-dir", default=str(Path.home() / ".claude"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-hooks", action="store_true")
    ap.add_argument("--skills", choices=["core", "dev", "all"], default="dev",
                    help="core: harness only · dev: + curated engineering pack (default) · all: 1400+ (~57k tokens/session)")
    ap.add_argument("--name", default="", help="how Jarvis addresses you; fills {{YOUR_NAME}} in CLAUDE.md")
    a = ap.parse_args()
    home = Path(a.claude_dir).expanduser()

    print(f"Jarvis 254 Agent -> {home}{' (dry-run)' if a.dry_run else ''}")
    install_skills(home, a.skills, a.dry_run)
    for src, dst, overwrite in COPIES:
        n = copy_item(REPO / src, home / dst, overwrite, a.dry_run)
        print(f"  + {src} -> {dst}: {n} file(s)")

    claude_md = home / "CLAUDE.md"
    if not claude_md.exists():
        if not a.dry_run:
            text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
            if a.name:
                text = text.replace("{{YOUR_NAME}}", a.name)
            claude_md.parent.mkdir(parents=True, exist_ok=True)
            claude_md.write_text(text, encoding="utf-8")
        hint = "" if a.name else " — tip: --name \"Ada\" fills {{YOUR_NAME}}"
        print(f"  + CLAUDE.md installed{hint}")
    else:
        print("  = CLAUDE.md already exists: left untouched. Compare it with the repo's and merge by hand.")

    if a.no_hooks:
        print("  = hooks skipped (--no-hooks)")
        return 0

    settings_path = home / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
    except json.JSONDecodeError as e:
        print(f"ERROR: {settings_path} is not valid JSON ({e}). Left unchanged.", file=sys.stderr)
        return 1
    added = merge_hooks(settings, home / "scripts")
    if added and not a.dry_run:
        if settings_path.exists():
            backup = settings_path.with_suffix(f".json.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            shutil.copy2(settings_path, backup)
            print(f"  backup: {backup}")
        settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  hooks merged: {added} new (existing ones kept)")
    print("Done. Check with: python jarvis_doctor.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
