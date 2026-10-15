#!/usr/bin/env python3
"""
JARVIS MODEL ROUTER — UserPromptSubmit hook
Clasifica cada mensaje entrante y recomienda el modelo correcto:
  - charla/conversación   → haiku  (claude-haiku-4-5-20251001)
  - ejecución/código      → sonnet (claude-sonnet-4-6)
  - plan/diseño/análisis  → opus   (claude-opus-4-7)
"""

import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-8"

# Patrones HAIKU — charla rápida y consultas simples
HAIKU_PATTERNS = [
    r"^(hola|hey|buenas|qué tal|cómo estás|cómo vas|cómo andas)",
    r"^(qué es|qué significa|qué hace|qué son)\s+\w+(\s+\w+){0,3}[?]?$",
    r"^(hay|existe|tienes|sabes)\s+",
    r"^(sí|no|ok|claro|entendido|perfecto|dale)[\s.,!]*$",
    r"^(gracias|jaja|xd|bien|mal|más o menos)[\s.,!]*$",
]
HAIKU_KEYWORDS = [
    "cuéntame algo", "qué piensas de", "tu opinión", "me recomiendas",
    "dime un", "dime una", "está?", "y está", "ya está",
    "cómo funciona", "para qué sirve", "qué diferencia hay",
]

# Patrones OPUS — planificación, diseño, análisis profundo
OPUS_PATTERNS = [
    r"\b(diseña|arquitectura|estrategia|planifica|propón|evalúa)\b",
    r"\b(investiga|compara opciones|análisis profundo|mejores prácticas)\b",
    r"\b(cómo deberíamos|qué enfoque|qué patrón arquitect|visión general)\b",
    r"\b(roadmap|sprint planning|decisión técnica|trade.?off)\b",
]
OPUS_KEYWORDS = [
    "arquitectura", "diseño del sistema", "estrategia", "planificación",
    "análisis completo", "evalúa opciones", "compara", "investiga a fondo",
    "propón solución", "cómo deberíamos", "qué modelo usar", "decisión",
]

# Patrones SONNET — ejecución técnica (default)
SONNET_PATTERNS = [
    r"\b(implementa|crea|escribe|arregla|fix|refactoriza|deploy|instala|configura)\b",
    r"\b(código|función|clase|componente|endpoint|api|script|hook|test)\b",
    r"\b(bug|error|excepción|falla|crash|no funciona)\b",
    r"\b(instala|actualiza|migra|configura|despliega)\b",
]


def extract_text(prompt: str) -> str:
    """Extrae el texto real del prompt, removiendo wrappers XML de Discord/Telegram."""
    channel_match = re.search(r'<channel[^>]*>(.*?)</channel>', prompt, re.DOTALL)
    if channel_match:
        return channel_match.group(1).strip()
    return prompt.strip()


def classify(prompt: str) -> tuple[str, str, str]:
    """Retorna (model_id, model_short, task_type)."""
    p = extract_text(prompt).lower()
    words = p.split()

    # HAIKU: mensajes cortos + patrones conversacionales
    for pattern in HAIKU_PATTERNS:
        if re.search(pattern, p):
            if len(words) <= 20:
                return HAIKU_MODEL, "haiku", "charla"
    for kw in HAIKU_KEYWORDS:
        if kw in p and len(words) <= 30:
            return HAIKU_MODEL, "haiku", "charla"

    # OPUS: planificación y diseño
    for pattern in OPUS_PATTERNS:
        if re.search(pattern, p):
            return OPUS_MODEL, "opus", "planificación/diseño"
    for kw in OPUS_KEYWORDS:
        if kw in p:
            return OPUS_MODEL, "opus", "planificación/diseño"

    # SONNET: ejecución técnica (default)
    return SONNET_MODEL, "sonnet", "ejecución técnica"


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        prompt = data.get("prompt", "")
    except Exception:
        sys.exit(0)

    if not prompt:
        sys.exit(0)

    model_id, model_short, task_type = classify(prompt)

    # Inyectar clasificación en el contexto que Jarvis ve
    msg = (
        f"[JARVIS ROUTER] Tarea detectada: {task_type}\n"
        f"[JARVIS ROUTER] Modelo recomendado: {model_short} ({model_id})\n"
    )

    if model_short == "haiku":
        msg += "[JARVIS ROUTER] Instrucción: respuesta concisa, máximo 3 oraciones. No elaborar en exceso.\n"
    elif model_short == "opus":
        msg += "[JARVIS ROUTER] Instrucción: usar pensamiento profundo. Si se delega a Claude Flow, spawner con model='opus'.\n"
    else:
        msg += "[JARVIS ROUTER] Instrucción: ejecución directa con Sonnet (modelo actual). Proceder normalmente.\n"

    print(msg, end="")
    sys.exit(0)


if __name__ == "__main__":
    main()
