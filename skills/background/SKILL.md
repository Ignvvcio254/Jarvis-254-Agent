---
name: background
description: "Ejecuta prompts en segundo plano mientras la conversación continúa sin interrupciones. Activar con: /background <prompt>, /bg <prompt>, /btw <prompt> — o cuando el señor Ignacio diga 'ejecuta esto en paralelo', 'hazlo en background', 'no me bloquees'. NO USAR para tareas que requieran confirmación del usuario antes de continuar."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# Background — Tareas Asíncronas No Bloqueantes

> Inspirado en el sistema `/background` de Hermes Agent (NousResearch).
> El agente lanza subtareas mientras la conversación principal continúa sin interrupciones.

---

## ¿Cuándo usar?

| Situación | Usar background |
|-----------|----------------|
| Build largo (> 30 segundos) | ✅ |
| Crawl web / fetch múltiples URLs | ✅ |
| Generación de reportes pesados | ✅ |
| Indexación / búsqueda en codebase grande | ✅ |
| Tarea simple < 5 segundos | ❌ — ejecutar directamente |
| Tarea que requiere confirmación del usuario | ❌ — ejecutar interactivamente |

---

## Protocolo de Ejecución

### Activación

Trigger phrases:
- `/background <prompt>` — lanza inmediatamente
- `/bg <prompt>` — alias corto
- `/btw <prompt>` — "by the way, hazlo mientras"
- "hazlo en background", "ejecuta esto en paralelo", "no me bloquees con esto"

### Paso 1 — Acuse de recibo inmediato

Antes de lanzar la tarea, responder en Discord:
```
⚡ Lanzando en background: [descripción corta]
Continúa la conversación — te notifico cuando termine.
```

### Paso 2 — Lanzar subtarea

Usar `Agent` tool con `run_in_background: true`:

```
Agent({
  description: "Background: [descripción]",
  prompt: "[prompt completo con todo el contexto necesario — el worker inicia frío]",
  run_in_background: true
})
```

**Regla crítica:** El worker no tiene contexto de la conversación. El prompt debe ser completamente autocontenido:
- Incluir rutas de archivos absolutas
- Incluir el objetivo final esperado
- Incluir restricciones relevantes (no borrar, no push, etc.)

### Paso 3 — Continuar la conversación principal

Después de lanzar, Jarvis continúa respondiendo al señor Ignacio normalmente. No bloquear esperando resultados.

### Paso 4 — Notificación al completar

Cuando el Agent en background completa, Jarvis recibe la notificación automáticamente. Entonces:
- Si el señor Ignacio está en Discord → `reply("✅ Background completó: [descripción]\n\n[resumen]")`
- Si el resultado es largo → adjuntar como archivo `.md`

---

## /queue — Cola de prompts

`/queue <prompt>` o `/q <prompt>`: Encola un prompt para ejecutar en el **próximo turno**, sin interrumpir el turno actual.

**Uso:** Cuando el señor Ignacio quiere agregar una tarea que se ejecute después de la actual.

**Implementación:** Guardar el prompt en una nota al final de la respuesta actual:
```
[QUEUE: {prompt}]
Al iniciar el siguiente turno, ejecutar este prompt antes de responder al nuevo mensaje.
```

---

## /steer — Inyección mid-conversación

`/steer <mensaje>`: Ajusta el rumbo del agente después del siguiente tool call, sin interrumpir el flujo.

**Uso:** Cuando el señor Ignacio quiere corregir dirección sin detener la ejecución en curso.

**Implementación:** Después de completar el tool call en progreso, insertar el mensaje de steer como contexto adicional antes de generar la siguiente respuesta.

---

## Límites de seguridad

- **Nunca** lanzar en background tareas destructivas (delete, force-push, drop table)
- **Siempre** incluir contexto completo en el prompt del worker — inicia frío
- **Máximo 3 tasks en background simultáneamente**
- Si el worker falla → notificar con el error, nunca silenciar
- Registrar en `cerebro/log.md`: `[fecha] background: [descripción] — [OK/FAIL]`
