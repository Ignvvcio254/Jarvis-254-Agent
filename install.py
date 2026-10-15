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

# evento -> [(matcher, script, timeout)]
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

# (origen en el repo, destino relativo a ~/.claude, sobrescribir)
COPIES = [
    ("skills", "skills", True),
    ("agents", "agents", True),
    ("commands", "commands", True),
    ("rules", "rules", True),
    ("hooks", "scripts", True),
    ("models", "scripts", True),
    ("models/profiles/gateway.example.json", "profiles/gateway.json", False),
    ("models/profiles/multi.settings.example.json", "profiles/multi.settings.json", False),
]


def copy_item(src: Path, dst: Path, overwrite: bool, dry: bool) -> int:
    if src.is_file():
        if dst.exists() and not overwrite:
            print(f"  = {dst} (ya existe, se respeta)")
            return 0
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return 1
    n = 0
    for f in src.rglob("*"):
        if f.is_file() and "__pycache__" not in f.parts and f.name != "profiles":
            if f.parent.name == "profiles" and src.name == "models":
                continue  # los perfiles se instalan aparte, sin pisar
            n += copy_item(f, dst / f.relative_to(src), overwrite, dry)
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
    ap.add_argument("--name", default="", help="how Jarvis addresses you; fills {{YOUR_NAME}} in CLAUDE.md")
    a = ap.parse_args()
    home = Path(a.claude_dir).expanduser()

    print(f"Jarvis 254 Agent -> {home}{' (dry-run)' if a.dry_run else ''}")
    for src, dst, overwrite in COPIES:
        n = copy_item(REPO / src, home / dst, overwrite, a.dry_run)
        print(f"  + {src} -> {dst}: {n} archivo(s)")

    claude_md = home / "CLAUDE.md"
    if not claude_md.exists():
        if not a.dry_run:
            text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
            if a.name:
                text = text.replace("{{YOUR_NAME}}", a.name)
            claude_md.parent.mkdir(parents=True, exist_ok=True)
            claude_md.write_text(text, encoding="utf-8")
        hint = "" if a.name else " — tip: --name \"Ada\" fills {{YOUR_NAME}}"
        print(f"  + CLAUDE.md instalado{hint}")
    else:
        print("  = CLAUDE.md ya existe: no se toca. Compare con el del repo y fusione a mano.")

    if a.no_hooks:
        print("  = hooks omitidos (--no-hooks)")
        return 0

    settings_path = home / "settings.json"
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
    except json.JSONDecodeError as e:
        print(f"ERROR: {settings_path} no es JSON válido ({e}). No se modifica.", file=sys.stderr)
        return 1
    added = merge_hooks(settings, home / "scripts")
    if added and not a.dry_run:
        if settings_path.exists():
            backup = settings_path.with_suffix(f".json.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            shutil.copy2(settings_path, backup)
            print(f"  respaldo: {backup}")
        settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  hooks fusionados: {added} nuevo(s) (los existentes se respetan)")
    print("Listo. Verifique con: python jarvis_doctor.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
