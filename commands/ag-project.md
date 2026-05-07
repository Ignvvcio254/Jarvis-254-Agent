---
description: Crear proyecto con handoff Jarvis↔Antigravity.
argument-hint: "<nombre-del-proyecto> [tipo: web|api|fullstack|script]"
---

# /ag-project — Crear proyecto con integración Jarvis↔Antigravity

Inicializa un nuevo proyecto con la estructura de handoff para colaboración entre Jarvis y el agente de Antigravity.

## Comportamiento operativo

- Crea un proyecto nuevo desde cero.
- Deja estructura mínima para ejecución con handoff explícito.
- Prioriza portabilidad (sin rutas absolutas incrustadas en archivos generados).
- Devuelve al usuario la ruta final y pasos inmediatos de arranque.

## Uso
```
/ag-project <nombre-del-proyecto> [tipo: web|api|fullstack|script]
```

## Pasos que ejecuta Jarvis

1. Crear carpeta del proyecto con estructura base según el tipo
2. Inicializar `.agent/` con templates de CONTEXT, HANDOFF, PROGRESS y DECISIONS
3. Crear `GEMINI.md` en la raíz del proyecto con instrucciones para el agente de Antigravity
4. Inicializar git con `.gitignore` apropiado
5. Crear `README.md` con la arquitectura inicial
6. Reportar la ruta y cómo abrirlo en Antigravity

## Output esperado

- Carpeta de proyecto creada.
- Subcarpeta `.agent/` con contexto y trazabilidad inicial.
- Documento `GEMINI.md` listo para uso del agente colaborador.
- `README.md` inicial con arquitectura base.

## Reglas de seguridad

- No escribir secretos/API keys en archivos iniciales.
- No modificar proyectos existentes sin intención explícita del usuario.
- Mantener plantillas legibles y neutrales al proveedor.

## Estructura generada

```
<nombre>/
├── .agent/
│   ├── CONTEXT.md      ← contexto del proyecto
│   ├── HANDOFF.md      ← instrucciones para Antigravity (vacío inicial)
│   ├── PROGRESS.md     ← log de avances
│   └── DECISIONS.md    ← decisiones arquitectónicas
├── GEMINI.md           ← instrucciones sistema para agente Antigravity
├── .gitignore
└── README.md
```

## Plantilla GEMINI.md de proyecto

El `GEMINI.md` que Jarvis crea en cada proyecto incluye:
- Contexto del proyecto (stack, estructura, convenciones)
- Instrucciones de handoff: leer `.agent/HANDOFF.md` antes de actuar
- Instrucciones de log: escribir en `.agent/PROGRESS.md` al completar
- Reglas del proyecto (estilo de código, no tocar ciertos archivos)

## Plantilla CONTEXT.md inicial

```markdown
# Contexto del Proyecto — <nombre>

## Stack
[tecnologías]

## Estructura
[árbol de directorios relevante]

## Convenciones
[naming, estilo, patrones usados]

## Estado actual
[qué está hecho, qué falta]

## Última actualización
[fecha] — Jarvis
```

## Abrir en Antigravity

Después de crear el proyecto:
```bash
antigravity <ruta-del-proyecto>
```

O desde Antigravity: File → Open Folder → seleccionar la carpeta del proyecto.
