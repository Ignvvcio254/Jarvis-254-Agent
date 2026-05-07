# Changelog

Todos los cambios notables a este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado con [SemVer](https://semver.org/lang/es/).

## [Unreleased]

## [0.1.0] — 2026-05-06

### Added
- Contrato operativo completo (`CLAUDE.md`) con motor de decisión de 8 arquetipos.
- Pack de 1400+ skills procedurales en `skills/`.
- Sistema de memoria wiki en `cerebro/` (índice, log, sesiones, fuentes).
- Runtime ejecutable `jarvis_runtime.py` con subcomandos: `doctor`, `providers`, `plan`, `session`, `memory`.
- Diagnóstico `jarvis_doctor.py` con modo `--repo-only` para validación de instalación.
- Comandos slash en `commands/` (memoria, consumo, ag-project, etc.).
- Sistema SaaS System + PRP + bucle agéntico para features complejas.
- Reglas por stack en `rules/` (common, web, mobile, backend).
- Templates MCP provider-agnostic en `mcp/`.
- Documentación reorganizada en `docs/` — root limpio con 5 archivos top-level.
- Playbook de adopción de patrones desde NousResearch/hermes-agent.
- Sanitización formal con `quarantine/` y política documentada.

[Unreleased]: https://github.com/Ignvvcio254/Jarvis-254-Agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ignvvcio254/Jarvis-254-Agent/releases/tag/v0.1.0
