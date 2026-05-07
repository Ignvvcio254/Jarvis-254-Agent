# SaaS System System

Guía operativa del sistema SaaS System integrado en Jarvis.

## Qué es SaaS System

Framework de ejecución para features complejas con control de contexto, planificación previa y despliegue por fases.

Base conceptual:

- PRP antes de implementar.
- Fases con mapeo just-in-time.
- Registro de decisiones y aprendizaje acumulado.

## Componentes del sistema

### Skills núcleo

- `skills/prp/SKILL.md`
  - función: generar Product Requirements Proposal (PRP) estructurado.
- `skills/bucle-agentico/SKILL.md`
  - función: ejecutar fases secuenciales con subtareas derivadas del estado real.
- `skills/autoresearch/SKILL.md`
  - función: optimizar skills y reducir rework recurrente.

### Artefactos

- `PRPs/prp-base.md`
  - template base para PRPs.
- `cerebro/`
  - memoria de decisiones, outputs y pendientes.

### Comandos de soporte

- `commands/ag-project.md`
  - bootstrap del proyecto con estructura de handoff.
- `commands/memoria.md`
  - ingest/query/lint para continuidad de contexto.
- `commands/consumo.md`
  - control de presión de contexto durante ejecución larga.

## Flujo recomendado end-to-end

1. **Inicio de proyecto**
   - usar `/ag-project` si el proyecto no existe.
2. **Definición de feature**
   - construir PRP con `skills/prp/SKILL.md` usando `PRPs/prp-base.md`.
3. **Aprobación**
   - marcar PRP como aprobado antes de tocar implementación compleja.
4. **Ejecución por fases**
   - ejecutar con `skills/bucle-agentico/SKILL.md`.
5. **Memoria y trazabilidad**
   - registrar con `/memoria ingest` al cerrar hito relevante.
6. **Mejora continua**
   - aplicar `skills/autoresearch/SKILL.md` cuando se detecten gaps.

## Contratos de calidad

- No saltar PRP en tareas multiarchivo/multicapa.
- No generar todas las subtareas al inicio (usar mapeo por fase).
- Documentar decisiones arquitectónicas y pendientes.
- Verificar cada fase antes de pasar a la siguiente.

## Señales para activar SaaS System

Activar cuando la tarea involucra uno o más:

- cambios coordinados en backend + frontend + datos,
- múltiples archivos con dependencias entre sí,
- entregable por fases,
- alto riesgo de rework sin planificación previa.

## Integración con documentación del repo

- comandos: `COMMANDS.md`
- matriz comando-skill: `COMMAND_SKILL_BEHAVIOR.md`
- instalación: `INSTALL.md`
- skills: `SKILLS.md`
- sanitización y seguridad: `SANITIZATION.md`
