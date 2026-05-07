# Hermes Adoption Playbook

Objetivo: capturar lo mejor de `NousResearch/hermes-agent` para mejorar Jarvis-254-Agent sin romper portabilidad ni sanitización.

## Estado actual

- Upstream clonado en: `upstream/hermes-agent/`
- Licencia verificada: MIT (reutilización permitida con atribución).
- Script de actualización upstream: `sync_hermes_upstream.ps1`
- `upstream/` es opcional y no se versiona (ignorado por git).

## Qué adoptamos ya

1. **Referencia upstream local**
   - Se mantiene un clon de Hermes dentro del repo para análisis técnico directo.

2. **Operación tipo doctor**
   - Nuevo script: `jarvis_doctor.py`
   - Nuevo comando documentado: `commands/doctor.md`
   - Beneficio: diagnóstico instantáneo para nuevos cloners.

3. **Madurez documental operativa**
   - Matriz de capacidades y entrypoints en `README.md`.
   - Matriz de aprobaciones en `RULES.md`.
   - Plantilla de releases en `RELEASE_TEMPLATE.md`.

4. **Runtime-lite inicial**
   - Nuevo ejecutable: `jarvis_runtime.py`
   - Módulos base: `jarvis_core/providers.py`, `jarvis_core/sessions.py`, `jarvis_core/policy.py`, `jarvis_core/telemetry.py`
   - Guía de uso: `RUNTIME_LITE.md`

## Qué extraer de Hermes (prioridad alta)

### A. Runtime mínimo productivo (MVP)

- Crear `jarvis_core/` con:
  - interfaz de provider,
  - health checks,
  - session manager,
  - command dispatcher.

**Resultado:** menor fricción de arranque y base para capacidades reales, no solo documentación.

### B. Multi-provider real

- Adaptadores con fallback por costo/latencia/disponibilidad.
- Política explícita de selección de proveedor.

**Resultado:** resiliencia y menor lock-in.

### C. Observabilidad mínima

- Logs estructurados para comandos críticos.
- Métricas básicas de uso y tiempos de respuesta.

**Resultado:** depuración y mejora continua basada en evidencia.

### D. Packaging por perfiles

- Perfil `portable-docs` (actual).
- Perfil `runtime-lite` (doctor + core mínimo + adapters básicos).

**Resultado:** distribución clara para distintos tipos de usuario.

## Qué NO copiar de Hermes (por ahora)

- Gateway completo multi-canal, cron engine avanzado y superficie runtime extensa.
- Componentes que exijan credenciales reales por defecto.
- Cualquier flujo que aumente riesgo de fuga de secretos.

## Plan de ejecución recomendado

1. **Fase 1 (rápida):** consolidar doctor + bootstrap + checks automáticos.
2. **Fase 2:** construir `runtime-lite` con core y adapters básicos.
3. **Fase 3:** añadir observabilidad y fallback policies.
4. **Fase 4:** evaluar gateway/cron solo si hay demanda real.

## Criterio de éxito

Un usuario que clona el repo debe poder:

- verificar su instalación en minutos,
- operar memoria y contexto sin setup complejo,
- entender qué hacer, cuándo hacerlo y con qué comando,
- extender el sistema de forma segura y portable.
