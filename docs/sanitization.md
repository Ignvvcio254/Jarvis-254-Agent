# Sanitization Report

## Propósito

Este documento deja trazabilidad de qué se importó, qué se excluyó y por qué, para mantener el repositorio seguro, portable y publicable.

## Alcance revisado

Fuentes evaluadas desde `C:\Users\w10\.claude`:

- `commands/`
- `skills/`
- `rules/`
- `design-systems/`
- archivos de configuración (`.claude.json`, `settings.json`)
- memorias locales de proyecto (`projects/*/memory`)

## Incluido (seguro)

- `rules/` (packs de reglas por stack)
- `design-systems/` (documentación visual y assets)
- `commands/` (comandos slash documentados)
- `skills/` (pack completo, solo `SKILL.md` por skill)
- `PRPs/prp-base.md` (template base SaaS System)
- plantillas sanitizadas en `config/` y `mcp/`

## Excluido (cuarentena)

Ubicación: `quarantine/private-excluded/` (ignorado por `.gitignore`)

- `.claude.json` real
- `settings.json` real
- memorias privadas (`memory/`)

## Criterios de exclusión

Un archivo se excluye si contiene al menos uno de estos riesgos:

- credenciales o tokens,
- rutas absolutas de usuario/sistema,
- telemetría o estado de sesión no portable,
- datos personales o contexto privado de trabajo.

## Regla operativa

Si un artefacto debe publicarse y hoy está en cuarentena:

1. crear versión template en `config/` o `mcp/`,
2. reemplazar valores sensibles por placeholders,
3. documentar el cambio en este archivo.

## Estado actual

- Sanitización: completa para distribución pública.
- Riesgo residual conocido: bajo (sujeto a revisiones futuras de contenido nuevo).
