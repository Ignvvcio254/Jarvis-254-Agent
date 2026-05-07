# Commands Index

Catálogo oficial de comandos slash en `commands/`, con comportamiento esperado, entradas, salidas y relación con skills/workflows.

## Convención de comando

Cada archivo en `commands/` debe incluir frontmatter mínimo:

- `description`
- `argument-hint`

Y debe documentar explícitamente:

- propósito,
- inputs esperados,
- pasos de ejecución,
- output final,
- reglas de seguridad.

Checklist rápido para revisión documental:

- ¿Se entiende cuándo usar el comando?
- ¿Los argumentos están descritos con casos válidos e inválidos?
- ¿La salida esperada está explicitada?
- ¿Hay reglas de seguridad y límites de alcance?

## Catálogo operativo

### `/memoria`

- Archivo: `commands/memoria.md`
- Objetivo: operar el wiki global de Jarvis (`ingest`, `query`, `lint`).
- Entradas:
  - `ingest` (default)
  - `query <pregunta>`
  - `lint`
- Output:
  - nodos de sesión actualizados o respuesta citada por nodos.
- Dependencias:
  - `cerebro/` (index, log, sessions)
  - script de búsqueda (`cerebro/search.py`)

### `/consumo`

- Archivo: `commands/consumo.md`
- Objetivo: estimar consumo de sesión y sugerir/gestionar modo Caveman.
- Entradas:
  - `status` (default)
  - `lite|full|ultra|off`
- Output:
  - reporte de consumo + recomendación de modo.
- Dependencias:
  - historial de sesión actual.

### `/ag-project`

- Archivo: `commands/ag-project.md`
- Objetivo: crear proyecto base con handoff Jarvis↔Antigravity.
- Entradas:
  - `<nombre-del-proyecto>`
  - `[tipo: web|api|fullstack|script]`
- Output:
  - estructura inicial con `.agent/`, `GEMINI.md`, `README.md`, git init.
- Dependencias:
  - filesystem local.

### `/marketing-swarm`

- Archivo: `commands/marketing-swarm.md`
- Objetivo: ejecutar análisis/acción de marketing con 7 workers en paralelo.
- Entradas:
  - contexto de producto
  - objetivo del swarm
- Output:
  - síntesis multi-dominio (SEO/CRO/Copy/Paid/Growth/Sales/Strategy).
- Dependencias:
  - Claude Flow
  - skills de marketing

### `/connect-apps-setup`

- Archivo: `commands/connect-apps-setup.md`
- Objetivo: configurar MCP de Composio para apps externas.
- Entradas:
  - API key de Composio (directa o implícita según flujo)
- Output:
  - configuración local de MCP connect-apps.
- Dependencias:
  - archivo local de configuración MCP.

### `/doctor`

- Archivo: `commands/doctor.md`
- Objetivo: validar estado operativo del clon/instalación Jarvis.
- Entradas:
  - `repo-only`
  - `full` (default)
- Output:
  - estado de checks + faltantes + siguiente acción sugerida.
- Dependencias:
  - `jarvis_doctor.py`

## Mapa comando → sistema

- Memoria: `/memoria`
- Gestión de contexto/consumo: `/consumo`
- Bootstrap de proyecto: `/ag-project`
- Orquestación de marketing: `/marketing-swarm`
- Integraciones externas: `/connect-apps-setup`
- Diagnóstico del sistema: `/doctor`

## Relación con SaaS System

- `/ag-project` crea base de proyecto para ejecución ordenada.
- `/memoria` documenta decisiones y continuidad.
- `PRPs/prp-base.md` + skills `prp` y `bucle-agentico` habilitan el ciclo completo.

## Archivo complementario

Ver `SAAS_FACTORY.md` para flujo completo PRP→ejecución por fases.
Ver `COMMAND_SKILL_BEHAVIOR.md` para matriz detallada comando↔skill.
Ver `PRPs/README.md` para convención de artefactos PRP.

## Runtime CLI complementario

Además de slash commands, el repositorio expone runtime-lite ejecutable:

- `python jarvis_runtime.py doctor`
- `python jarvis_runtime.py providers`
- `python jarvis_runtime.py plan --intent "..."`
- `python jarvis_runtime.py session start|list|end`
- `python jarvis_runtime.py memory index|query|stats`

Ver `RUNTIME_LITE.md` para detalles operativos.
