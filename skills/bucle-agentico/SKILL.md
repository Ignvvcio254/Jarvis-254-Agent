---
name: bucle-agentico
description: "Ejecutar features complejas por fases con mapeo de contexto real ANTES de cada fase. La innovacion clave: NO generar todas las subtareas al inicio — mapear contexto just-in-time y generar subtareas basadas en la realidad actual del sistema. Activar cuando la tarea toca multiples archivos coordinados, requiere cambios en DB + codigo + UI, tiene fases que dependen una de otra, o cuando un PRP fue aprobado y hay que implementarlo."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Modo BLUEPRINT del Bucle Agentico

> "No planifiques lo que no entiendes. Mapea contexto, luego planifica."

El modo BLUEPRINT es para sistemas complejos que requieren construccion por fases con mapeo de contexto just-in-time.

---

## Cuando Usar

- La tarea requiere multiples componentes coordinados
- Involucra cambios en DB + codigo + UI
- Tiene fases que dependen una de otra
- Requiere entender contexto antes de implementar
- Un PRP fue aprobado y hay que ejecutarlo

---

## La Innovacion: Mapeo de Contexto Just-In-Time

### Enfoque Tradicional (MALO)

Recibir problema → Generar TODAS las tareas y subtareas → Ejecutar linealmente.
Problema: Las subtareas se generan basandose en SUPOSICIONES, no en contexto real.

### Enfoque BLUEPRINT (CORRECTO)

```
Recibir problema → Generar solo FASES (sin subtareas)
    |
ENTRAR en Fase 1 → MAPEAR contexto real
    |
GENERAR subtareas basadas en contexto REAL → Ejecutar Fase 1
    |
ENTRAR en Fase 2 → MAPEAR contexto (incluyendo lo construido en Fase 1)
    |
GENERAR subtareas de Fase 2 → Ejecutar → ... repetir ...
```

Ventaja: Cada fase se planifica con informacion REAL del estado actual del sistema.

---

## El Flujo BLUEPRINT: 5 Pasos

### PASO 1: DELIMITAR EN FASES

- Entender el problema FINAL completo
- Romper en FASES ordenadas cronologicamente
- Identificar dependencias entre fases
- NO generar subtareas todavia
- Usar TodoWrite para registrar las fases

### PASO 2: ENTRAR EN FASE N — MAPEAR CONTEXTO

ANTES de generar subtareas, explorar:

**Codebase:**
- Que archivos/componentes existen relacionados?
- Que patrones usa el proyecto actualmente?
- Hay codigo que se puede reutilizar?

**Estado actual del sistema:**
- Que construi en fases anteriores?
- Que puedo asumir que ya existe?
- Que restricciones tengo?

DESPUES de mapear, generar subtareas especificas y actualizar TodoWrite.

### PASO 3: EJECUTAR SUBTAREAS DE LA FASE

```
WHILE subtareas pendientes en fase actual:
  1. Marcar subtarea como in_progress en TodoWrite
  2. Ejecutar la subtarea
  3. Usar herramientas segun el juicio (playwright, build, grep, etc.)
  4. Validar resultado
     - Si hay error → AUTO-BLINDAJE (paso 3.5)
     - Si esta bien → Marcar completed
  5. Siguiente subtarea
Fase completada cuando todas las subtareas done.
```

### PASO 3.5: AUTO-BLINDAJE (cuando hay errores)

Cuando algo falla:
1. ARREGLA el codigo
2. TESTEA que funcione
3. DOCUMENTA el aprendizaje:

```markdown
### [YYYY-MM-DD]: [Titulo corto]
- **Error**: [Que fallo exactamente]
- **Fix**: [Como se arreglo]
- **Aplicar en**: [Donde mas aplica este conocimiento]
```

| Tipo de Error | Donde Documentar |
|---------------|-----------------|
| Especifico de esta feature | PRP actual (seccion Aprendizajes) |
| Aplica a multiples features | Skill relevante en ~/.claude/skills/ |
| Aplica a TODO el proyecto | CLAUDE.md del proyecto |

El conocimiento persiste. El mismo error NUNCA ocurre dos veces.

### PASO 4: TRANSICIONAR A SIGUIENTE FASE

- Confirmar que la fase actual esta REALMENTE completa
- NO asumir que todo salio como se planeo
- Volver a PASO 2 con la siguiente fase
- El contexto ahora INCLUYE lo construido

### PASO 5: VALIDACION FINAL

- Testing end-to-end del sistema completo
- Validacion visual si aplica (playwright)
- Confirmar que el problema ORIGINAL esta resuelto
- Reportar al senor Ignacio que se construyo

---

## Errores Comunes

**Error 1: Generar todas las subtareas al inicio**
```
MAL:  Fase 1: DB Schema → 10 subtareas detalladas
      Fase 2: APIs → 8 subtareas (basadas en SUPOSICIONES)

BIEN: Fase 1: DB Schema (sin subtareas)
      Fase 2: APIs (sin subtareas)
      → Entrar en Fase 1 → MAPEAR contexto → GENERAR subtareas → Ejecutar
      → Entrar en Fase 2 → MAPEAR contexto real → GENERAR subtareas
```

**Error 2: No re-mapear contexto entre fases**
```
MAL:  Fase 1 completada → Pasar directo a ejecutar Fase 2
BIEN: Fase 1 completada → MAPEAR contexto de Fase 2 → Generar subtareas → Ejecutar
```

---

## Checklist por Fase

Antes de marcar una fase como completada:
- [ ] Todas las subtareas estan realmente terminadas?
- [ ] La funcionalidad hace lo que se esperaba?
- [ ] Hay errores documentados en auto-blindaje?

Antes de transicionar a siguiente fase:
- [ ] Mapee el contexto actualizado?
- [ ] Las subtareas de la nueva fase consideran lo que YA existe?

---

## Principios BLUEPRINT

1. Fases primero, subtareas despues — Solo generar subtareas cuando entras a la fase
2. Mapeo obligatorio — Siempre mapear contexto real antes de generar subtareas
3. TodoWrite activo — Mantener actualizado el progreso para visibilidad
4. Validacion por fase — Confirmar que cada fase esta completa antes de avanzar
5. Contexto acumulativo — Cada fase hereda el contexto de las anteriores
6. Auto-blindaje — Cada error se documenta para no repetirse

---

*"La precision viene de mapear la realidad, no de imaginar el futuro."*
*"El sistema que se blinda solo es invencible."*