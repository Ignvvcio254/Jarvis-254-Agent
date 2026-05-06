# /ag-project — Crear proyecto con integración Jarvis↔Antigravity

Inicializa un nuevo proyecto con la estructura de handoff para colaboración entre Jarvis y el agente de Antigravity.

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
