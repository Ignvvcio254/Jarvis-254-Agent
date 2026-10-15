---
name: scratchpad
description: Memoria de trabajo de Jarvis — notas propias durante tareas largas + detección de correcciones del usuario + propagación a las 5 capas de memoria. Resuelve la fragmentación (conocimiento que vive en una sola capa). Activar en tareas multi-fase, al recibir una corrección, o al cerrar una sesión significativa.
---

# scratchpad — Notas propias + correction-detection + propagación

> Harness Jarvis-UPLIFT (F3). Réplica de la capacidad de Fable 5 "improves its outputs
> using its own notes" (dio 3× mejora). Porta correction-detection de prax-agent.
> Resuelve de raíz la fragmentación de memoria diagnosticada el 2026-06-16.

## Las tres funciones

### 1. Scratchpad de tarea (notas propias durante trabajo largo)

En toda tarea multi-fase, mantener un archivo de notas vivo en `.scratch/task.md` del
proyecto. No es para el usuario — es la memoria de trabajo de Jarvis.

Qué registrar (append, nunca reescribir):
- Decisiones tomadas y su porqué
- Qué se intentó y falló (para no repetirlo en la misma tarea)
- Estado actual: qué está hecho, qué falta
- Hallazgos de contexto (archivos clave, patrones del proyecto)

Por qué: en tareas largas el modelo re-deriva contexto que ya sabía → desperdicia
tokens y comete errores. Releer las notas propias evita ambos. Al retomar tras una
interrupción, leer `.scratch/task.md` PRIMERO.

### 2. Correction-detection (cuando el usuario corrige)

Disparadores — el usuario dice algo como:
- "no, mejor...", "eso está mal", "no es así", "te equivocaste"
- "ya te dije que...", "otra vez lo mismo", "recuerda que..."
- "no hagas X", "siempre haz Y", "prefiero Z"
- corrige un output, revierte algo, repite una instrucción previa

Al detectar una corrección:
1. Extraer el patrón **problema → solución** (qué hice mal, qué debí hacer)
2. Clasificar el alcance (tabla abajo) y guardarlo en la capa correcta
3. Confirmar brevemente: "Anotado: [regla] — no se repetirá."

NUNCA dejar una corrección solo en la conversación. Conversación = conocimiento muerto.

### 3. Propagación a las 5 capas (el fix de la fragmentación)

Cada tipo de conocimiento tiene UNA capa-hogar. No escribir en todas; escribir en la
correcta según esta matriz:

| Tipo de conocimiento | Capa-hogar | Cómo |
|---|---|---|
| Notas de trabajo de la tarea actual | `.scratch/task.md` | append directo |
| Corrección de comportamiento (cómo trabajar) | `memory/` tipo `feedback` | nodo nuevo + MEMORY.md |
| Anti-patrón de un modelo/worker | `agent-uplift/antipatterns/` | append al archivo del modelo |
| Decisión/output de sesión significativa | `cerebro/` vía `/memoria ingest` | nodo de sesión + index |
| Entidad/relación durable (sistema, skill, proyecto) | `memory MCP` (grafo) | create_entities + relations |
| Hecho del proyecto no derivable del código | `memory/` tipo `project` | nodo nuevo + MEMORY.md |

Regla de oro de propagación: **al cerrar una sesión significativa, recorrer la matriz**
y asegurar que cada conocimiento nuevo llegó a su capa-hogar. Eso evita que algo viva
solo en una capa (la fragmentación que se diagnosticó: trabajo de junio solo en
`memory/`, ausente de cerebro/grafo/mem0).

## Degradación

Si `mem0` o `memory MCP` están caídos → escribir en las capas de archivo (`.scratch`,
`memory/`, `cerebro/`) que nunca fallan. No bloquear por un MCP caído (regla de
degradación de CLAUDE.md). Marcar en el nodo de sesión qué capa quedó pendiente.

## Integración con verify-repair

El scratchpad registra el resultado del [[verify-repair]] gate por tarea: nivel de
modelo usado ([[token-router]]), si el gate pasó a la primera, cuántos intentos de
repair. Eso alimenta la métrica de economía (tokens por tarea exitosa) y los
anti-patrones (si un modelo falla repetido el mismo check → anti-patrón).

## Verificación de este skill

- Crear `.scratch/task.md`, append 2 notas, confirmar persistencia.
- Simular una corrección → verificar que se crea el nodo `feedback` en `memory/` y se
  actualiza MEMORY.md.

## Relación

Cierra el harness con [[verify-repair]] (F1) y [[token-router]] (F2). El conocimiento
que produce alimenta `agent-uplift` (anti-patrones) y `jarvis-evolve` (automejora).
Usa el sistema `/memoria` existente para la capa cerebro — no lo duplica.