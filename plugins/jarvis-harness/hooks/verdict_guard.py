#!/usr/bin/env python3
"""
JARVIS VERDICT GUARD — impone el veredicto objetivo (patrón GateGuard del repo
ganador ECC + Performance Outcomes de Anthropic).

El harness dice "verifica antes de reportar" como REGLA (skill verify-repair).
Este guard la convierte en ENFORCEMENT: como Stop hook, detecta si en el proyecto
hay archivos de código modificados más recientemente que el último veredicto
`pass`, y si es así inyecta un recordatorio para correr verify-gate antes de
cerrar. El sistema impone la disciplina; no depende de que Jarvis la recuerde.

Doctrina (comunidad 4 capas): "Skill enseña · Hook impone · Subagente aísla".
Este es el HOOK que impone lo que el skill verify-repair enseña.

GATES NO-PS1 (fix 2026-06-26, feedback_verdict_guard_nontsc_gates): para no dar
falsos positivos cuando el archivo SÍ se verificó por otro gate válido, el guard
auto-verifica los archivos baratos de chequear:
  - .js/.mjs/.cjs  → `node --check`   (sintaxis de Node/Electron, instantáneo)
  - .py            → `py_compile`     (sintaxis de Python, instantáneo)
Un archivo barato que pasa se considera VERIFICADO y no dispara el aviso. Los
caros (.ts/.tsx, build) se sellan con `verdict_stamp.py` o `verify-gate.ps1`.

Uso como Stop hook (settings.json):
  { "type": "command", "command": "python ~/.claude/scripts/verdict_guard.py" }

Lee el JSON del evento por stdin (cwd). Salida:
  - exit 0 + texto vacío  → todo verificado, silencio (success is quiet)
  - exit 0 + additionalContext → recordatorio de verificar (no bloquea, avisa)
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CODE_EXT = {".js", ".ts", ".tsx", ".jsx", ".py", ".go", ".rs", ".php", ".html",
            ".css", ".java", ".rb", ".c", ".cpp", ".cs", ".ps1", ".sh"}
# Extensiones que se pueden verificar barato (sintaxis) en el propio hook.
NODE_CHECK_EXT = {".js", ".mjs", ".cjs"}
PY_CHECK_EXT = {".py"}
IGNORE = {"node_modules", ".git", ".verify", "__pycache__", ".venv", "venv",
          ".swarm", ".hive-mind", ".scratch", "_reference", "backups",
          ".claude", "AppData", "Temp", ".cache", ".bun", "dist", "build",
          ".next", "target"}
IGNORE_FILES = {"next-env.d.ts"}
MAX_AGE_S = 1800   # solo mirar código tocado en los últimos 30 min (este turno)
MAX_FILES = 20000  # backstop: no escanear árboles gigantes indefinidamente
MAX_CHEAP_CHECKS = 25  # cota de verificaciones baratas por ejecución del hook


_HERE = Path(__file__).resolve().parent
STAMP = (_HERE / "verdict_stamp.py").as_posix()
GATE = next((p.as_posix() for p in (_HERE.parent / "skills" / "verify-repair" / "verify_gate.py",
                                     Path.home() / ".claude" / "skills" / "verify-repair" / "verify_gate.py")
             if p.exists()), "~/.claude/skills/verify-repair/verify_gate.py")


def read_event():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except Exception:
        return {}


def verdict_mtime(root: Path):
    """mtime de un .verify/verdict.json con verdict 'pass'; None si no hay/!pass."""
    vf = root / ".verify" / "verdict.json"
    if not vf.exists():
        return None
    try:
        d = json.loads(vf.read_text(encoding="utf-8"))
        if d.get("verdict") == "pass":
            return vf.stat().st_mtime
        return False  # existe pero NO es pass (señal distinta a "no existe")
    except Exception:
        return None


def cheap_check(path: Path) -> bool:
    """True si el archivo pasa su verificación barata de sintaxis. Para exts no
    cubiertas devuelve False (no es 'falla', es 'no aplica' → lo maneja el caller)."""
    ext = path.suffix.lower()
    try:
        if ext in NODE_CHECK_EXT:
            node = shutil.which("node")
            if not node:
                return False
            r = subprocess.run([node, "--check", str(path)],
                               capture_output=True, timeout=15)
            return r.returncode == 0
        if ext in PY_CHECK_EXT:
            r = subprocess.run([sys.executable, "-m", "py_compile", str(path)],
                               capture_output=True, timeout=15)
            return r.returncode == 0
    except Exception:
        return False
    return False


def is_cheap_ext(path: Path) -> bool:
    ext = path.suffix.lower()
    return ext in NODE_CHECK_EXT or ext in PY_CHECK_EXT


def recent_code_files(root: Path, cutoff: float):
    """Lista (mtime, Path) de archivos de código tocados después de `cutoff`,
    podando dirs ignorados. Ordenada por mtime descendente."""
    out, seen = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE]
        for fn in filenames:
            if fn in IGNORE_FILES:
                continue
            if os.path.splitext(fn)[1].lower() not in CODE_EXT:
                continue
            seen += 1
            if seen > MAX_FILES:
                break
            p = os.path.join(dirpath, fn)
            try:
                m = os.stat(p).st_mtime
            except OSError:
                continue
            if m > cutoff:
                out.append((m, Path(p)))
        if seen > MAX_FILES:
            break
    out.sort(key=lambda t: t[0], reverse=True)
    return out


def newest_unverified(root: Path, now: float, vmtime):
    """Devuelve (file, kind) del archivo más nuevo que NECESITA veredicto:
      - salta archivos baratos que pasan su chequeo de sintaxis (verificados)
      - kind='fail' si un archivo barato FALLA su chequeo (problema real)
      - kind='need' si es un archivo no-barato (ts/etc) sin veredicto pass fresco
    Devuelve (None, None) si todo lo reciente está verificado.
    """
    cutoff = now - MAX_AGE_S
    # si hay verdict pass, solo importan archivos más nuevos que él
    base = cutoff
    if isinstance(vmtime, float):
        base = max(base, vmtime)
    files = recent_code_files(root, base)
    cheap_done = 0
    for _m, p in files:
        if is_cheap_ext(p) and cheap_done < MAX_CHEAP_CHECKS:
            cheap_done += 1
            if cheap_check(p):
                continue          # verificado barato → no bloquea
            return p, "fail"      # sintaxis rota → problema real
        # no-barato (o se acabó la cuota de chequeos): necesita veredicto
        return p, "need"
    return None, None


def emit(context: str):
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": context}
    }))


def main():
    ev = read_event()
    if ev.get("stop_hook_active"):
        sys.exit(0)
    root = Path(ev.get("cwd") or ".").resolve()
    now = time.time()

    vmtime = verdict_mtime(root)  # float (pass), False (no-pass), o None (no existe)
    nf, kind = newest_unverified(root, now, vmtime)
    if nf is None:
        sys.exit(0)  # nada reciente sin verificar → silencio

    rel = nf.name
    if kind == "fail":
        msg = (f"[verdict-guard] {rel} FAILS its syntax check "
               f"(node --check / py_compile). Fix it before reporting.")
    elif vmtime is None:
        msg = (f"[verdict-guard] You edited {rel} (not cheaply auto-verifiable) and there is NO "
               f"`.verify/verdict.json`. Run the objective verdict before reporting: "
               f"`python {GATE} --path .`, or if you already "
               f"verified with tsc/build, stamp it: `python {STAMP} tsc`.")
    elif vmtime is False:
        msg = (f"[verdict-guard] The last verdict is NOT 'pass'. Don't report success: "
               f"repair and re-verify before closing.")
    else:
        msg = (f"[verdict-guard] {rel} changed after the last passing verdict. "
               f"If you already verified it (tsc/build/deploy), stamp it: "
               f"`python {STAMP} tsc`. Otherwise run the verify gate.")
    emit(msg)
    sys.exit(0)


if __name__ == "__main__":
    main()
