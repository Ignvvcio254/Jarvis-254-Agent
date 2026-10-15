import json
import subprocess
import sys
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "skills" / "verify-repair" / "verify_gate.py"


def gate(path: Path, *args: str) -> int:
    return subprocess.run([sys.executable, str(GATE), "--path", str(path), *args],
                          capture_output=True, text=True).returncode


def verdict(path: Path) -> dict:
    return json.loads((path / ".verify" / "verdict.json").read_text())


def test_pass_on_valid_python(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    assert gate(tmp_path) == 0
    v = verdict(tmp_path)
    assert v["verdict"] == "pass" and len(v["stateHash"]) == 64


def test_fail_on_syntax_error(tmp_path):
    (tmp_path / "app.py").write_text("def broken(:\n")
    assert gate(tmp_path) == 1
    assert verdict(tmp_path)["verdict"] == "fail"


def test_no_checks_is_not_a_pass(tmp_path):
    (tmp_path / "notes.txt").write_text("hello")
    assert gate(tmp_path) == 1
    assert verdict(tmp_path)["verdict"] == "no-checks"


def test_behaviour_checks(tmp_path):
    (tmp_path / "page.txt").write_text("dayPhase = 'night'")
    assert gate(tmp_path, "--must-contain", "dayPhase", "--file", "page.txt") == 0
    assert gate(tmp_path, "--must-not-contain", "dayPhase", "--file", "page.txt") == 1


def test_verifier_exit_code(tmp_path):
    ok = f'"{sys.executable}" -c "raise SystemExit(0)"'
    bad = f'"{sys.executable}" -c "raise SystemExit(3)"'
    assert gate(tmp_path, "--verifier", ok) == 0
    assert gate(tmp_path, "--verifier", bad) == 1


def test_missing_path_is_setup_error(tmp_path):
    assert gate(tmp_path / "nope") == 2
