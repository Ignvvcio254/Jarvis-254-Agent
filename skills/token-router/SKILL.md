---
name: token-router
description: Decide el modelo MÍNIMO suficiente para cada tarea/subtarea antes de ejecutar o delegar. Ahorro de tokens por dificultad — no usar el modelo más potente por defecto. Trivial→Haiku/gemma(gratis), estándar→Sonnet, complejo→Opus. Activar al planificar trabajo, al delegar a workers (AGY/OpenCode), o ante cualquier tarea con costo de tokens relevante.
---

# token-router — El modelo mínimo suficiente, no el más potente

> Harness Jarvis-UPLIFT (F2). Porta el CostAwareRouter de `grind` (Opus planea,
> Haiku ejecuta, 3-5× ahorro) + la evidencia de test-time scaling (modelo pequeño +
> verificación = nivel frontier; arxiv 2408.03314, 2502.06703).

## El principio

No usar el modelo más potente por defecto. Usar el **mínimo suficiente** para la
dificultad real de la tarea. El ahorro grande del harness vive aquí.

Funciona porque el [[verify-repair]] gate respalda al modelo barato: si gemma falla,
el veredicto objetivo lo detecta y se repara. Sin verify-repair, modelo barato =
riesgo. Con él, modelo barato = barato Y confiable. **El router depende del gate.**

## Las dos dimensiones de routing

Jarvis ya tiene `model_router.py` (hook UserPromptSubmit) que adapta el COMPORTAMIENTO
de la sesión (brevedad/profundidad). Este skill cubre la otra dimensión: **a quién
DELEGAR el trabajo de ejecución** (Jarvis mismo o un worker, y con qué modelo).

| Dimensión | Quién la maneja | Qué decide |
|---|---|---|
| Comportamiento de sesión | `model_router.py` (hook) | Brevedad vs profundidad de Jarvis |
| **Delegación de trabajo** | **este skill** | **Jarvis directo vs worker, y qué modelo** |

## Matriz de decisión (dificultad → motor → costo)

| Nivel | Señales de la tarea | Motor | Costo relativo |
|---|---|---|---|
| **Trivial** | rename, formato, lookup, edición 1-3 líneas, búsqueda, parse | Haiku 4.5 / **gemma (OpenCode, gratis)** | ~1× |
| **Estándar** | función nueva, CRUD, fix acotado, refactor 1 archivo, test unitario | Sonnet 4.6 | ~12× Haiku |
| **Complejo** | arquitectura, debug multi-archivo, tarea larga, razonamiento encadenado, decisión de diseño | Opus 4.8 | ~60× Haiku |

Precios de referencia (Claude API, por 1M tokens output): Haiku ~$1.25 · Sonnet ~$15 · Opus ~$75.

## Clasificación de dificultad (cómo decidir)

Subir de nivel SOLO si hay señal real. Señales de COMPLEJO (cualquiera basta):
- Toca ≥3 archivos coordinados
- Requiere razonamiento encadenado >3 pasos
- Decisión arquitectónica o trade-off
- Tarea larga / multi-fase
- Debugging de causa raíz no obvia

Señales de TRIVIAL (todas deben cumplirse):
- 1 archivo, cambio acotado
- Sin decisión de diseño
- Resultado verificable mecánicamente (lint/grep/parse)

Default si hay duda entre dos niveles: el MENOR + verify-repair. Si el gate falla y
el repair no converge en 2 intentos → subir un nivel (escalada por evidencia, no por
precaución).

## Routing a workers (integración con multi-cli)

Al delegar trabajo paralelo o de escala:

| Tarea | Worker + modelo |
|---|---|
| Lote trivial paralelo (formato, generación repetitiva) | OpenCode + gemma (gratis) |
| Módulo estándar contra contrato de interfaz | OpenCode + sonnet, o AGY |
| Componente complejo / refactor delicado | AGY + Opus (settings.json) |

Regla de oro: **todo worker entrega con `verify-gate.ps1` exit 0**, sin importar su
modelo. El gate es lo que permite confiar en gemma.

## Métrica de éxito (lo que medimos)

Tokens gastados por tarea completada con éxito. Éxito = "funciona (gate pass) Y costó
menos que hacerlo con Opus a pelo". Registrar en el scratchpad de la tarea: nivel
asignado, motor usado, si el gate pasó a la primera, intentos de repair.

## Anti-patrón a evitar

"Por las dudas uso Opus" → desperdicia 60× tokens en tareas triviales. La cautela
correcta no es el modelo caro: es el verify-repair gate sobre el modelo barato.

## Relación

Depende de [[verify-repair]] (sin gate objetivo no se puede bajar de modelo).
Se integra con `multi-cli` (delegación) y el spec-compiler de `agent-uplift`
(spec limpia hace que el modelo barato rinda como uno caro).