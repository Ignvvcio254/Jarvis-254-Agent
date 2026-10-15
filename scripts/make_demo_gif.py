#!/usr/bin/env python3
"""Renders assets/demo.gif from REAL command output (nothing in the GIF is typed by hand).

Each scene runs a command against a throwaway sandbox, captures its stdout, and animates it as a terminal:
the command is typed, then the captured output appears. Re-run after changing hooks or the gate.

Usage:  python scripts/make_demo_gif.py [--out assets/demo.gif]
Needs:  Pillow (pip install pillow), node on PATH.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
W, H, PAD, LINE = 980, 560, 22, 21
BG, FG, DIM, PROMPT, OK, BAD, WARN, ACCENT = (
    "#0d1117", "#e6edf3", "#7d8590", "#58a6ff", "#3fb950", "#f85149", "#d29922", "#bc8cff")


def font(size: int) -> ImageFont.FreeTypeFont:
    for name in ("consola.ttf", "DejaVuSansMono.ttf", "Menlo.ttc", "LiberationMono-Regular.ttf"):
        for base in ("C:/Windows/Fonts", "/usr/share/fonts/truetype/dejavu", "/System/Library/Fonts", ""):
            try:
                return ImageFont.truetype(str(Path(base) / name) if base else name, size)
            except OSError:
                continue
    return ImageFont.load_default()


SANDBOX: Path | None = None  # replaced by "~/demo" in every captured line (no real paths in the GIF)


def run(cmd: list[str], stdin: str = "", cwd: Path | None = None) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=cwd or REPO, env=env)
    out = (p.stdout + p.stderr).strip()
    if SANDBOX is not None:
        for form in {str(SANDBOX), SANDBOX.as_posix(), str(SANDBOX.resolve())}:
            out = out.replace(form, "~/demo")
        out = out.replace("~/demo\\", "~/demo/")
    return out.replace(str(Path.home()), "~").replace(Path.home().as_posix(), "~")


def hook_context(out: str) -> str:
    try:
        o = json.loads(out)["hookSpecificOutput"]
        return o.get("additionalContext") or f"permissionDecision: {o['permissionDecision']}\n{o['permissionDecisionReason']}"
    except (ValueError, KeyError):
        return out


def wrap(text: str, width: int = 108) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        while len(raw) > width:
            cut = raw.rfind(" ", 0, width)
            cut = cut if cut > 20 else width
            lines.append(raw[:cut])
            raw = "  " + raw[cut:].lstrip()
        lines.append(raw)
    return lines


def colour(line: str) -> str:
    low = line.lower()
    if "fail" in low or "invalid" in low or "mass or irreversible" in low:
        return BAD
    if "pass" in low or " ok" in low or "distinguish" in low:
        return OK
    if line.startswith("[") or "permissiondecision" in low:
        return WARN
    return FG


def scenes(sandbox: Path) -> list[tuple[str, str, str]]:
    """(title, command shown, real output)."""
    gate = str(REPO / "skills" / "verify-repair" / "verify_gate.py")
    app = sandbox / "app"
    app.mkdir()
    (app / "main.py").write_text("def total(items):\n    return sum(i['price'] for i in items\n", encoding="utf-8")
    fail = run([PY, gate, "--path", str(app)])
    (app / "main.py").write_text("def total(items):\n    return sum(i['price'] for i in items)\n", encoding="utf-8")
    ok = run([PY, gate, "--path", str(app)])
    hooks = REPO / "hooks"
    route = hook_context(run([PY, str(hooks / "archetype_router.py")],
                             json.dumps({"prompt": "the checkout page crashes, please fix it"})))
    corr = hook_context(run([PY, str(hooks / "correction_detector.py")],
                            json.dumps({"prompt": "no, actually use pnpm instead of npm"})))
    guard = hook_context(run([PY, str(hooks / "destructive_guard.py")],
                             json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf ./src"}})))
    install = run([PY, str(REPO / "install.py"), "--dry-run", "--claude-dir", str(sandbox / ".claude")])
    assert "Users" not in install and "\\" not in install, "a real path leaked into the demo"
    evals = "\n".join(run(["node", str(REPO / "evals" / "jarvis-eval.mjs"), "--selftest"]).splitlines()[-5:])
    return [
        ("Install — merges, never overwrites", "python install.py --dry-run", install),
        ("Objective verdict — the model's word is not enough", "python verify_gate.py --path app   # broken code",
         fail.replace("~/demo/app", "./app")),
        ("Objective verdict — fixed and re-verified", "python verify_gate.py --path app", ok.replace("~/demo/app", "./app")),
        ("Autopilot hook — routes the task", 'prompt: "the checkout page crashes, please fix it"', route),
        ("Autopilot hook — captures corrections", 'prompt: "no, actually use pnpm instead of npm"', corr),
        ("Autopilot hook — guards destructive actions", "Bash: rm -rf ./src", guard),
        ("Behaviour bench — graders checked before any real run", "node evals/jarvis-eval.mjs --selftest", evals),
    ]


def frame(title: str, shown: list[tuple[str, str]], f_title, f_body) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, W - 8, H - 8], radius=12, outline="#30363d", width=2)
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        d.ellipse([24 + i * 20, 22, 36 + i * 20, 34], fill=c)
    d.text((100, 18), "Jarvis-254-Agent", font=f_title, fill=DIM)
    d.text((PAD, 52), title, font=f_title, fill=ACCENT)
    y = 88
    for text, col in shown[-((H - 110) // LINE):]:
        d.text((PAD, y), text, font=f_body, fill=col)
        y += LINE
    return img


def build(out: Path) -> None:
    f_title, f_body = font(18), font(15)
    frames: list[Image.Image] = []
    durations: list[int] = []
    global SANDBOX
    with tempfile.TemporaryDirectory() as tmp:
        SANDBOX = Path(tmp)
        for title, cmd, output in scenes(SANDBOX):
            shown: list[tuple[str, str]] = []
            typed = "$ "
            for ch in cmd:  # type the command
                typed += ch
                if len(typed) % 3 == 0 or ch == cmd[-1]:
                    frames.append(frame(title, shown + [(typed + "▌", PROMPT)], f_title, f_body))
                    durations.append(35)
            shown.append((typed, PROMPT))
            for line in wrap(output):  # reveal the real output
                shown.append((line, colour(line)))
                frames.append(frame(title, shown, f_title, f_body))
                durations.append(70)
            durations[-1] = 2200  # hold the result
    out.parent.mkdir(parents=True, exist_ok=True)
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=64) for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durations, loop=0, optimize=True, disposal=2)
    print(f"{out.relative_to(REPO)}: {len(frames)} frames, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "assets" / "demo.gif"))
    build(Path(ap.parse_args().out))
