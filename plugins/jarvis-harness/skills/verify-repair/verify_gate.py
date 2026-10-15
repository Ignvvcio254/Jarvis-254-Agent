#!/usr/bin/env python3
"""verify_gate.py — OBJECTIVE task-completion verdict (cross-platform port of verify-gate.ps1).

A task is not done because the model says so, but because the checks pass.
Auto-detects the project, runs the applicable checks (build/parse, typecheck,
lint, test, case verifier, behaviour) and writes .verify/verdict.json bound to a
stateHash (sha256 of the tree). Exit 0 only if EVERYTHING applicable passes.

Usage:
  python verify_gate.py [--path .] [--verifier "node verify.js"]
                        [--must-contain X --file F] [--must-not-contain Y --file F]
Exit: 0 pass · 1 fail / no checks · 2 setup error
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKIP_DIRS = re.compile(r"node_modules|\.git|\.verify|__pycache__|\.venv|venv|\.swarm|\.hive-mind")
SKIP_FILES = re.compile(r"\.(index|db|lock)$")


class Gate:
    def __init__(self) -> None:
        self.checks: list[dict] = []

    def add(self, name: str, ok: bool, detail: str) -> None:
        self.checks.append({"name": name, "status": "pass" if ok else "fail", "detail": detail})
        print(f"  [{'OK  ' if ok else 'FAIL'}] {name} {detail}")


def run(cmd: list[str] | str, cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, FileNotFoundError) as e:
        return 127, str(e)


def npm() -> str | None:
    return shutil.which("npm.cmd") or shutil.which("npm")


def node_check(path: Path, root: Path) -> bool:
    return run(["node", "--check", str(path)], root)[0] == 0


def py_files(root: Path) -> list[Path]:
    return [f for f in root.rglob("*.py") if not SKIP_DIRS.search(str(f.relative_to(root)))]


def check_node(g: Gate, root: Path) -> None:
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return
    try:
        scripts = json.loads(pkg_path.read_text(encoding="utf-8")).get("scripts") or {}
    except json.JSONDecodeError:
        g.add("package.json", False, "invalid JSON")
        return
    n = npm()
    if not n:
        g.add("npm", False, "package.json present but npm not found")
        return
    if "build" in scripts:
        g.add("build", run([n, "run", "build"], root)[0] == 0, "npm run build")
    if (root / "tsconfig.json").exists():
        npx = shutil.which("npx.cmd") or shutil.which("npx")
        if npx:
            g.add("typecheck", run([npx, "tsc", "--noEmit"], root)[0] == 0, "tsc --noEmit")
    if "lint" in scripts:
        g.add("lint", run([n, "run", "lint"], root)[0] == 0, "npm run lint")
    if "test" in scripts:
        code, out = run([n, "test"], root)
        if "no test specified" not in out:
            g.add("test", code == 0, "npm test")


def check_loose_js(g: Gate, root: Path) -> None:
    if not shutil.which("node"):
        return
    js = sorted(root.glob("*.js")) + sorted(root.glob("*.mjs"))
    if js:
        bad = [f.name for f in js if not node_check(f, root)]
        g.add("parse-js", not bad, f"invalid syntax: {', '.join(bad)}" if bad else f"{len(js)} JS files OK")
    html = sorted(root.glob("*.html"))
    if not html:
        return
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        for h in html:
            content = h.read_text(encoding="utf-8", errors="replace")
            for i, m in enumerate(re.finditer(r"(?s)<script([^>]*)>(.*?)</script>", content)):
                attrs, code = m.group(1), m.group(2)
                if len(code.strip()) < 5 or re.search(r"src\s*=", attrs) or "module" in attrs:
                    continue
                t = Path(tmp) / f"{h.stem}_{i}.js"
                t.write_text(code, encoding="utf-8")
                if not node_check(t, root):
                    bad.append(f"{h.name}#script{i}")
    g.add("parse-html-js", not bad, f"invalid inline JS: {', '.join(bad)}" if bad else f"{len(html)} HTML OK")


def check_python(g: Gate, root: Path) -> None:
    files = py_files(root)
    if not files:
        return
    bad = [f.name for f in files if run([sys.executable, "-m", "py_compile", str(f)], root)[0] != 0]
    g.add("parse-py", not bad, f"invalid syntax: {', '.join(bad)}" if bad else f"{len(files)} .py files OK")
    has_tests = (root / "tests").is_dir() or any(root.glob("test_*.py"))
    if has_tests:
        code, out = run([sys.executable, "-m", "pytest", "-q"], root)
        if "No module named pytest" in out:
            g.add("test", False, "pytest not installed")
        else:
            g.add("test", code == 0, "pytest")


def check_verifier(g: Gate, root: Path, verifier: str) -> None:
    code, out = run(verifier, root)
    ok, score = code == 0, None
    try:
        score = json.loads(out.strip().splitlines()[-1]).get("score")
    except (ValueError, IndexError, AttributeError):
        pass
    if score is not None:
        ok = score >= 100
    g.add("verifier", ok, verifier + (f" (score={score})" if score is not None else ""))


def check_behaviour(g: Gate, root: Path, a: argparse.Namespace) -> None:
    if not a.file:
        return
    fp = root / a.file
    text = fp.read_text(encoding="utf-8", errors="replace") if fp.exists() else None
    if a.must_contain:
        g.add("must-contain", text is not None and a.must_contain in text, f"'{a.must_contain}' in {a.file}")
    if a.must_not_contain:
        g.add("must-not-contain", text is None or a.must_not_contain not in text,
              f"'{a.must_not_contain}' absent from {a.file}")


def state_hash(root: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = f.relative_to(root).as_posix()
        if SKIP_DIRS.search(rel) or SKIP_FILES.search(rel):
            continue
        try:
            digest = hashlib.sha256(f.read_bytes()).hexdigest()
        except OSError:
            digest = "locked"
        h.update(f"{rel}:{digest};".encode())
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Objective verdict gate")
    ap.add_argument("--path", default=".")
    ap.add_argument("--verifier", default="")
    ap.add_argument("--must-contain", default="")
    ap.add_argument("--must-not-contain", default="")
    ap.add_argument("--file", default="")
    a = ap.parse_args()

    root = Path(a.path).resolve()
    if not root.is_dir():
        print(f"[gate] path does not exist: {a.path}", file=sys.stderr)
        return 2
    print(f">>> verify-gate :: {root}")

    g = Gate()
    check_node(g, root)
    check_loose_js(g, root)
    check_python(g, root)
    if a.verifier:
        check_verifier(g, root, a.verifier)
    check_behaviour(g, root, a)

    failed = [c["name"] for c in g.checks if c["status"] == "fail"]
    verdict = "no-checks" if not g.checks else ("fail" if failed else "pass")
    out_dir = root / ".verify"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "verdict.json").write_text(json.dumps({
        "verdict": verdict,
        "stateHash": state_hash(root),
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "checks": g.checks,
        "gate": "verify_gate.py",
        "note": "Objective verdict. The model must not write this file by hand.",
    }, indent=2), encoding="utf-8")

    print()
    if verdict == "pass":
        print(f"=== VERDICT: PASS ({len(g.checks)} checks) ===")
        return 0
    if verdict == "no-checks":
        print("=== VERDICT: NO APPLICABLE CHECKS — cannot attest ===")
        print("    Pass --verifier or --must-contain/--file for a task without build/test.")
        return 1
    print(f"=== VERDICT: FAIL ({len(failed)}/{len(g.checks)} checks) — failed: {', '.join(failed)} ===")
    return 1


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
