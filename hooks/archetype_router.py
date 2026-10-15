#!/usr/bin/env python3
"""
JARVIS ARCHETYPE ROUTER — autopilot del MOTOR DE DECISIÓN (UserPromptSubmit hook).

Automatiza la clasificación de la tarea entrante en uno de los arquetipos del
CLAUDE.md e inyecta qué skills del núcleo activar — para que Jarvis no dependa de
recordar el motor de decisión, el sistema se lo recuerda en cada mensaje relevante.

Solo dispara cuando detecta una tarea de ingeniería (no en charla trivial), para
no ensuciar conversaciones casuales.

Uso (settings.json UserPromptSubmit):
  { "type": "command", "command": "python ~/.claude/scripts/archetype_router.py" }
"""
import json
import re
import sys

# arquetipo -> (patrones, skills/herramientas núcleo sugeridas)
ARCHETYPES = [
    ("BUILD", r"\b(crea|construye|implementa|agrega|nueva feature|nuevo (componente|endpoint|módulo)|desarrolla)\b",
     "token-router (modelo por dificultad) → spec-compiler (agent-uplift) → verify-repair (gate). Subagentes si es multi-archivo."),
    ("FIX", r"\b(arregla|fix|corrige|bug|error|falla|no funciona|rompe|crashea)\b",
     "verify-repair PRIMERO (reproducir el fallo objetivamente) → fix → re-verificar. Crítico ≠ generador si no converge."),
    ("DESIGN", r"\b(diseña|mockup|ui|interfaz|landing|pantalla|estética|componente visual)\b",
     "stitch-design / emil-design-eng + web-accessibility. verify con playwright screenshot."),
    ("RESEARCH", r"\b(investiga|compara|analiza opciones|documentación|qué librería|busca cómo)\b",
     "subagent-orchestration (fan-out Explore en paralelo → synthesize). exa/context7/firecrawl."),
    ("TEST", r"\b(test|prueba|e2e|cobertura|tdd|valida)\b",
     "verify-repair + playwright/pytest. Veredicto objetivo, no claim."),
    ("DEPLOY", r"\b(deploy|despliega|producción|vercel|docker|build de prod)\b",
     "verify-repair (smoke test) + multi-cli si es a escala. Confirmar antes de acción irreversible."),
    ("DATA", r"\b(query|migración|esquema|base de datos|sql|prisma|tabla)\b",
     "buscar-skill(ORM) + verify-repair. Confirmar antes de migración destructiva."),
    ("SWARM", r"\b(en paralelo|múltiples archivos|todo el codebase|a escala|varios agentes)\b",
     "subagent-orchestration (fan-out/synthesize + grader) o multi-cli (AGY/OpenCode). 3-5 concurrentes óptimo."),
]

# No disparar en charla trivial
TRIVIAL = re.compile(r"^(hola|hey|buenas|gracias|ok|dale|sí|no|jaja|qué tal|cómo (estás|vas))",
                     re.IGNORECASE)


def extract_text(prompt: str) -> str:
    m = re.search(r"<channel[^>]*>(.*?)</channel>", prompt, re.DOTALL)
    return (m.group(1) if m else prompt).strip()


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except Exception:
        sys.exit(0)
    text = extract_text(data.get("prompt", ""))
    low = text.lower()
    if not text or TRIVIAL.match(low) or len(low.split()) < 3:
        sys.exit(0)

    matched = [(name, skills) for name, pat, skills in ARCHETYPES if re.search(pat, low)]
    if not matched:
        sys.exit(0)

    # máx 2 arquetipos (regla de tareas mixtas del CLAUDE.md)
    matched = matched[:2]
    lines = [f"- **{name}** → {skills}" for name, skills in matched]
    msg = (
        "[archetype-router] Tarea de ingeniería detectada. Motor de decisión sugiere:\n"
        + "\n".join(lines)
        + "\nRecuerda: veredicto objetivo antes de reportar (verdict_guard lo impone al cerrar)."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()