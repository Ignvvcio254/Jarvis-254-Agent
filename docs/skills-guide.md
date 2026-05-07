# Skills Index

Este repositorio incluye el pack completo de skills top-level espejado desde `~/.claude/skills`.

## Resumen

- Total skills imported: 1414
- Source parity: 1:1 with top-level `~/.claude/skills/*/SKILL.md`
- Repository format: `skills/<skill-name>/SKILL.md`

## Navegación rápida

- Explorar todas las skills bajo `skills/`
- Usar búsqueda CLI por dominio (ej. `prisma`, `kubernetes`, `seo`, `security`)
- Para ubicar skills por tecnología, priorizar búsqueda por keyword del stack (ej. `fastapi`, `react`, `stripe`)
- Skills núcleo del workflow Jarvis:
  - `skills/claude-engineer/SKILL.md`
  - `skills/prp/SKILL.md`
  - `skills/bucle-agentico/SKILL.md`
  - `skills/autoresearch/SKILL.md`

## Skills y ejecución por comandos

No todas las skills se invocan con slash command directo. En este repo existen dos vías:

- **Comando slash en `commands/`**: interfaz explícita para tareas operativas (ej. `/memoria`).
- **Activación por workflow/trigger**: la skill se invoca por contexto, no por slash command textual.

Para el sistema SaaS Factory:

- Preparación estructural: `commands/ag-project.md`
- Planificación: `skills/prp/SKILL.md`
- Ejecución por fases: `skills/bucle-agentico/SKILL.md`
- Optimización de skills: `skills/autoresearch/SKILL.md`

Ver también `COMMANDS.md` y `SAAS_FACTORY.md`.

## Convenciones

- Una skill por directorio.
- Archivo requerido: `SKILL.md`.
- Mantener docs provider-agnostic y libres de secretos.
- No editar `skills/*/SKILL.md` salvo tarea explícita de evolución de skills.
