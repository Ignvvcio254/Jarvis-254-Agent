---
description: Diagnostica el estado de instalación portable de Jarvis y detecta faltantes críticos.
argument-hint: "[repo-only | full]"
---

# /doctor

Ejecuta una verificación rápida del ecosistema Jarvis para confirmar que un clon del repositorio está operativo.

## Entradas

- `repo-only`: valida solo archivos del repositorio actual.
- `full` o vacío: valida repo + instalación local en `~/.claude`.

## Flujo esperado

1. Determinar modo según `$ARGUMENTS`.
2. Ejecutar:
   - `python jarvis_doctor.py --repo-only` (modo `repo-only`)
   - `python jarvis_doctor.py` (modo `full`)
3. Reportar resultado con resumen claro:
   - checks OK,
   - faltantes,
   - siguiente acción recomendada.

## Output

- Estado de diagnóstico (`All checks passed` o faltantes detectados).
- Lista de paths faltantes cuando aplique.
- Siguiente paso mínimo para recuperación (`INSTALL.md`).

## Seguridad

- No escribe secretos.
- No modifica archivos por defecto.
- Solo lectura de estructura local.
