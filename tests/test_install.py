import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(home: Path, *extra: str) -> None:
    subprocess.run([sys.executable, str(REPO / "install.py"), "--claude-dir", str(home), *extra],
                   check=True, capture_output=True)


def test_install_merges_hooks_without_clobbering(tmp_path):
    user_hook = {"matcher": "", "hooks": [{"type": "command", "command": "echo mine"}]}
    (tmp_path / "settings.json").write_text(json.dumps({"model": "opus", "hooks": {"Stop": [user_hook]}}))
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "gateway.json").write_text("{\"custom\": true}")

    run(tmp_path)
    run(tmp_path)  # idempotente

    s = json.loads((tmp_path / "settings.json").read_text())
    assert s["model"] == "opus"
    stop_cmds = [h["command"] for g in s["hooks"]["Stop"] for h in g["hooks"]]
    assert "echo mine" in stop_cmds
    assert sum("verdict_guard.py" in c for c in stop_cmds) == 1
    assert json.loads((tmp_path / "profiles" / "gateway.json").read_text()) == {"custom": True}
    assert (tmp_path / "skills" / "verify-repair" / "SKILL.md").exists()
    assert (tmp_path / "scripts" / "modelo-proxy.mjs").exists()
    assert (tmp_path / "agents" / "code-reviewer.md").exists()


def test_dry_run_writes_nothing(tmp_path):
    run(tmp_path, "--dry-run")
    assert not any(tmp_path.iterdir())


def test_name_fills_placeholder_only_on_fresh_install(tmp_path):
    run(tmp_path, "--name", "Ada", "--no-hooks")
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "{{YOUR_NAME}}" not in text and "Ada" in text
    (tmp_path / "CLAUDE.md").write_text("mine", encoding="utf-8")
    run(tmp_path, "--name", "Other", "--no-hooks")
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "mine"


def test_skill_profiles_reference_existing_skills():
    profiles = json.loads((REPO / "skills" / "PROFILES.json").read_text(encoding="utf-8"))
    for name in profiles["core"] + profiles["dev"]:
        assert (REPO / "skills" / name / "SKILL.md").exists(), name


def test_core_profile_is_lean(tmp_path):
    run(tmp_path, "--skills", "core", "--no-hooks")
    installed = [p for p in (tmp_path / "skills").iterdir() if p.is_dir()]
    assert 5 <= len(installed) <= 20
    assert (tmp_path / "skills" / "field-lessons" / "SKILL.md").exists()
    assert (tmp_path / "output-styles" / "jarvis-concise.md").exists()
    assert (tmp_path / "evals" / "jarvis-eval.mjs").exists()
