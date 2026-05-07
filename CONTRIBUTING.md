# Contribuir a Jarvis-254-Agent

Gracias por tu interés. Este proyecto sigue un modelo de cambios mínimos y reversibles.

## Antes de contribuir

1. Lee [`CLAUDE.md`](CLAUDE.md) — es el contrato operativo del agente.
2. Corre el diagnóstico para confirmar que tu entorno es válido:
   ```bash
   python jarvis_doctor.py --repo-only
   ```
3. Lee [`docs/sanitization.md`](docs/sanitization.md) — nada con credenciales reales entra al repo.

## Tipos de contribución

### Agregar un skill nuevo

- Crear `skills/<nombre>/SKILL.md` con frontmatter mínimo:
  ```markdown
  ---
  name: nombre-del-skill
  description: Qué hace en una línea
  ---
  ```
- El nombre debe ser kebab-case y único.
- No modificar skills existentes sin justificación explícita en el PR.

### Agregar un comando slash

- Crear `commands/<nombre>.md` siguiendo el formato de comandos existentes.
- Actualizar [`docs/commands.md`](docs/commands.md) con la entrada correspondiente.
- Actualizar [`docs/command-skill-matrix.md`](docs/command-skill-matrix.md) si el comando activa un workflow.

### Correr el diagnóstico local

```bash
python jarvis_doctor.py          # diagnóstico completo
python jarvis_doctor.py --repo-only  # solo valida estructura del repo
```

## Reglas del PR

- Un PR = un cambio cohesivo. No mezclar refactors con features.
- Describir el **por qué** del cambio, no solo el qué.
- Ningún secreto, token, ni credencial real — usar placeholders (`{{YOUR_API_KEY}}`).
- Si el cambio toca `CLAUDE.md`, explicar el impacto en el comportamiento del agente.

## Código de conducta

Trato respetuoso en todos los canales. Issues y PRs en inglés o español.
