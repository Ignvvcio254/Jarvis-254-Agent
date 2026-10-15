---
name: verify-repair
description: Gate de veredicto OBJETIVO antes de reportar cualquier entrega. Una tarea no está hecha porque el modelo lo diga, sino porque una señal ejecutable lo confirma (exit code, test, lint, grep, screenshot). Incluye bucle repair con crítico separado del generador. Activar al cerrar cualquier tarea de código, fix, build, o entregable verificable.
---

# verify-repair — El veredicto no es un claim del modelo

> Núcleo del harness Jarvis-UPLIFT (F1). Porta el patrón anti-gaming de evolve-loop
> (`commit-gate`) + el orden de verificación de prax-agent.
> Doctrina: *"The verdict is not a model claim — it's an exit code. The model writes
> prose but cannot game the predicate suite."*

## El principio (no negociable)

Una tarea **NO está completa porque Jarvis lo diga**. Está completa cuando una **señal
objetiva** lo confirma. El modelo puede escribir prosa; no puede gamear el predicado.

Causa raíz que esto elimina: reportar éxito sin verificar (ej. caso `dayPhase` —
se reportó "está hecho", Playwright mostró que no existía).

## Cuándo se activa (obligatorio)

Antes de reportar como completa CUALQUIER tarea de:
- código nuevo o editado
- fix de bug
- build / config / infra
- entregable de worker (AGY / OpenCode)
- refactor / delete

No aplica a: respuestas conversacionales, investigación pura, decisiones de diseño.

## Gates equivalentes + sello (evita falsos positivos del verdict_guard)

`verify-gate.ps1` escribe `.verify/verdict.json`. Pero otros gates son igual o MÁS
fuertes y el `verdict_guard` ahora los reconoce:
- **Auto-reconocidos por el guard** (no requieren nada): `.js/.mjs/.cjs` → `node --check`;
  `.py` → `py_compile`. El guard los verifica solo y no avisa si pasan.
- **Caros (TS/build/deploy)**: si verificaste con `tsc --noEmit` exit 0, `npm run build`,
  o un deploy de Vercel READY, **séllalo** para que el guard no dé falso positivo:
  `python ~/.claude/scripts/verdict_stamp.py <gate>` (ej. `tsc`, `vercel-build`).
  El sello SOLO se pone tras una verificación REAL que pasó; no es para saltarse el gate.

## El orden de verificación (de prax-agent, adaptado)

Correr **solo los checks que el proyecto soporta**, en este orden. Saltar los no
aplicables explicando por qué (nunca en silencio):

```
1. build / parse   → ¿compila / parsea sin error?
2. typecheck       → tsc, pyright, mypy (si hay tipos)
3. lint            → eslint, ruff, etc. (si hay config)
4. test            → la suite del proyecto, o el verificador del caso
5. behavior        → grep del patrón esperado / playwright screenshot del resultado
```

Regla: **usar el entrypoint existente del proyecto** (`npm test`, `pytest`, etc.).
No inventar comandos. Reportar SOLO resultados reales de ejecución.

## El motor: verify-gate.ps1

`verify-gate.ps1` automatiza el veredicto objetivo:
- Auto-detecta tipo de proyecto (node / python / web-estático / genérico)
- Corre los checks disponibles
- Escribe `.verify/verdict.json` con: resultado por check + `stateHash` (sha256 del
  estado del árbol) + veredicto final
- **Exit 0 solo si todo lo aplicable pasa.** Exit 1 si algo falla.

El `stateHash` liga el veredicto al estado exacto del código (patrón evolve-loop):
si el código cambia después, el veredicto anterior ya no vale → imposible de gamear.

```powershell
# Uso básico (auto-detecta y verifica el proyecto actual):
pwsh ~/.claude/skills/verify-repair/verify-gate.ps1 -Path .

# Con verificador específico de caso (benchmark / tarea con verify.js):
pwsh ~/.claude/skills/verify-repair/verify-gate.ps1 -Path . -Verifier "node verify.js"

# Con check de comportamiento (grep de patrón que DEBE existir):
pwsh ~/.claude/skills/verify-repair/verify-gate.ps1 -Path . -MustContain "dayPhase" -File "game.html"
```

## El bucle repair (crítico ≠ generador)

Si `verify-gate.ps1` sale con exit 1:

```
1. LEER el verdict.json → identificar QUÉ check falló y su output real
2. El CRÍTICO (rol distinto del que generó) diagnostica la causa raíz
   · NO el mismo razonamiento que produjo el error (MAR: single-agent se estanca)
   · si fue un worker, re-derivar en conversación FRESCA (doctrina one-shot)
3. APLICAR la corrección dirigida al check que falló
4. RE-CORRER verify-gate.ps1
5. Repetir hasta exit 0 o hasta MAX_REPAIR (default 3)
6. Si tras MAX_REPAIR sigue fallando → DETENER y reportar al usuario:
   qué falla, qué se intentó, output objetivo. Nunca reportar éxito falso.
```

Por qué crítico separado: la investigación (MAR, arxiv 2512.20845) muestra que un
solo agente reflexionando sobre su propio error **repite el error**. El crítico debe
atacar desde otro ángulo: leer el output objetivo del check, no el razonamiento previo.

## Anti-gaming (de evolve-loop)

- El veredicto vive en `verdict.json`, ligado a `stateHash`.
- Si alguien (modelo incluido) edita el código sin re-verificar, el hash no coincide
  → el veredicto se considera inválido.
- El modelo no puede escribir `verdict.json` a mano: lo escribe el script tras correr
  los checks reales.

## Delegación a workers

Al despachar a AGY/OpenCode vía `multi-cli`, incluir en la spec:
> "Tu entrega no se acepta hasta que `verify-gate.ps1` salga con exit 0.
>  Corre la verificación tú mismo antes de marcar `.done`."

El runner de `multi-cli` corre `verify-gate.ps1` sobre el output del worker antes de
aceptar la entrega. `edited=True` (cambió tamaño) + `verdict=pass` = entrega válida.

## Verificación de este skill (meta)

Probar sobre zombieswar: `verify-gate.ps1 -Path . -MustContain "dayPhase" -File "zombieswar.html"`
debe salir exit 1 (porque `dayPhase` no existe) — demostrando que el gate detecta lo
que el reporte humano pasó por alto.

## Relación

Parte del harness con [[token-router]] (qué modelo), spec-compiler de `agent-uplift`
(qué instrucción), y `multi-cli` (cómo delegar). Veredicto objetivo es prerequisito
del router: sin él, no se puede confiar en modelos baratos.