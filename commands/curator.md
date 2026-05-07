# /curator — Skill Lifecycle Curation

Gestiona el ciclo de vida de los skills en `skills/`. Marca skills obsoletos como `stale` y archiva los que llevan demasiado tiempo sin modificación.

## Implementación

`jarvis_core/skill_curator.py` — clase `SkillCurator`.
Runtime: `python jarvis_runtime.py curator [opciones]`

## Estados de skill

| Estado | Significado |
|---|---|
| `active` | Skill vigente y usable |
| `stale` | Sin modificaciones en > 60 días |
| `archived` | Movido a `skills/_archived/` — siempre recuperable |

## Invariantes de seguridad (patrón Hermes curator.py)

- Skills con `pinned: true` en frontmatter nunca son tocados.
- Skills en `_ALWAYS_PINNED` (primer, prp, bucle-agentico, autoresearch, antigravity-bridge) están protegidos por código.
- Archiva en lugar de borrar — siempre recuperable desde `skills/_archived/`.
- No usa frecuencia de acceso como criterio (evita sesgos de popularidad).

## Uso

```bash
# Ver estado actual de todos los skills
python jarvis_runtime.py curator --status

# Preview de cambios (dry-run, default seguro)
python jarvis_runtime.py curator --verbose

# Aplicar cambios reales
python jarvis_runtime.py curator --execute --verbose

# Ajustar umbrales
python jarvis_runtime.py curator --stale-days 90 --archive-days 180 --verbose
```

## Opciones

| Opción | Default | Descripción |
|---|---|---|
| `--status` | — | Muestra breakdown de estados sin ejecutar |
| `--dry-run` | true | Preview sin escribir nada |
| `--execute` | — | Aplica los cambios (opuesto a --dry-run) |
| `--stale-days` | 60 | Días sin modificación para marcar stale |
| `--archive-days` | 120 | Días en stale antes de archivar |
| `--verbose` | — | Muestra todas las acciones no-keep |

## Proteger un skill manualmente

Agregar al frontmatter del `SKILL.md`:

```yaml
---
name: mi-skill
description: ...
pinned: true
---
```
