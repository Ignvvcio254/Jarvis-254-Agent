<div align="center">

<!-- BANNER PLACEHOLDER — replace with your image -->
<!-- ![Jarvis-254-Agent Banner](assets/banner.png) -->

# 🤖 Jarvis-254-Agent

### The open-source AI engineering co-pilot that unifies the best the community has built — into one structured, portable system.

[![CI](https://github.com/Ignvvcio254/Jarvis-254-Agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Ignvvcio254/Jarvis-254-Agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-1400%2B-blueviolet)](#-skills--1400-procedural-skills)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

**Not a replacement. Not a fork. A unification.**

[📦 Install](#-installation) · [⚡ Quick Start](#-quick-start) · [📖 Docs](docs/README.md) · [🤝 Credits](#-credits--community) · [🛠 Contributing](CONTRIBUTING.md)

</div>

---

## 🧠 What Is This?

Most AI agent setups are good **in isolation**.

- A great CLAUDE.md contract — but no persistent memory.
- 1400 community skills — but no lifecycle curation.
- A powerful runtime — but no structured workflow system.
- Hermes' learning loop — but locked to one provider.

**Jarvis-254-Agent unifies them.**

It takes the best patterns from the open-source community — NousResearch/hermes-agent, Antigravity, SaaS Factory, and more — and composes them into a single, structured, portable system you can clone in minutes and run immediately.

> **We don't own any of these systems. We curate, credit, and compose them.**

---

## ⚡ Quick Start

```bash
# 1. Clone
git clone https://github.com/Ignvvcio254/Jarvis-254-Agent.git
cd Jarvis-254-Agent

# 2. Diagnose your setup
python jarvis_doctor.py --repo-only

# 3. Plan your first task
python jarvis_runtime.py plan --intent "build a REST API with FastAPI"

# 4. Search your memory wiki (FTS5 BM25)
python jarvis_runtime.py memory search "authentication patterns"
```

That's it. No npm install. No Docker. No cloud account required.

---

## 🏗 Architecture

```
Jarvis-254-Agent/
│
├── CLAUDE.md              ← 🧠 Agent operating contract (the core)
├── jarvis_runtime.py      ← ⚙️  Executable runtime (plan/memory/curator/session)
├── jarvis_doctor.py       ← 🩺 Setup diagnostics
│
├── commands/              ← 💬 Slash commands (/memoria, /consumo, /curator...)
├── skills/                ← 🎯 1400+ procedural skills by domain
├── rules/                 ← 📏 Engineering rules by stack (common → web → mobile)
├── cerebro/               ← 💾 Persistent memory wiki (FTS5-indexed)
├── PRPs/                  ← 📋 Product Requirement Prompts (SaaS Factory)
├── jarvis_core/           ← 🔧 Python core modules
│   ├── cerebro_index.py   ←     FTS5 search + ContextCompressor (protect_n)
│   ├── skill_curator.py   ←     Skill lifecycle manager (Hermes pattern)
│   ├── providers.py       ←     Multi-provider adapter
│   ├── sessions.py        ←     Session store
│   └── policy.py          ←     Workflow recommender
├── mcp/                   ← 🔌 MCP provider templates (provider-agnostic)
├── design-systems/        ← 🎨 Visual design systems library
├── config/                ← 🔒 Sanitized config templates
└── docs/                  ← 📚 Full documentation index
```

---

## 🎯 Skills — 1400+ Procedural Skills

The largest curated collection of Claude Code skills, organized by domain:

| Domain | Examples |
|---|---|
| 🏗 Architecture | `architect`, `ddd-strategic-design`, `microservices-patterns` |
| 🌐 Frontend | `react-best-practices`, `nextjs-app-router-patterns`, `scroll-experience` |
| ⚙️ Backend | `fastapi-pro`, `nodejs-backend-patterns`, `go-concurrency-patterns` |
| 🔐 Security | `security-audit`, `api-security-testing`, `penetration-testing` |
| 🤖 AI/Agents | `ai-agents-architect`, `rag-engineer`, `langchain-architecture` |
| 📊 Data | `data-engineer`, `sql-optimization-patterns`, `vector-database-engineer` |
| ☁️ DevOps | `kubernetes-architect`, `terraform-specialist`, `github-actions-templates` |
| 📱 Mobile | `flutter-expert`, `react-native-architecture`, `ios-developer` |

Skills are **auto-curated** by `SkillCurator` — stale skills get marked, old ones archived. Never deleted.

```bash
# Check skill health
python jarvis_runtime.py curator --status

# Preview curation (safe dry-run by default)
python jarvis_runtime.py curator --verbose
```

---

## 💾 Memory System — Persistent Across Sessions

Based on the **claude-brain** pattern. Your agent remembers decisions, context, and architecture across every session.

```
cerebro/
├── index.md      ← Dense catalog — read this first every session
├── log.md        ← Append-only change log
├── sources.md    ← Pointers to core files
└── sessions/     ← One .md per work session
```

**FTS5-powered search** (BM25 ranking, zero external deps):

```bash
python jarvis_runtime.py memory search "authentication"
python jarvis_runtime.py memory search "database migration" --limit 5
```

**Context compression** following the Hermes `protect_n` contract:
- `protect_first_n = 3` — system context never compressed
- `protect_last_n = 6` — active conversation preserved
- Compresses only when usage ≥ 75% of context window

---

## 🔄 SaaS Sistem — Agentic Workflow System

For complex features, use the PRP (Product Requirement Prompt) system:

```
1. /prp [feature description]   → Generate PRP-XXX-feature.md
2. Review & approve the plan
3. /bucle-agentico               → Execute phase by phase, just-in-time context
4. Auto-Blindaje                  → Errors documented, never repeated
```

This is the **SaaS Factory** pattern — phased execution with living documentation.

---

## 🩺 Doctor — Instant Health Check

```bash
# Validate repo structure only
python jarvis_doctor.py --repo-only

# Full local setup check
python jarvis_doctor.py
```

Output:
```
[OK] CLAUDE.md
[OK] docs/commands.md
[OK] cerebro/index.md
...
All checks passed.
```

---

## 📋 Runtime Commands

```bash
python jarvis_runtime.py <command>
```

| Command | Description |
|---|---|
| `doctor` | Setup diagnostics |
| `providers` | Show LLM provider readiness |
| `plan --intent "..."` | Recommend track + commands for a task |
| `session start --goal "..."` | Start a tracked work session |
| `memory search "query"` | FTS5 BM25 search over cerebro/ |
| `memory index` | Rebuild memory index |
| `curator --status` | Show skill lifecycle state |
| `curator --verbose` | Preview curation (dry-run) |
| `curator --execute` | Apply curation changes |

---

## 🛡 Security & Portability

- ❌ No secrets, tokens, or credentials in the repo — ever.
- ✅ All sensitive config lives as `{{PLACEHOLDER}}` templates.
- ✅ `quarantine/` and `upstream/` are git-ignored.
- ✅ CI scans for leaked credentials on every PR.
- ✅ `jarvis_doctor.py` validates structure before any local install.

---

## 🤝 Credits & Community

**Jarvis-254-Agent does not own or claim any of the following.**
We stand on the shoulders of giants. These projects made this possible:

| Project | What we adopted | License |
|---|---|---|
| [NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) ⭐134k | Curator pattern, `protect_first_n/last_n`, FTS5 memory, doctor pattern | MIT |
| [Antigravity / Everything Claude Code](https://github.com/anthropics/everything-claude-code) | 1400+ skill pack, skill schema, agent orchestration patterns | MIT |
| [SaaS Factory](https://github.com/Agentic-Insights/saas-factory) | PRP system, bucle agéntico, agentic workflow structure | MIT |
| [claude-brain](https://github.com/AgustinGoniDev/claude-brain-skill) | cerebro/ wiki system, session continuity contract | MIT |
| [Anthropic Claude Code](https://github.com/anthropics/claude-code) | The agent runtime everything runs on | © Anthropic |

> **Philosophy:** We curate and compose. Every pattern we adopt is credited, every license respected. If you built something we use and want better attribution, open an issue — we'll fix it immediately.

---

## 🚀 Installation

See [`INSTALL.md`](INSTALL.md) for the full guide. TL;DR:

```bash
# Copy commands to Claude Code
cp -r commands/* ~/.claude/commands/

# Copy skills to Claude Code
cp -r skills/* ~/.claude/skills/

# Copy cerebro wiki
cp -r cerebro/* ~/.claude/cerebro/

# Verify
python jarvis_doctor.py
```

---

## 📚 Documentation

| Doc | Purpose |
|---|---|
| [`docs/commands.md`](docs/commands.md) | All slash commands and their behavior |
| [`docs/command-skill-matrix.md`](docs/command-skill-matrix.md) | Command → skill → workflow mapping |
| [`docs/skills-guide.md`](docs/skills-guide.md) | How to navigate 1400+ skills |
| [`docs/saas-factory.md`](docs/saas-factory.md) | PRP + agentic workflow system |
| [`docs/runtime-lite.md`](docs/runtime-lite.md) | `jarvis_runtime.py` full reference |
| [`docs/context-compression.md`](docs/context-compression.md) | Token optimization: protect_n + FTS5 |
| [`docs/hermes-adoption.md`](docs/hermes-adoption.md) | What we adopted from Hermes and why |
| [`docs/sanitization.md`](docs/sanitization.md) | Security policy and quarantine rules |

---

## 🤝 Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) first. Key rules:

- Minimum viable changes — one PR, one concern.
- All skills need frontmatter (`name`, `description`).
- No secrets. Ever. CI will catch it.
- Credit any external pattern you introduce.

---

## 📄 License

MIT — see [`LICENSE`](LICENSE).

This project composes MIT-licensed community work. Attribution is in the [Credits](#-credits--community) section above. If you use this project, you inherit the responsibility to credit the upstream sources.

---

<div align="center">

**Built with ❤️ by the community, for the community.**

*Jarvis-254-Agent is not affiliated with Anthropic, NousResearch, or any credited project.*
*We are an independent open-source composition effort.*

⭐ **Star this repo if it saved you time. Share it if it helped your agent.**

</div>
