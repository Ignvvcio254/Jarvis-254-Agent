#!/usr/bin/env python3
"""
JARVIS CORRECTION DETECTOR — automatiza la correction-detection del skill
scratchpad (F3). Porta el patrón de prax-agent.

Como UserPromptSubmit hook, examina cada mensaje del usuario. Si detecta
una corrección (frases tipo "no, mejor", "está mal", "ya te dije", "otra vez"),
inyecta un recordatorio para que Jarvis extraiga el patrón problema→solución y
lo guarde en su capa-hogar (memory/ feedback, antipatterns, o cerebro) — en vez
de dejar la corrección morir en la conversación.

"Conocimiento solo-en-conversación = conocimiento muerto" (doctrina Mythos).

Uso (settings.json UserPromptSubmit):
  { "type": "command", "command": "python ~/.claude/scripts/correction_detector.py" }

Lee {prompt} por stdin. Salida:
  - sin corrección → exit 0 silencioso
  - con corrección → additionalContext recordando guardar el patrón
"""
import json
import re
import sys

# Señales de corrección en español (el usuario corrige o reitera).
PATTERNS = [
    r"\bno,?\s+(mejor|en realidad|así no|eso no)\b",
    r"\b(está|esta)\s+mal\b",
    r"\bno\s+es\s+(así|asi|correcto|lo que)\b",
    r"\bte\s+equivocaste\b",
    r"\bya\s+te\s+(dije|hab[ií]a dicho)\b",
    r"\botra\s+vez\s+(lo mismo|el mismo)\b",
    r"\b(recuerda|acordate|acu[eé]rdate)\s+que\b",
    r"\bno\s+(hagas|vuelvas a|quiero que)\b",
    r"\b(siempre|nunca)\s+(haz|hagas|uses|pongas)\b",
    r"\bte\s+(dije|ped[ií])\s+que\b",
    r"\beso\s+(no era|no es lo que)\b",
    r"\bmal\s+ah[ií]\b",
]


def extract_text(prompt: str) -> str:
    m = re.search(r"<channel[^>]*>(.*?)</channel>", prompt, re.DOTALL)
    return (m.group(1) if m else prompt).strip()


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except Exception:
        sys.exit(0)
    prompt = extract_text(data.get("prompt", "")).lower()
    if not prompt:
        sys.exit(0)

    hit = next((p for p in PATTERNS if re.search(p, prompt)), None)
    if not hit:
        sys.exit(0)

    msg = (
        "[correction-detector] Detecté una posible CORRECCIÓN del usuario. "
        "Antes de continuar, aplica el skill scratchpad (F3): "
        "1) extrae el patrón problema→solución (qué hice mal, qué debí hacer); "
        "2) guárdalo en su capa-hogar (memory/ tipo feedback si es sobre cómo trabajar, "
        "antipatterns/<modelo> si es de un worker, cerebro si es decisión de sesión); "
        "3) confirma en una línea: 'Anotado: <regla> — no se repetirá'. "
        "No dejes la corrección solo en la conversación."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()