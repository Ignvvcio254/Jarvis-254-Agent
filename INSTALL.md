# Installation Guide — Jarvis 254 Agent

## Objetivo

Instalar Jarvis de forma portable y segura, con comandos, memoria, skills y base SaaS System listos para operar.

## Requisitos

- [Claude Code](https://claude.ai/code) instalado y autenticado
- Node.js 18+
- Python 3.11+
- Git

## 1) Clonar repositorio

```bash
git clone https://github.com/Ignvvcio254/Jarvis-254-Agent.git
cd Jarvis-254-Agent
```

Validación del clon:

```bash
python jarvis_doctor.py --repo-only
python jarvis_runtime.py doctor --repo-only
```

## 2) Instalar contrato principal (`CLAUDE.md`)

```bash
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup
cp CLAUDE.md ~/.claude/CLAUDE.md
```

Reemplazar placeholders en `~/.claude/CLAUDE.md`:

- `{{YOUR_NAME}}`
- `{{GITHUB_USERNAME}}`
- `{{GITHUB_TOKEN}}` (solo local, opcional)

## 3) Instalar skills

```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

Validación rápida:

```bash
find ~/.claude/skills -maxdepth 2 -name SKILL.md | head
```

## 4) Inicializar memoria (`cerebro`)

```bash
mkdir -p ~/.claude/cerebro/sessions
cp cerebro/index.md ~/.claude/cerebro/
cp cerebro/log.md ~/.claude/cerebro/
cp cerebro/sources.md ~/.claude/cerebro/
cp cerebro/search.py ~/.claude/cerebro/
```

Validación:

```bash
cd ~/.claude/cerebro
python search.py index
python search.py stats
```

## 5) Instalar comandos slash

```bash
mkdir -p ~/.claude/commands
cp commands/*.md ~/.claude/commands/
```

Comandos clave instalados:

- `/memoria`
- `/consumo`
- `/ag-project`
- `/marketing-swarm`
- `/connect-apps-setup`

## 6) Instalar base SaaS System (PRP)

```bash
mkdir -p ~/.claude/PRPs
cp PRPs/prp-base.md ~/.claude/PRPs/
```

Esto habilita el flujo PRP + ejecución por fases.

## 7) Configurar MCP (seguro)

Opción A (plantillas MCP):

```bash
cp mcp/mcp.template.json ~/.claude.json
cp mcp/env.example .env
```

Opción B (templates de config sanitizados):

```bash
cp config/settings.template.json ~/.claude/settings.json
cp config/claude.template.json ~/.claude.json
```

Reglas:

- Nunca commitear `.env`, tokens o credenciales reales.
- Mantener rutas portables.

## 8) (Opcional) Crear archivo de goals

```bash
cat > ~/.claude/goals.md << 'EOF'
# Goals — Jarvis

## Active

*(sin goals activos — use /goal para agregar)*

## Completed

*(none)*
EOF
```

## 9) Primera sesión

Abrir Claude Code en cualquier proyecto. Jarvis cargará:

1. `~/.claude/CLAUDE.md`
2. `~/.claude/cerebro/index.md`
3. `~/.claude/goals.md` (si existe)

## Verificación funcional

Probar en Claude Code:

```text
/goal Mi primer objetivo
/goal list
/snapshot create
/insights
/memoria lint
/doctor
```

Verificación técnica local:

```bash
python jarvis_doctor.py
python jarvis_runtime.py doctor
python jarvis_runtime.py providers
python jarvis_runtime.py plan --intent "fix login bug"
```

## 10) (Opcional) Actualizar referencia Hermes para benchmark

```powershell
powershell -ExecutionPolicy Bypass -File .\sync_hermes_upstream.ps1
```

Notas:

- `upstream/` es opcional y está excluido de git.
- Sirve para análisis comparativo y extracción de patrones, no para runtime obligatorio.

## Verificación SaaS System

```text
/ag-project demo-saas fullstack
/memoria query PRP
```

Y para features complejas:

1. Generar PRP con `skills/prp/SKILL.md` + `PRPs/prp-base.md`.
2. Ejecutar por fases con `skills/bucle-agentico/SKILL.md`.

## Troubleshooting

- Skills no activan: verificar `~/.claude/skills/<skill>/SKILL.md`.
- Fallo en cerebro: ejecutar `python ~/.claude/cerebro/search.py index`.
- Error MCP: validar `node --version` y revisar `~/.claude.json`.
- Comandos slash no aparecen: confirmar copia en `~/.claude/commands/`.
