import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOOKS = REPO / "hooks"


def hook(script: str, event: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOKS / script)], input=json.dumps(event),
                          capture_output=True, text=True, encoding="utf-8", timeout=30)


def context(proc: subprocess.CompletedProcess) -> str:
    return json.loads(proc.stdout)["hookSpecificOutput"].get("additionalContext", "") if proc.stdout.strip() else ""


def test_plugin_is_in_sync_with_sources():
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "build_plugin.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_marketplace_points_to_existing_plugin():
    m = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    for p in m["plugins"]:
        root = (REPO / p["source"]).resolve()
        manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        assert manifest["name"] == p["name"]
        hooks = json.loads((root / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        for groups in hooks.values():
            for g in groups:
                for h in g["hooks"]:
                    script = h["command"].split("/hooks/")[-1].strip('"')
                    assert (root / "hooks" / script).exists(), script


@pytest.mark.parametrize("prompt,expected", [
    ("implement a new endpoint for users", "BUILD"),
    ("the login page crashes, please fix it", "FIX"),
    ("crea un componente nuevo para el dashboard", "BUILD"),
])
def test_archetype_router_bilingual(prompt, expected):
    assert f"**{expected}**" in context(hook("archetype_router.py", {"prompt": prompt}))


def test_archetype_router_ignores_small_talk():
    assert hook("archetype_router.py", {"prompt": "hi there, thanks!"}).stdout.strip() == ""


@pytest.mark.parametrize("prompt", ["no, actually use pnpm instead", "I already told you to use tabs",
                                    "ya te dije que uses pnpm", "eso está mal"])
def test_correction_detector_bilingual(prompt):
    assert "CORRECTION" in context(hook("correction_detector.py", {"prompt": prompt}))


def test_correction_detector_quiet_on_normal_prompt():
    assert hook("correction_detector.py", {"prompt": "add a dark mode toggle"}).stdout.strip() == ""


def test_destructive_guard_asks_on_recursive_delete():
    out = json.loads(hook("destructive_guard.py",
                          {"tool_name": "Bash", "tool_input": {"command": "rm -rf ~/projects/app"}}).stdout)
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"


@pytest.mark.parametrize("script", ["session_boot.py", "precompact_checkpoint.py", "verdict_guard.py"])
def test_lifecycle_hooks_never_crash(script, tmp_path):
    r = hook(script, {"cwd": str(tmp_path), "session_id": "t", "transcript_path": "", "hook_event_name": "x"})
    assert r.returncode == 0, r.stderr
