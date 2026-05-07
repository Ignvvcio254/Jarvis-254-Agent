---
name: antigravity-bridge
description: Coordinar trabajo entre Jarvis (Claude Code), Antigravity IDE y GitHub Copilot CLI usando el sistema de archivos como canal compartido.
---

# Antigravity Bridge — Protocolo Jarvis ↔ Antigravity ↔ Copilot CLI

## Propósito
Coordinar trabajo entre Jarvis (Claude Code) y los agentes de Antigravity IDE y GitHub Copilot CLI, usando el sistema de archivos como canal de comunicación compartido. Jarvis orquesta, mantiene memoria y decide qué herramienta usar para cada tarea.

---

## Mapa de modelos disponibles

### Jarvis — Claude Code CLI
| Modelo | Cuándo usar |
|---|---|
| `claude-sonnet-4-6` | Ejecución técnica, código, tareas con contexto de memoria |
| `claude-opus-4-7` | Plan mode, razonamiento arquitectónico complejo |
| `claude-haiku-4-5` | Conversación rápida, respuestas breves |

### Antigravity IDE (pool propio — sin API key adicional)
| Modelo | Cuándo delegar |
|---|---|
| Gemini 3 Flash | Boilerplate, completado rápido, preguntas simples |
| Gemini 3.1 Pro Low | Código rutinario diario, tareas livianas |
| Gemini 3.1 Pro High | Refactor complejo, análisis profundo dentro del IDE |
| **Claude Sonnet 4.6** | Code review, código de precisión media |
| **Claude Opus 4.6** | Análisis de codebase grande, documentación extensa |

### GitHub Copilot CLI (cuenta Ignvvcio254 — sin API key adicional)
| Modelo | Cuándo delegar |
|---|---|
| `claude-opus-4.5` | Tareas CLI complejas, debugging profundo, arquitectura |
| `claude-sonnet-4.5` | Tareas CLI rutinarias, ediciones rápidas en terminal |
| `gpt-5.2-codex` | Code review de alto volumen, segunda opinión |

> Config: `~/.copilot/config.json` (modelo activo: `claude-sonnet-4.5`)
> Cambiar modelo: `gh copilot config set model claude-opus-4.5`

---

## Protocolo de decisión — ¿qué herramienta usar?

```
¿La tarea necesita contexto de cerebro/mem0/CLAUDE.md?
├── SÍ → Jarvis la ejecuta directamente
└── NO → ¿Es tarea de IDE (editar archivos en proyecto)?
    ├── SÍ → Antigravity (seleccionar modelo según complejidad)
    └── NO → ¿Es tarea de terminal/CLI/git?
        └── SÍ → Copilot CLI (seleccionar modelo según complejidad)
```

### Tabla rápida de delegación
| Tipo de tarea | Herramienta | Modelo |
|---|---|---|
| Orquestación, memoria, cerebro | Jarvis | Sonnet 4.6 |
| Plan arquitectónico | Jarvis plan mode | Opus 4.7 |
| Boilerplate / CRUD rápido | Antigravity | Gemini Flash |
| Code review en IDE | Antigravity | Claude Sonnet 4.6 |
| Análisis de codebase completo | Antigravity | Claude Opus 4.6 |
| Comandos CLI complejos | Copilot CLI | Claude Opus 4.5 |
| Git / GitHub workflows | Copilot CLI | Claude Sonnet 4.5 |
| Segunda opinión de código | Copilot CLI | GPT-5.2 Codex |

---

## Estructura de handoff en proyectos

Todo proyecto con integración Jarvis↔Antigravity usa la carpeta `.agent/` en la raíz:

```
proyecto/
├── .agent/
│   ├── CONTEXT.md      ← contexto del proyecto para ambos agentes
│   ├── HANDOFF.md      ← instrucciones para el siguiente agente
│   ├── PROGRESS.md     ← log append-only de avances
│   └── DECISIONS.md    ← decisiones arquitectónicas tomadas
├── GEMINI.md           ← instrucciones sistema para agente Antigravity
└── (código del proyecto)
```

---

## Protocolo de delegación (Jarvis → Antigravity)

1. Escribir en `.agent/HANDOFF.md` con:
   - Tarea específica con contexto autocontenido
   - Archivos relevantes a modificar
   - Modelo recomendado para esta tarea
   - Criterio de completitud

2. Abrir Antigravity en el proyecto y decirle: `"Lee .agent/HANDOFF.md y ejecuta la tarea con [modelo]"`

3. Antigravity escribe resultado en `.agent/PROGRESS.md`

4. Jarvis lee PROGRESS.md al retomar e ingesta en cerebro si aplica

---

## Protocolo de delegación (Jarvis → Copilot CLI)

Para tareas en terminal:
```bash
gh copilot chat "Lee .agent/HANDOFF.md del proyecto en [ruta] y ejecuta la tarea"
```

O cambiar modelo temporalmente:
```bash
gh copilot config set model claude-opus-4.5  # para tarea compleja
gh copilot chat "[instrucción autocontenida]"
gh copilot config set model claude-sonnet-4.5  # restaurar
```

---

## Template HANDOFF.md

```markdown
# Handoff — [fecha]
**De:** Jarvis
**Para:** [Antigravity | Copilot CLI]
**Modelo sugerido:** [Gemini Flash | Claude Sonnet 4.6 | Claude Opus 4.6 | Claude Opus 4.5]

## Tarea
[descripción específica y autocontenida]

## Contexto
[archivos relevantes, estado actual — NO asumir que el agente tiene contexto previo]

## Criterio de completitud
- [ ] [criterio 1]
- [ ] [criterio 2]

## No tocar
[archivos o áreas fuera de scope]
```

---

## MCPs compartidos entre herramientas

Todos los agentes tienen acceso a los mismos MCPs base:
- **Jarvis:** `~/.claude.json` (completo — 20+ servidores)
- **Antigravity:** `~/.gemini/antigravity/mcp_config.json` (filesystem + github)
- **Copilot CLI:** `~/.copilot/mcp-config.json` (filesystem + github)

---

## CLIs de Antigravity disponibles

- `antigravity` v1.107.0 — CLI principal
- `agk` (antigravity-kit) — gestión cuentas/workspaces: `npm install -g antigravity-kit`
- `antigravity-usage` — monitoreo cuota: `npm install -g antigravity-usage`

## CLI de Copilot disponibles
- `gh copilot chat` — conversación agentic
- `gh copilot explain` — explicar código/comandos
- `gh copilot suggest` — sugerir comandos de terminal
- `gh copilot config` — cambiar modelo y configuración

---

## Reglas del puente

1. Jarvis NUNCA delega tareas que requieran contexto de cerebro/mem0 — ese contexto no llega a otros agentes
2. Los agentes delegados trabajan con contexto frío — HANDOFF.md debe ser autocontenido
3. Jarvis ingesta en cerebro las decisiones importantes de los agentes delegados
4. `.agent/DECISIONS.md` es la fuente de verdad de decisiones arquitectónicas
5. Cambios de modelo en Copilot CLI se restauran después de la tarea delegada
