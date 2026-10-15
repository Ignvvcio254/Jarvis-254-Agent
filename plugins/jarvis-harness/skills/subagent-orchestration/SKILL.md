---
name: subagent-orchestration
description: Orquestar subagentes (Agent/Task) con context firewall, patrón fan-out→synthesize y grader por rúbrica (Performance Outcomes). Usar cuando una tarea es masivamente paralela, larga, o se beneficia de context windows aislados — investigación multi-fuente, refactor multi-archivo, revisión multi-perspectiva, benchmark de N combinaciones. Complementa multi-cli (CLIs externos) con subagentes Claude internos.
---

# subagent-orchestration — Paralelismo con aislamiento y grader

> Harness Jarvis-UPLIFT (extensión frontier). Porta los patrones de Anthropic
> Dynamic Workflows + Performance Outcomes (jun 2026, +10pts en benchmarks duros)
> y el "context firewall" de subagentes (Claude Code 2026).

## La doctrina de 4 capas (comunidad, validada)

| Capa | Componente | Rol | Cuándo |
|---|---|---|---|
| 1 | CLAUDE.md | reglas/memoria | siempre |
| 2 | Skills | procedimiento reutilizable inline | tarea repetible en el mismo contexto |
| 3 | Hooks | enforcement determinista | regla que SIEMPRE debe dispararse |
| 4 | **Subagentes** | aislamiento + paralelo | trabajo que ensuciaría el contexto principal |

Regla de decisión: **"Skill enseña · Hook impone · Subagente aísla"**. Se combinan.

## Cuándo usar un subagente (no inline)

Usar `Agent`/`Task` cuando:
- La tarea generaría ruido que no volverás a mirar (búsquedas, logs, lecturas masivas) → **context firewall**: el principal solo ve el resumen.
- Es masivamente paralela (N fuentes, N archivos, N combinaciones).
- Cada paso se beneficia de un context window limpio (no cross-contaminación).
- Es adversarial (generar vs verificar deben estar separados — ver grader).

NO usar subagente para: ediciones pequeñas, tareas de 1 archivo, cosas donde el costo de coordinar > el de hacerlo inline. (3-5 subagentes concurrentes es el punto óptimo; más, gastas más mergeando que ahorrando.)

## Patrón 1 — Fan-out → Synthesize

Para tareas con muchos sub-pasos independientes:

```
LEAD (Opus/Jarvis)
  ├─ fan-out: N subagentes Explore (Haiku, baratos) en paralelo
  │    cada uno: una fuente / un módulo / una hipótesis · context window propio
  ├─ barrera: esperar a TODOS
  └─ synthesize: 1 subagente (Opus) o Jarvis fusiona los resúmenes estructurados
```

Routing de modelo ([[token-router]]): explorar = Haiku/gemma (barato, paralelo);
sintetizar = Opus (donde se justifica el razonamiento). Ahorro real: el grueso del
trabajo corre en el tier barato; solo la síntesis usa el caro.

Ejemplo: investigación multi-fuente, mapeo de codebase grande, refactor de N archivos
independientes, benchmark de N modelos×prompts.

## Patrón 2 — Grader por rúbrica (Performance Outcomes)

El verify-repair objetivo (exit code) cubre tareas binarias. Para tareas con calidad
graduable, añadir un **grader separado**:

```
GENERADOR (subagente A) → produce el entregable
        ↓
GRADER (subagente B, distinto) → evalúa contra una RÚBRICA explícita
        ↓
  ¿cumple? → aceptar
  ¿no?     → devolver al generador con el gap específico → revisar (máx N)
```

Reglas:
- El grader es un subagente DISTINTO del generador (MAR: el mismo se estanca).
- La rúbrica es explícita y se escribe ANTES: ej. "todos los tests pasan · sin TODOs
  nuevos · sin cambios de API pública · cobertura ≥ 80%".
- Donde se pueda, la rúbrica se ancla en señal objetiva ([[verify-repair]]
  `verify-gate.ps1`): el grader corre el gate y lee el verdict, no opina.
- Esto es lo que Anthropic llama Performance Outcomes (+10pts en sus benchmarks duros).

## Patrón 3 — SubagentStop gate

Cuando un subagente termina, su salida NO se acepta sin pasar el gate:
- Si la tarea fue de código → correr `verify-gate.ps1` sobre su output (exit 0 obligatorio).
- Si falla → re-despachar al subagente con el gap (additionalContext), no aceptar el resumen.
- Es el equivalente subagente del check `edited`+verdict de multi-cli.

## Integración con el harness

| Skill | Rol en la orquestación |
|---|---|
| [[token-router]] | Haiku para fan-out, Opus para synthesize — el ahorro |
| [[verify-repair]] | señal objetiva del grader y del SubagentStop gate |
| `agent-uplift` SPEC-COMPILER | cada subagente recibe una spec one-shot compilada |
| [[scratchpad]] | registra qué subagente hizo qué + correcciones |
| `multi-cli` | hermano externo: CLIs (AGY/OpenCode) en vez de subagentes Claude. Elegir según: subagente=contexto Claude aislado · multi-cli=modelos de otros proveedores en terminales visibles |

## Subagente vs multi-cli (cuándo cada uno)

- **Subagente** (`Agent`/`Task`): trabajo Claude que necesita context firewall, dentro de la sesión. El lead ve solo el resumen.
- **multi-cli** (AGY/OpenCode): delegar a modelos de OTROS proveedores en terminales visibles que el usuario supervisa, resiliencia multi-proveedor.

## Verificación de este skill

- Una tarea de investigación: 3 subagentes Explore en paralelo + 1 synthesize → reporte citado.
- Una tarea de código con grader: generador + grader separado corriendo verify-gate.

## Anti-patrón

Spawnar >5 subagentes para todo "por paralelizar": el costo de mergear resúmenes supera
el ahorro. Fan-out masivo solo cuando la tarea genuinamente se abre (N fuentes/archivos).