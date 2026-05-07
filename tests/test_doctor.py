"""Tests for jarvis_doctor.py repo-only mode."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_doctor_repo_only_passes():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "jarvis_doctor.py"), "--repo-only"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Doctor failed:\n{result.stdout}\n{result.stderr}"


def test_doctor_output_contains_all_ok():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "jarvis_doctor.py"), "--repo-only"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert "[MISSING]" not in result.stdout, f"Missing files:\n{result.stdout}"
    assert "All checks passed" in result.stdout
