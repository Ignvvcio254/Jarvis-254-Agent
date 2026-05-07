# Command Skill Behavior Matrix

Matriz de comportamiento entre comandos slash (`commands/`) y skills (`skills/`).

## Modelo de ejecución

Hay dos capas complementarias:

- **Comandos slash**: interfaz de usuario para iniciar operaciones concretas.
- **Skills**: capacidad especializada que se activa por contexto, workflow o decisión del agente.

## Matriz comando → skill/workflow

| Comando | Rol principal | Skills relacionadas | Tipo de activación |
|---|---|---|---|
| `/memoria` | Operar wiki global (ingest/query/lint) | `prp`, `bucle-agentico` (indirecto), `claude-engineer` | Directa por slash command |
| `/consumo` | Monitorear presión de contexto y modos Caveman | `claude-engineer` | Directa por slash command |
| `/ag-project` | Bootstrap de proyecto y handoff | `claude-engineer`, `prp` (flujo posterior) | Directa por slash command |
| `/marketing-swarm` | Orquestación marketing paralela | skills de marketing por dominio | Directa por slash command + activación contextual |
| `/connect-apps-setup` | Configuración de conectores externos | skills de automatización/integración (según uso) | Directa por slash command |
| `/doctor` | Diagnóstico rápido de instalación y operación | `claude-engineer` + reglas de seguridad operativa | Directa por slash command |

## Matriz skill SaaS Factory → comando de soporte

| Skill | Función | Comando de soporte recomendado |
|---|---|---|
| `skills/prp/SKILL.md` | Definir PRP para feature compleja | `/memoria` para registrar decisiones |
| `skills/bucle-agentico/SKILL.md` | Ejecutar implementación por fases | `/consumo` para sesiones largas |
| `skills/autoresearch/SKILL.md` | Mejorar skills y reducir rework | `/memoria` para trazabilidad de mejoras |

## Regla operativa

No todo skill necesita comando dedicado. En Jarvis:

- si la operación es recurrente y orientada a usuario, se expone como slash command;
- si la operación es una capacidad interna especializada, se mantiene como skill de activación contextual.

## Referencias

- `COMMANDS.md`
- `SAAS_FACTORY.md`
- `SKILLS.md`
- `RUNTIME_LITE.md`
