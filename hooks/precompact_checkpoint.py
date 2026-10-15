#!/usr/bin/env python3
"""
JARVIS PRECOMPACT CHECKPOINT — que la compactación no me borre el hilo.

Cuando el contexto se llena, Claude Code compacta (resume) la conversación y se pierde detalle: qué pidió el
usuario hace diez turnos, qué archivos se tocaron, qué faltaba. Este hook (evento PreCompact) guarda un
resumen COMPACTO del estado en ~/.claude/precompact/by-cwd/<hash-del-cwd>.md, y session_boot.py lo reinyecta
cuando la sesión continúa tras la compactación (SessionStart con source="compact").

Qué guarda (todo sale del transcript, sin llamar a ningún modelo):
  · los últimos pedidos REALES del usuario (sin notificaciones del sistema ni resultados de herramientas)
  · los archivos que se escribieron/editaron en la sesión
  · la última lista de tareas (TodoWrite)
  · rama git del directorio
Silencioso: no imprime nada (no ensucia el contexto) y jamás rompe la compactación (siempre exit 0).

Entrada (stdin, JSON): {session_id, transcript_path, cwd, trigger: "manual"|"auto"}
"""
import hashlib
import json
import sys
import time
from pathlib import Path

DIR = Path.home() / ".claude" / "precompact" / "by-cwd"
N_PEDIDOS = 5
MAX_PEDIDO = 320
MAX_ARCHIVOS = 25
RUIDO = ("<system-reminder>", "[SYSTEM NOTIFICATION", "<task-notification", "<command-name>", "<local-command", "Caveat:")


def hash_cwd(cwd):
    return hashlib.sha1(str(cwd).lower().encode("utf-8")).hexdigest()[:10]


def texto_de(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def resumir(transcript):
    pedidos, archivos, todos = [], [], None
    try:
        with open(transcript, "r", encoding="utf-8", errors="replace") as f:
            for linea in f:
                if '"type"' not in linea:
                    continue
                try:
                    o = json.loads(linea)
                except ValueError:
                    continue
                t = o.get("type")
                msg = o.get("message") or {}
                if t == "user" and not o.get("isSidechain"):
                    txt = texto_de(msg.get("content")).strip()
                    if txt and not txt.startswith(RUIDO):
                        pedidos.append(" ".join(txt.split())[:MAX_PEDIDO])
                elif t == "assistant":
                    contenido = msg.get("content")
                    for b in contenido if isinstance(contenido, list) else []:
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        nombre, entrada = b.get("name"), b.get("input") or {}
                        if nombre in ("Write", "Edit", "NotebookEdit", "MultiEdit"):
                            ruta = entrada.get("file_path") or entrada.get("notebook_path")
                            if ruta and "\Temp\claude\\" not in str(ruta) and "/scratchpad/" not in str(ruta).replace("\\", "/"):
                                archivos.append(str(ruta))   # los temporales del scratchpad son ruido
                        elif nombre == "TodoWrite" and isinstance(entrada.get("todos"), list):
                            todos = entrada["todos"]
    except OSError:
        pass
    vistos, unicos = set(), []
    for a in reversed(archivos):          # los más recientes primero, sin repetir
        if a not in vistos:
            vistos.add(a); unicos.append(a)
    return pedidos[-N_PEDIDOS:], unicos[:MAX_ARCHIVOS], todos


def rama_git(cwd):
    try:
        cabeza = (Path(cwd) / ".git" / "HEAD").read_text(encoding="utf-8").strip()
        return cabeza.removeprefix("ref: refs/heads/") if cabeza.startswith("ref:") else cabeza[:12]
    except OSError:
        return None


def main():
    try:
        ev = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
        transcript, cwd = ev.get("transcript_path"), ev.get("cwd") or ""
        if not transcript or not cwd or not Path(transcript).exists():
            return 0
        pedidos, archivos, todos = resumir(transcript)
        if not pedidos and not archivos:
            return 0
        md = [f"# Checkpoint previo a compactar ({ev.get('trigger', '?')})",
              f"- sesión: {str(ev.get('session_id', ''))[:8]} · {time.strftime('%Y-%m-%d %H:%M')} · cwd: {cwd}"]
        rama = rama_git(cwd)
        if rama:
            md.append(f"- rama git: {rama}")
        if pedidos:
            md.append("\n## Últimos pedidos del usuario (más reciente al final)")
            md += [f"{i + 1}. {p}" for i, p in enumerate(pedidos)]
        if archivos:
            md.append("\n## Archivos escritos/editados en la sesión (recientes primero)")
            md += [f"- {a}" for a in archivos]
        if todos:
            md.append("\n## Lista de tareas al compactar")
            md += [f"- [{(t.get('status') or '?')}] {t.get('content', '')}" for t in todos if isinstance(t, dict)]
        DIR.mkdir(parents=True, exist_ok=True)
        (DIR / f"{hash_cwd(cwd)}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    except Exception as e:  # un checkpoint jamás debe romper la compactación
        print(f"[precompact] {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
