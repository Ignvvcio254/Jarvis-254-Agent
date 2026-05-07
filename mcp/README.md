# MCP Templates

Esta carpeta contiene templates MCP provider-agnostic y notas de setup.

## Reglas

- Nunca commitear tokens o credenciales reales.
- Usar variables de entorno o placeholders.
- Mantener rutas portables (evitar paths absolutos de usuario).

## Archivos

- `mcp.template.json` — base MCP server configuration template
- `env.example` — environment variables for MCP servers

## Uso

1. Copiar `mcp.template.json` a su `~/.claude.json` local.
2. Copiar `env.example` a `.env` (solo local) y completar valores.
3. Iniciar servidores MCP con su workflow preferido.

## Política recomendada

- Mantener la configuración MCP declarativa y mínima.
- Preferir variables de entorno sobre secretos inline.
- Si un MCP es opcional/no confiable, documentar fallback en docs de comandos.

## Checklist de validación

- Sintaxis JSON válida.
- Sin tokens hardcodeados.
- Sin rutas absolutas de usuario cuando sea evitable.
- Comandos de servidor resolubles en entorno local.
