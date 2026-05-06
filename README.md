# 🛠️ Jarvis Environment
### Professional AI Engineering Workspace

This repository provides a portable, high-fidelity export of a professional Claude/OpenCode environment. It is designed to give developers instant access to advanced reasoning, structured memory, and a massive library of specialized engineering skills.

## 🚀 Installation

### Windows
1. Clone this repository.
2. Open PowerShell as Administrator.
3. Run:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\install.ps1
   ```
4. Restart Claude Code.

## 📦 What's Inside?

### 1. Specialized Skill Library (`/skills`)
A curated collection of 1,400+ skills categorized by domain:
- **AI Engineering**: Prompting, RAG, Agent architecture.
- **Software Dev**: Full-stack patterns, language-specific best practices.
- **Infrastructure**: Cloud-native, DevOps, Security audits.
- **Design**: Visual blueprints and UI/UX patterns.

### 2. Intelligence Routing (`/scripts`)
Includes the `model_router.py`, which automatically classifies your prompts and recommends the best model (Haiku $\rightarrow$ Sonnet $\rightarrow$ Opus) to balance speed and depth.

### 3. Cerebro Memory Engine (`/memory`)
A structured, wiki-based long-term memory system. It prevents context loss across sessions by organizing knowledge into:
- **Session Nodes**: Capture of specific work units.
- **Concept Nodes**: Synthesized abstractions.
- **ADRs**: Architecture Decision Records.

### 4. Visual Design Systems (`/design-systems`)
A knowledge base of visual blueprints (Liquid Glass, Neumorphism, etc.) that allows the agent to generate high-fidelity SCSS/CSS styles consistently.

### 5. Operational Configs (`/config`)
Portable templates for `settings.json` and `settings.local.json`, including a comprehensive allow-list of safe and powerful commands.

## 📖 Usage & Customization

- **Adding Skills**: Simply drop new `SKILL.md` files into the appropriate category in `/skills`.
- **Managing Memory**: Use the `/memoria` commands (if implemented in your agent) to ingest and query the Cerebro wiki.
- **Modifying Routing**: Edit `model_router.py` to adjust how your prompts are classified.

## 🛡️ Portability & Safety
- **No Personal Data**: All session histories and private tokens have been removed.
- **Dynamic Paths**: The installer handles path resolution automatically using `{{HOME}}` templates.
- **Safe Defaults**: The included `settings.local.json` provides a balanced set of permissions for power users.
