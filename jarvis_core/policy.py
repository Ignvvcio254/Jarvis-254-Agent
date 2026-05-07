from __future__ import annotations


def recommend_workflow(intent: str) -> dict[str, list[str] | str]:
    text = intent.lower().strip()

    if any(term in text for term in ("bug", "error", "fix", "falla")):
        return {
            "track": "FIX+TEST",
            "commands": ["/memoria", "/doctor"],
            "read_first": ["RULES.md", "COMMANDS.md", "SAAS_FACTORY.md"],
            "next": "Diagnosticar causa raiz, aplicar fix minimo, validar y registrar en memoria.",
        }

    if any(term in text for term in ("feature", "nueva", "agregar", "build")):
        return {
            "track": "BUILD(+DATA/+TEST)",
            "commands": ["/ag-project", "/memoria", "/consumo"],
            "read_first": ["SAAS_FACTORY.md", "PRPs/README.md", "RULES.md"],
            "next": "Generar PRP, ejecutar por fases y cerrar con verificacion tecnica.",
        }

    if any(term in text for term in ("ui", "dise", "frontend", "screen")):
        return {
            "track": "DESIGN+BUILD",
            "commands": ["/memoria", "/consumo"],
            "read_first": ["DESIGN_SYSTEMS.md", "RULES.md", "COMMANDS.md"],
            "next": "Definir direccion visual, implementar iterativo y validar responsive/a11y.",
        }

    return {
        "track": "RESEARCH",
        "commands": ["/memoria", "/doctor"],
        "read_first": ["README.md", "COMMANDS.md", "RULES.md"],
        "next": "Aclarar objetivo, mapear contexto y proponer plan minimo reversible.",
    }
