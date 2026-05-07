# AGENTS.md

## Scope

Este repositorio empaqueta una capa cognitiva portable para Claude Code (Jarvis): instrucciones base, memoria wiki, comandos slash, SaaS System y pack de skills.

## Objetivo operativo

- Mantener el repo listo para distribución pública.
- Documentar comportamiento de comandos y workflows.
- Evitar filtración de datos privados o configuraciones no portables.

## Non-negotiables

- Nunca agregar tokens, secretos o logs de sesión privados.
- Mantener configs MCP como templates (sin credenciales reales).
- Preservar placeholders (`{{YOUR_NAME}}`, etc.).
- No crear/modificar archivos user-specific automáticamente.
- No editar `skills/*/SKILL.md` salvo tarea explícita de evolución de skills.

## Safe defaults

- Preferir documentación clara cuando haya ambigüedad.
- Aplicar cambios mínimos y reversibles.
- Usar rutas relativas y portables en ejemplos.
- Si un artefacto es sensible/dudoso: mover a `quarantine/` y documentar.

## Structure rules

- `CLAUDE.md` es la fuente de verdad del comportamiento del agente.
- `cerebro/` debe permanecer sanitizado.
- `commands/` define interfaces slash y comportamiento ejecutable.
- `PRPs/` y `SAAS_FACTORY.md` gobiernan features complejas.
- `skills/` conserva estructura `skills/<name>/SKILL.md`.

## Documentation quality bar

- Explicar para cada comando: propósito, entradas, flujo, output y seguridad.
- Mantener mapas cruzados comando↔skill↔workflow.
- Actualizar índices (`COMMANDS.md`, `SKILLS.md`, `RULES.md`, `DESIGN_SYSTEMS.md`) cuando cambie el contenido.
