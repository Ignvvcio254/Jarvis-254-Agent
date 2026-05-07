# Config Templates

Esta carpeta contiene templates de configuración sanitizados. Estos archivos son seguros para compartir.

## Uso

1. Copiar el template al destino de configuración local.
2. Completar placeholders solo en su máquina local.
3. Validar sintaxis JSON antes de ejecutar Claude Code.
4. Nunca commitear credenciales reales.

## Archivos

- `settings.template.json` — baseline seguro de settings.
- `claude.template.json` — ejemplo de configuración global sin secretos.

## Notas de seguridad

- No mover archivos reales de `~/.claude*` al repo.
- Si una config local contiene secretos, crear una versión template nueva y documentarla aquí.
