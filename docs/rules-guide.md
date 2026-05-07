# Rules Index

Mapa rápido de todos los packs de reglas bajo `rules/`.

## Cómo usar este índice

- `rules/common/*` aplica a cualquier stack.
- `rules/<stack>/*` añade especialización por lenguaje/plataforma.
- Orden recomendado de aplicación:
  1. `common`
  2. stack objetivo
  3. dominio específico (web, seguridad, testing, etc.)

## Mapa de categorías

- `coding-style` — formato, naming, legibilidad.
- `patterns` — arquitectura y diseño de implementación.
- `security` — controles y hardening.
- `testing` — cobertura, estrategia y validación.
- `hooks` — automatización de calidad pre/post cambio.

## Criterio de aplicación en tareas reales

- Priorizar siempre seguridad y correctitud sobre velocidad de implementación.
- Si dos reglas parecen conflictivas, usar la más específica del stack objetivo.
- En tareas multi-stack, documentar en PR qué reglas se aplicaron y por qué.

## Matriz rápida de seguridad y aprobación

| Tipo de acción | Riesgo | Aprobación explícita | Control mínimo |
|---|---|---|---|
| Editar documentación/rules/índices | Bajo | No | Mantener portabilidad y sanitización |
| Editar código fuente local | Medio | No | Validación mínima (lint/test según stack) |
| Crear rama/commit local | Medio | No | Mensaje claro + sin secretos |
| Push a remoto (no `main`) | Medio | Sí recomendada | Revisar diff y destino antes de push |
| Push directo a `main` | Alto | Sí obligatoria | Evitar por política; preferir PR |
| Rotar/crear credenciales | Alto | Sí obligatoria | Nunca almacenar en repo |
| Configurar MCP con datos reales | Alto | Sí obligatoria | Usar variables de entorno/local secrets |
| Deploy/acciones en producción | Alto | Sí obligatoria | Checklist pre-deploy + rollback plan |
| Borrado de archivos o datos | Alto | Sí obligatoria | Confirmar alcance y reversibilidad |

## Common

- `rules/common/agents.md`
- `rules/common/code-review.md`
- `rules/common/coding-style.md`
- `rules/common/development-workflow.md`
- `rules/common/git-workflow.md`
- `rules/common/hooks.md`
- `rules/common/patterns.md`
- `rules/common/performance.md`
- `rules/common/security.md`
- `rules/common/testing.md`

## Web

- `rules/web/coding-style.md`
- `rules/web/design-quality.md`
- `rules/web/hooks.md`
- `rules/web/patterns.md`
- `rules/web/performance.md`
- `rules/web/security.md`
- `rules/web/testing.md`

## TypeScript

- `rules/typescript/coding-style.md`
- `rules/typescript/hooks.md`
- `rules/typescript/patterns.md`
- `rules/typescript/security.md`
- `rules/typescript/testing.md`

## Python

- `rules/python/coding-style.md`
- `rules/python/hooks.md`
- `rules/python/patterns.md`
- `rules/python/security.md`
- `rules/python/testing.md`

## Rust

- `rules/rust/coding-style.md`
- `rules/rust/hooks.md`
- `rules/rust/patterns.md`
- `rules/rust/security.md`
- `rules/rust/testing.md`

## Go

- `rules/golang/coding-style.md`
- `rules/golang/hooks.md`
- `rules/golang/patterns.md`
- `rules/golang/security.md`
- `rules/golang/testing.md`

## Java

- `rules/java/coding-style.md`
- `rules/java/hooks.md`
- `rules/java/patterns.md`
- `rules/java/security.md`
- `rules/java/testing.md`

## Kotlin

- `rules/kotlin/coding-style.md`
- `rules/kotlin/hooks.md`
- `rules/kotlin/patterns.md`
- `rules/kotlin/security.md`
- `rules/kotlin/testing.md`

## CSharp

- `rules/csharp/coding-style.md`
- `rules/csharp/hooks.md`
- `rules/csharp/patterns.md`
- `rules/csharp/security.md`
- `rules/csharp/testing.md`

## Swift

- `rules/swift/coding-style.md`
- `rules/swift/hooks.md`
- `rules/swift/patterns.md`
- `rules/swift/security.md`
- `rules/swift/testing.md`
