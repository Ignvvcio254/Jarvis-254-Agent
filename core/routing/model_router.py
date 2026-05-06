#!/usr/bin/env python3
"""
JARVIS FRAMEWORK - MODEL ROUTER
Core Intelligence Infrastructure

This system classifies incoming user prompts and recommends the most appropriate 
AI model based on the detected intent, balancing speed, cost, and reasoning depth.

Supported modes:
- Chat/Conversational -> Lightweight Model (e.g., Haiku)
- Execution/Coding    -> Mid-tier Model (e.g., Sonnet)
- Design/Analysis     -> Heavy-tier Model (e.g., Opus)
"""

import io
import json
import re
import sys
from typing import Tuple, List, Dict

# Ensure UTF-8 output for cross-platform compatibility
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# --- CONFIGURATION ---
# In a production environment, these could be loaded from a .json or .env file
DEFAULT_CONFIG = {
    "models": {
        "lightweight": "claude-haiku-4-5-20251001",
        "midtier": "claude-sonnet-4-6",
        "heavy": "claude-opus-4-7",
    },
    "routing_rules": {
        "lightweight": {
            "patterns": [
                r"^(hola|hey|buenas|qué tal|cómo estás|cómo vas|cómo andas)",
                r"^(qué es|qué significa|qué hace|qué son)\s+\w+(\s+\w+){0,3}[?]?$",
                r"^(hay|existe|tienes|sabes)\s+",
                r"^(sí|no|ok|claro|entendido|perfecto|dale)[\s.,!]*$",
                r"^(gracias|jaja|xd|bien|mal|más o menos)[\s.,!]*$",
            ],
            "keywords": [
                "cuéntame algo", "qué piensas de", "tu opinión", "me recomiendas",
                "dime un", "dime una", "está?", "y está", "ya está",
                "cómo funciona", "para qué sirve", "qué diferencia hay",
            ],
            "max_words": 30,
            "label": "conversational",
        },
        "heavy": {
            "patterns": [
                r"\b(diseña|arquitectura|estrategia|planifica|propón|evalúa)\b",
                r"\b(investiga|compara opciones|análisis profundo|mejores prácticas)\b",
                r"\b(cómo deberíamos|qué enfoque|qué patrón arquitect|visión general)\b",
                r"\b(roadmap|sprint planning|decisión técnica|trade.?off)\b",
            ],
            "keywords": [
                "arquitectura", "diseño del sistema", "estrategia", "planificación",
                "análisis completo", "evalúa opciones", "compara", "investiga a fondo",
                "propón solución", "cómo deberíamos", "qué modelo usar", "decisión",
            ],
            "label": "deep-reasoning",
        },
        "midtier": {
            "patterns": [
                r"\b(implementa|crea|escribe|arregla|fix|refactoriza|deploy|instala|configura)\b",
                r"\b(código|función|clase|componente|endpoint|api|script|hook|test)\b",
                r"\b(bug|error|excepción|falla|crash|no funciona)\b",
                r"\b(instala|actualiza|migra|configura|despliega)\b",
            ],
            "label": "technical-execution",
        },
    },
}

class ModelRouter:
    def __init__(self, config: Dict = DEFAULT_CONFIG):
        self.config = config
        self.models = config["models"]
        self.rules = config["routing_rules"]

    def _extract_text(self, prompt: str) -> str:
        """Removes XML wrappers from prompts (e.g., from Discord/Telegram integrations)."""
        channel_match = re.search(r'<channel[^>]*>(.*?)</channel>', prompt, re.DOTALL)
        if channel_match:
            return channel_match.group(1).strip()
        return prompt.strip()

    def classify(self, prompt: str) -> Tuple[str, str, str]:
        """
        Classifies the prompt and returns (model_id, tier_label, task_type).
        """
        text = self._extract_text(prompt).lower()
        words = text.split()

        # 1. Check Lightweight (Conversational)
        light = self.rules["lightweight"]
        for pattern in light["patterns"]:
            if re.search(pattern, text) and len(words) <= light["max_words"]:
                return self.models["lightweight"], "lightweight", light["label"]
        for kw in light["keywords"]:
            if kw in text and len(words) <= light["max_words"]:
                return self.models["lightweight"], "lightweight", light["label"]

        # 2. Check Heavy (Deep Reasoning)
        heavy = self.rules["heavy"]
        for pattern in heavy["patterns"]:
            if re.search(pattern, text):
                return self.models["heavy"], "heavy", heavy["label"]
        for kw in heavy["keywords"]:
            if kw in text:
                return self.models["heavy"], "heavy", heavy["label"]

        # 3. Default to Midtier (Technical Execution)
        return self.models["midtier"], "midtier", self.rules["midtier"]["label"]

    def generate_instruction(self, tier: str) -> str:
        """Generates a tailored system instruction based on the routed tier."""
        instructions = {
            "lightweight": "[JARVIS ROUTER] Instruction: Be concise, max 3 sentences. Do not over-elaborate.",
            "heavy": "[JARVIS ROUTER] Instruction: Use deep-reasoning. If delegating to a flow, use model='heavy'.",
            "midtier": "[JARVIS ROUTER] Instruction: Direct technical execution. Proceed normally.",
        }
        return instructions.get(tier, "")

def main():
    """Entry point for Claude Code hook execution."""
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        data = json.loads(raw)
        prompt = data.get("prompt", "")
    except Exception:
        sys.exit(0)

    if not prompt:
        sys.exit(0)

    router = ModelRouter()
    model_id, tier, task_type = router.classify(prompt)
    instruction = router.generate_instruction(tier)

    # Format for the agent's context
    output = (
        f"[JARVIS ROUTER] Detected Task: {task_type}\n"
        f"[JARVIS ROUTER] Recommended Model: {tier} ({model_id})\n"
        f"{instruction}\n"
    )
    
    print(output, end="")
    sys.exit(0)

if __name__ == "__main__":
    main()
