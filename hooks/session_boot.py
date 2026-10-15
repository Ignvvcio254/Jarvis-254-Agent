#!/usr/bin/env python3
"""
JARVIS SESSION BOOT — autopilot de arranque (SessionStart hook).

Automatiza la recuperación de estado al abrir CUALQUIER sesión: inyecta el
scratchpad de tarea activa del proyecto + un recordatorio del protocolo del
harness. Resuelve el "resultado óptimo" de la pregunta 'en qué nos quedamos':
Jarvis sabe dónde quedó sin que el usuario lo pregunte.

Complementa el auto-memory (MEMORY.md ya se carga solo) añadiendo lo que NO se
carga: el scratchpad de trabajo en curso (.scratch/task.md) y el protocolo activo.

Uso (settings.json SessionStart):
  { "type": "command", "command": "python ~/.claude/scripts/session_boot.py" }

Lee {cwd, source} por stdin. Emite additionalContext con el brief de arranque.
Silencioso si no hay nada relevante que cargar (no ensucia sesiones nuevas).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

MAX_SCRATCH_CHARS = 1500   # no inundar el contexto de arranque
MAX_CKPT_CHARS = 2200      # checkpoint previo a compactar (lo escribe precompact_checkpoint.py)
CKPT_VIGENCIA_S = 6 * 3600


def read_event():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except Exception:
        return {}


def main():
    ev = read_event()
    root = Path(ev.get("cwd") or ".").resolve()
    parts = []

    # 0. Checkpoint previo a la compactación: solo cuando la sesión CONTINÚA tras compactar (source == "compact")
    ckpt = None
    if ev.get("source") == "compact":
        try:
            h = hashlib.sha1(str(ev.get("cwd") or "").lower().encode("utf-8")).hexdigest()[:10]
            f = Path.home() / ".claude" / "precompact" / "by-cwd" / f"{h}.md"
            if f.exists() and time.time() - f.stat().st_mtime < CKPT_VIGENCIA_S:
                ckpt = f.read_text(encoding="utf-8").strip()[:MAX_CKPT_CHARS]
        except Exception:
            ckpt = None
    if ckpt:
        parts.append("## State before the last compaction (compaction loses detail: use this to keep the thread)\n" + ckpt)

    # 1. Scratchpad de tarea activa (trabajo en curso) — scratchpad_resume
    scratch = root / ".scratch" / "task.md"
    if scratch.exists():
        try:
            txt = scratch.read_text(encoding="utf-8").strip()
            if txt:
                if len(txt) > MAX_SCRATCH_CHARS:
                    txt = txt[:MAX_SCRATCH_CHARS] + "\n... (truncated; read the full .scratch/task.md if you need more)"
                parts.append("## Work in progress (this project's scratchpad)\n" + txt)
        except Exception:
            pass

    # 2. Recordatorio del protocolo del harness (siempre, breve)
    parts.append(
        "## Active harness protocol\n"
        "- Before reporting code as done: run the verify gate (objective verdict). "
        "The verdict_guard Stop hook enforces it.\n"
        "- Before executing/delegating: token-router (minimum model by difficulty).\n"
        "- When closing significant work: propagate to memory (scratchpad skill).\n" "- Before claiming done/deployed, or on a works-but-doesn't symptom: field-lessons.\n"
        "- Core skills: verify-repair · token-router · scratchpad · agent-uplift · "
        "multi-cli · subagent-orchestration · long-run-harness."
    )

    # Solo emitir si hay scratchpad (trabajo en curso); el protocolo solo no
    # justifica inyección en cada sesión trivial.
    if not scratch.exists() and not ckpt:
        sys.exit(0)

    context = (
        "[session-boot] State restored automatically at startup:\n\n"
        + "\n\n".join(parts)
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()