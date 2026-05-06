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

### Linux / macOS
1. Clone this repository.
2. Open your terminal.
3. Make the installer executable and run it:
   ```bash
   chmod +x install.sh
   ./install.sh
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

## 📖 How to Use This Environment

### Leveraging the Skill Library
Once installed, your agent has access to the specialized skills. You can invoke them by referencing the domain or specific skill name. The agent will use these to provide production-grade code, security audits, and architecture reviews without needing repetitive prompting.

### Working with Cerebro Memory
Cerebro transforms your `.claude` folder into a living knowledge base. 
- **Recall**: The agent can refer back to previous `Session Nodes` to resume complex tasks without re-explaining the context.
- **Synthesis**: As you work, the agent synthesizes patterns into `Concept Nodes`, creating a permanent architectural record of your project.

### Dynamic Model Routing
The `model_router.py` helps you optimize token spend and latency. It analyzes the complexity of your request:
- **Simple tasks** $\rightarrow$ Haiku
- **Complex implementation** $\rightarrow$ Sonnet
- **Deep architectural reasoning** $\rightarrow$ Opus

## 🛡️ Portability & Safety
- **No Personal Data**: All session histories and private tokens have been removed.
- **Dynamic Paths**: The installer handles path resolution automatically using `{{HOME}}` templates.
- **Safe Defaults**: The included `settings.local.json` provides a balanced set of permissions for power users.

## 🛠️ Troubleshooting
- **Windows Permissions**: If `install.ps1` fails, ensure you are running PowerShell as Administrator and have set the `ExecutionPolicy` to `Bypass`.
- **Linux/macOS Permissions**: Ensure the `install.sh` script has execution permissions (`chmod +x`).
- **MCP Tools**: This framework configures the *hooks* for MCPs. You must still install the corresponding MCP servers (e.g., `claude-mem`) on your machine for the tools to function.
