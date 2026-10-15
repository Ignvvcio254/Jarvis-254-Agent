#!/usr/bin/env python3
"""
JARVIS ARCHETYPE ROUTER — autopilot for the DECISION ENGINE (UserPromptSubmit hook).

Classifies the incoming task into one of the CLAUDE.md archetypes (BUILD, FIX, ...)
and injects which core skills to activate, so the agent does not depend on
remembering the decision engine. Bilingual detection (English / Spanish).

Only fires on engineering tasks, never on small talk.

Usage (settings.json UserPromptSubmit):
  { "type": "command", "command": "python ~/.claude/scripts/archetype_router.py" }
"""
import json
import re
import sys

# archetype -> (pattern, suggested core skills)
ARCHETYPES = [
    ("BUILD",
     r"\b(create|build|implement|add|new feature|scaffold|develop|crea|construye|implementa|agrega|nueva feature|nuevo (componente|endpoint|módulo)|desarrolla)\b",
     "token-router (model by difficulty) → spec compiler (agent-uplift) → verify-repair (gate). Subagents if multi-file."),
    ("FIX",
     r"\b(fix|debug|bug|error|broken|crash|crashes|not working|failing|arregla|corrige|falla|no funciona|rompe|crashea)\b",
     "verify-repair FIRST (reproduce the failure objectively) → fix → re-verify. Critic ≠ generator if it doesn't converge."),
    ("DESIGN",
     r"\b(design|mockup|ui|ux|layout|landing|screen|styling|diseña|interfaz|pantalla|estética|componente visual)\b",
     "frontend design skills + web-accessibility. Verify with a playwright screenshot."),
    ("RESEARCH",
     r"\b(research|investigate|compare|which library|how to|investiga|compara|analiza opciones|documentación|qué librería|busca cómo)\b",
     "subagent-orchestration (parallel Explore fan-out → synthesize) + official docs (context7)."),
    ("TEST",
     r"\b(test|tests|testing|e2e|coverage|tdd|validate|prueba|cobertura|valida)\b",
     "verify-repair + playwright/pytest. Objective verdict, not a claim."),
    ("DEPLOY",
     r"\b(deploy|deployment|ship|release|production|docker|despliega|producción|build de prod)\b",
     "verify-repair (smoke test). Confirm before any irreversible action."),
    ("DATA",
     r"\b(query|migration|schema|database|sql|prisma|table|migración|esquema|base de datos|tabla)\b",
     "the ORM/database skill + verify-repair. Confirm before a destructive migration."),
    ("SWARM",
     r"\b(in parallel|many files|whole codebase|at scale|multiple agents|en paralelo|múltiples archivos|todo el codebase|a escala|varios agentes)\b",
     "subagent-orchestration (fan-out/synthesize + grader) or multi-cli. 3-5 concurrent is optimal."),
]

# Do not fire on small talk
TRIVIAL = re.compile(
    r"^(hola|hey|hi|hello|thanks|thank you|buenas|gracias|ok|dale|sí|yes|no|jaja|lol|qué tal|cómo (estás|vas))(\W|$)",
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

    matched = matched[:2]  # max 2 archetypes (mixed-task rule in CLAUDE.md)
    lines = [f"- **{name}** → {skills}" for name, skills in matched]
    msg = (
        "[archetype-router] Engineering task detected. Decision engine suggests:\n"
        + "\n".join(lines)
        + "\nReminder: objective verdict (verify-gate) before reporting done; verdict_guard enforces it on Stop."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
