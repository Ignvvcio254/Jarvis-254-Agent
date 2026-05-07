---
description: Configura connect-apps (Composio MCP) para integrar apps externas.
argument-hint: "[api-key-opcional]"
---

# /connect-apps-setup

Configura `connect-apps` (Composio) para que el agente pueda ejecutar acciones reales en apps externas (Gmail, Slack, GitHub, etc.).

## Entradas

- Argumento opcional: API key (`[api-key-opcional]`).
- Si no se recibe por argumento, solicitarla al usuario una única vez.

## Flujo de ejecución

### Paso 1 — Obtener API key

- Si no hay key en `$ARGUMENTS`, solicitarla.
- Si el usuario no tiene key, indicar:
  - `https://dashboard.composio.dev`
  - ruta: `Settings -> API Keys`

### Paso 2 — Escribir configuración MCP

Guardar/mergear en `~/.mcp.json` la entrada `connect-apps`:

```json
{
  "connect-apps": {
    "type": "http",
    "url": "https://connect.composio.dev/mcp",
    "headers": {
      "x-consumer-api-key": "THE_API_KEY"
    }
  }
}
```

Si `~/.mcp.json` ya existe con más servidores, conservarlos y agregar/actualizar solo `connect-apps`.

### Paso 3 — Confirmación al usuario

Mensaje final sugerido:

```text
Setup complete!
To activate: exit and run `claude` again
Then try: "Send me a test email at your@email.com"
```

## Reglas de seguridad

- No persistir la API key en archivos versionados del repositorio.
- No modificar `settings.local.json` para este caso.
- No hacer más de una pregunta si falta la key.
- Mantener el cambio local al entorno de ejecución del usuario.
