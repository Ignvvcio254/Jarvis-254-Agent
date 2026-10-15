---
name: agent-uplift
description: Sistema para que modelos baratos/libres alcancen RESULTADOS de tarea clase Fable 5 mediante harness (specs compiladas, bucle generate→verify→repair, descomposición, router por evidencia y anti-patrones por modelo). Usar cuando el usuario pida elevar la calidad de workers multi-CLI, ejecutar el benchmark UPLIFT, o cerrar la brecha modelo-barato vs frontier. Deadline del proyecto: 2026-06-22.
---

# AGENT-UPLIFT — resultados clase Fable con cualquier modelo

## Tesis (honesta)

No se puede convertir un modelo de 26B en Fable 5 — los pesos no se tocan. Lo que SÍ se iguala es el **resultado de la tarea**: un modelo barato dentro de un harness disciplinado (spec perfecta + verificación objetiva + reparación acotada + descomposición) produce salidas que pasan la misma revisión que aceptaría una entrega de Fable. La brecha barato-vs-frontier en tareas agénticas es mayormente de **contexto, verificación y reintento** — no de inteligencia bruta. Eso es harness, y el harness es nuestro.

Evidencia semilla (sesión 2026-06-09/10, banco de pruebas Zombies War):
- gemma falló QA sobre archivo 71KB (sesión agotada) → con continuación `-c` + check de entregable, lo completó.
- Opus 4.6 one-shot entregó F3 completa a la primera con spec de 6 puntos numerados.
- Sonnet omitió 1 de 6 puntos de spec → detectado por checklist grep → corrección acotada lo cerró.
→ El mismo modelo rinde niveles distintos según la calidad del spec y del bucle. Esa es la palanca.

## Arquitectura (5 componentes)

### 1. SPEC-COMPILER — compilar el pedido en one-shot perfecto
> Plantilla operativa: `templates/spec-compilada.md` (llenar + checklist antes de despachar).
Todo despacho pasa por compilación antes de llegar al worker:
- **Contexto mínimo suficiente**: qué existe (funciones/contratos exactos con nombres reales — verificados por grep, jamás supuestos), qué NO tocar.
- **Puntos numerados auditables** (1..N), cada uno con criterio de aceptación observable.
- **Contrato de salida**: archivos exactos, formato, "resumen máx N líneas".
- **Prefijo de ejecución** para modelos que planifican sin ejecutar: "esta tarea se completa ÚNICAMENTE escribiendo código con tus herramientas; no describas planes".
- **Inyección de anti-patrones** del modelo destino (componente 4).
- Presupuesto: tarea para modelo barato ≤ 6 puntos y ≤ 1 archivo grande; si excede → descomponer (componente 3).

### 2. VERIFY-REPAIR — bucle generate→verify→repair
Tras cada entrega, verificadores OBJETIVOS (no opinión):
- `edited`/`Test-Path` de entregables (del .done del runner multi-cli).
- Sintaxis: node --check / linter del lenguaje.
- Checklist grep: un patrón de evidencia por punto numerado.
- Funcional: Playwright/curl/test runner según tipo (tabla de verificación de CLAUDE.md).
Resultado → veredicto: ACEPTADA / REPARAR (one-shot de reparación SOLO con los puntos fallidos + evidencia del fallo) / ESCALAR.
Máx 2 reparaciones por tarea; la reparación es conversación FRESCA (anti contaminación).

**Crítico ≠ generador (MAR, arxiv 2512.20845):** el que diagnostica y repara NO debe ser
el mismo razonamiento que produjo el error — un solo agente reflexionando sobre su propio
fallo lo repite ("cognitive entrenchment"). Reglas:
- El crítico parte del OUTPUT OBJETIVO del verificador (qué check falló, su salida real),
  no del razonamiento previo del generador.
- Si el generador fue un worker (gemma/sonnet/AGY) → la reparación va a conversación fresca,
  idealmente con un modelo distinto o tier superior (router por evidencia).
- Si el generador fue Jarvis mismo → adoptar explícitamente rol de crítico: leer el
  `verdict.json` de [[verify-repair]] y atacar desde otro ángulo, no re-justificar.
- Motor objetivo de este componente: el skill [[verify-repair]] (`verify-gate.ps1`) provee
  el veredicto; agent-uplift provee la política de reparación (cuántos intentos, quién repara).

### 3. DECOMPOSE-ROUTE — descomposición y enrutado por evidencia
- Tarea grande → subtareas del tamaño que el tier barato resuelve bien (datos del benchmark, no intuición).
- Router: tipo de tarea × historial de éxito por modelo (tabla viva en `benchmark/results.md`).
- Integración de piezas: siempre tier alto (Opus/Jarvis) — la integración es donde los baratos fallan.

### 4. ANTI-PATTERN CATALOG — el "entrenamiento" sin tocar pesos
`~/.claude/skills/agent-uplift/antipatterns/<modelo>.md` — cada fallo observado se cataloga:
`[fecha] · síntoma · causa · CONTRAMEDIDA DE PROMPT (texto inyectable)`.
El SPEC-COMPILER inyecta las contramedidas del modelo destino en cada spec. El catálogo solo crece → el mismo modelo mejora con cada tarea sin reentrenar. Iniciales:
- **gemma/OC**: se queda sin sesión en archivos >50KB → contramedida: "no leas archivos completos; usa búsquedas dirigidas" + partir tarea.
- **Sonnet/AGY**: omite puntos de specs largas → contramedida: "antes de terminar, relee los puntos 1..N y verifica cada uno".
- **Sonnet/Opus/AGY**: responde plan sin ejecutar en -p → contramedida: prefijo de ejecución.

### 5. BENCHMARK — medir o no existe mejora
Suite en `<proyecto>/benchmark/`: 10 tareas reproducibles sobre un codebase de prueba (feature acotada, fix con repro, refactor, módulo nuevo, QA, integración, edge cases, docs técnicas, test suite, tarea con trampa anti-instrucciones).
Rúbrica por tarea: % puntos del spec con evidencia + sintaxis + funcional + nº reparaciones usadas. Score 0-100.
Protocolo: medir cada modelo SIN harness (baseline) y CON harness completo. Métrica de éxito del proyecto: **tier gratis con harness ≥ 90% del score de Opus sin harness** en la suite.

## Ciclo de iteración (bucle agéntico permanente)

```
benchmark → peor brecha identificada → mejorar el componente responsable
(spec? verificador? router? anti-patrón nuevo?) → re-benchmark → repetir
```
Cada iteración deja: score nuevo en `benchmark/results.md` + anti-patrones nuevos + cambio concreto en un componente. Nunca dos iteraciones sin medición entre ellas.

## Relación con otras skills
- `multi-cli`: es la capa de EJECUCIÓN (terminales, runners, .done, TTS). agent-uplift es la capa de CALIDAD encima.
- `bucle-agentico`: gobierna las fases del proyecto UPLIFT (BLUEPRINT, just-in-time).
- Límites éticos: esto eleva capacidad de ingeniería de software del agente. Nada de evasión de salvaguardas, ciber-ofensivo ni biología — fuera de alcance por diseño.

## Estado del proyecto
- F0 benchmark: COMPLETO (suite C1-C8; baseline opus46=100, gemma=100 fácil / 78 duro — brecha en C8 inyección).
- F1 verify-repair: COMPLETO y validado. F2 token-router: COMPLETO. F3 scratchpad: COMPLETO. F4 spec-compiler + crítico separado: COMPLETO. F5 integración multi-cli + verificación adaptativa: EN CURSO.
- Nota: el gate "2026-06-22" era el deadline de Fable 5 gratis; Fable se suspendió el 12-jun. Gate vigente: feature larga de zombieswar end-to-end auto-verificada.

## Integración harness (skills hermanas)
- [[verify-repair]] (F1) provee el veredicto objetivo (motor del componente 2 VERIFY-REPAIR).
- [[token-router]] (F2) provee el router por dificultad (motor del componente 3 DECOMPOSE-ROUTE).
- [[scratchpad]] (F3) provee memoria + correction-detection (alimenta el componente 4 ANTI-PATTERN CATALOG).