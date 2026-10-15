#!/usr/bin/env python3
"""PreToolUse (Bash/PowerShell): obliga a CONFIRMAR antes de un borrado masivo.

Doctrina "el Hook impone": la regla "no borrar sin confirmación" no puede depender de mi criterio.
Detecta borrados recursivos / masivos y responde permissionDecision="ask": el usuario ve el
comando y decide; en sesiones sin humano (claude -p, workers) queda denegado y el modelo debe explicar.
Se exime lo desechable: carpetas temporales y artefactos reconstruibles (node_modules, .next, dist, __pycache__).
Falla ABIERTO (si el hook revienta, no bloquea trabajo): un guardia roto no debe tumbar la sesión.
"""
import json
import re
import sys

# --- patrones de borrado masivo ---
RM_RECURSIVO = re.compile(r"(?:^|[;&|(\s])rm\s+(?:-[a-zA-Z]*\s+)*(?:-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)\b")
PS_RECURSIVO = re.compile(r"\b(?:Remove-Item|ri|del|erase|rd|rmdir)\b[^;|\n]*(?:-Recurse\b|\s/s\b)", re.I)
GIT_DESTRUCTIVO = re.compile(r"\bgit\s+(?:clean\s+-[a-zA-Z]*f|reset\s+--hard|checkout\s+--\s+\.|restore\s+(?:--source\S+\s+)?\.)", re.I)

# --- lo desechable: si el comando apunta a esto, no se pregunta ---
DESECHABLE = re.compile(
    r"mktemp|/tmp/|\\Temp\\|\$TEMP\b|\$env:TEMP|\bscratchpad\b|\.scratch\b|node_modules|\.next\b|\bdist\b|__pycache__|\.pytest_cache|\.cache\b|/AppData/Local/Temp",
    re.I,
)


def evaluar(comando: str):
    """Devuelve el motivo si hay que preguntar, o None si se puede seguir."""
    if not comando:
        return None
    destructivo = RM_RECURSIVO.search(comando) or PS_RECURSIVO.search(comando) or GIT_DESTRUCTIVO.search(comando)
    if not destructivo:
        return None
    if DESECHABLE.search(comando) and not GIT_DESTRUCTIVO.search(comando):
        return None
    fragmento = comando.strip().replace("\n", " ")[:160]
    return f"Mass or irreversible deletion: `{fragmento}`. Jarvis rule: confirm with the user FIRST (what gets deleted and whether there is a backup)."


# Herramientas MCP con efecto irreversible o externo (borrar, comprar, fusionar, firmar, enviar formularios, cancelar, reiniciar).
MCP_RIESGO = re.compile(r"^mcp__.+__(?:delete|buy|merge|sign|submit|cancel|terminate|reset|rollback)[a-z_]*$", re.I)
# En modo auto / bypass un "ask" NO detiene la acción (lo documentó un usuario cuyo agente casi firma un contrato): ahí se DENIEGA.
MODOS_SIN_HUMANO = {"auto", "bypasspermissions", "bypass", "dontask"}


def evaluar_herramienta(nombre: str):
    if nombre and MCP_RIESGO.match(nombre):
        return f"Irreversible MCP tool or one with external effects: `{nombre}`. Jarvis rule: confirm with the user BEFORE running it."
    return None


def main() -> int:
    try:
        datos = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
        comando = (datos.get("tool_input") or {}).get("command", "")
        motivo = evaluar(str(comando)) or evaluar_herramienta(str(datos.get("tool_name") or ""))
        modo = str(datos.get("permission_mode") or "").lower()
    except Exception:
        return 0  # falla abierto
    if motivo:
        decision = "deny" if modo in MODOS_SIN_HUMANO else "ask"
        if decision == "deny":
            motivo += " (no human confirmation available: blocked; ask the user to confirm in text)"
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": motivo}}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
