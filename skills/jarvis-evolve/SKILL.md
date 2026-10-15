---
name: jarvis-evolve
description: Bucle de automejora permanente de Jarvis — audita señales (bitácoras, anti-patrones, memoria, fallos de sesión, skills locales), diagnostica brechas, propone mejoras al aplica las aprobadas y mide. Incluye la doctrina "razonamiento nivel Mythos por contexto" para elevar a cualquier modelo Claude. Invocar al cerrar sesiones significativas, cuando se repita un error, o con /jarvis-evolve.
---

# JARVIS-EVOLVE — el agente que se automejora

## Doctrina: razonamiento nivel Mythos por contexto

Un modelo no se mejora tocando pesos — se eleva **destilando conocimiento en documentos inyectables**. El razonamiento de clase Mythos/Fable de una sesión buena no muere con la sesión: se captura como contexto reutilizable, y cualquier modelo Claude (Haiku, Sonnet, Opus) que arranque con ese contexto razona desde ese nivel en ese dominio.

Las cuatro destilerías (dónde se captura cada tipo de conocimiento):

| Tipo de conocimiento | Destino | Quién lo consume |
|---|---|---|
| Cómo operar (protocolos verificados) | Skills del núcleo (`multi-cli`, `agent-uplift`, esta) | Jarvis en cualquier sesión/modelo |
| Qué falla y su contramedida | `agent-uplift/antipatterns/<modelo>.md` | SPEC-COMPILER → workers |
| Decisiones y estado de proyectos | Memoria persistente + `cerebro/` + `workspace/APRENDIZAJES.md` | Jarvis al retomar |
| Reglas de identidad y arbitraje | `CLAUDE.md` (compacto — es costo fijo por sesión) | Toda sesión |

Regla de oro: **conocimiento que solo vive en la conversación es conocimiento muerto.** Si costó descubrirlo, se destila antes de cerrar.

## El bucle (6 pasos)

1. **SENSE — recolectar señales.** Fuentes: `workspace/APRENDIZAJES.md` de proyectos activos (sección Auto-blindaje), `antipatterns/`, memoria del proyecto, fallos repetidos de la sesión actual, métricas del benchmark UPLIFT si existe, fricción observada (¿qué tarea costó más de lo que debía?).
2. **DIAGNOSE — clasificar brechas por impacto.** ¿Es falta de skill? ¿skill desactualizada vs realidad verificada? ¿regla de CLAUDE.md obsoleta o ausente? ¿anti-patrón sin contramedida? ¿conocimiento no destilado? Priorizar por frecuencia × costo del fallo.
3. **PROPOSE — mesa del usuario.** Tabla compacta: brecha · mejora propuesta · archivo afectado · riesgo. Él aprueba o declina (principio: proponer, no ejecutar — salvo autorización explícita de automejora en curso).
4. **APPLY — aplicar lo aprobado.** Ediciones quirúrgicas: skills del núcleo, CLAUDE.md (siempre COMPACTO: cada línea de CLAUDE.md se paga en cada sesión — preferir mover detalle a skills y dejar punteros), plantillas, anti-patrones.
5. **MEASURE — verificar que la mejora mejora.** La siguiente tarea del mismo tipo debe mostrar el efecto (menos reintentos, revisión más limpia, benchmark arriba). Mejora sin efecto medible en 2 usos → revertir o reformular.
6. **RECORD — destilar.** Memoria persistente + sync a `jarvis-brain-repo` (CLAUDE.md/cerebro/memoria, protocolo de CLAUDE.md). Versionar: bump de versión en CLAUDE.md por cambio de reglas.

## Curaduría de las ~1400 skills locales

- Descubrimiento por keyword ANTES de codear (ya en CLAUDE.md Tier 3) — evolve añade el cierre del ciclo:
- **Fallo repetido sin skill que lo cubra** → brecha de catálogo → buscar en comunidad o crear skill propia (PROPOSE).
- **Skill consultada que contradice la realidad verificada** → marcarla en memoria como no confiable para ese caso; la verdad verificada va al núcleo.
- **Nunca borrar** skills de terceros: ignorarlas cuesta cero; borrarlas destruye opcionalidad (patrón SkillCurator: archivar, no eliminar).
- Las skills del NÚCLEO (multi-cli, agent-uplift, bucle-agentico, prp, autoresearch, jarvis-evolve) tienen mantenimiento activo: cada sesión que las use y encuentre fricción debe dejar al menos un candidato de mejora.

## Disparadores del bucle

- Cierre de sesión significativa (junto a `/memoria ingest`).
- Mismo error 2 veces en cualquier contexto (auto-blindaje escala a evolve).
- El usuario pide elevar capacidad ("hazlo mejor", "automejora").
- Benchmark UPLIFT muestra regresión.

## Invariantes (no se automejoran fuera)

Trato "usuario" · seguridad > accesibilidad > correctitud > estética > performance · confirmación antes de acciones destructivas · proponer-antes-de-ejecutar para cambios de identidad/reglas · límites éticos del agent-uplift.