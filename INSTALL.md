# Installation Guide — Jarvis 254 Agent

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and authenticated
- Node.js 18+ (for MCP servers)
- Python 3.11+ (for cerebro/search.py)
- Git

## Step 1 — Clone

```bash
git clone https://github.com/Ignvvcio254/Jarvis-254-Agent.git
cd Jarvis-254-Agent
```

## Step 2 — Install CLAUDE.md

```bash
[ -f ~/.claude/CLAUDE.md ] && cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup
cp CLAUDE.md ~/.claude/CLAUDE.md
```

Open `~/.claude/CLAUDE.md` and replace placeholders:
- `{{YOUR_NAME}}` → your name (how Jarvis will address you)
- `{{GITHUB_USERNAME}}` → your GitHub username
- `{{GITHUB_TOKEN}}` → your GitHub personal access token (optional)

## Step 3 — Install Skills

```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

## Step 4 — Initialize Cerebro Wiki

```bash
mkdir -p ~/.claude/cerebro/sessions
cp cerebro/index.md ~/.claude/cerebro/
cp cerebro/log.md ~/.claude/cerebro/
cp cerebro/sources.md ~/.claude/cerebro/
cp cerebro/search.py ~/.claude/cerebro/

# Verify search engine works
cd ~/.claude/cerebro
python search.py index
python search.py stats
```

## Step 5 — Install Slash Commands

```bash
mkdir -p ~/.claude/commands
cp commands/memoria.md ~/.claude/commands/
```

## Step 6 — Configure MCP Servers (Optional)

Edit `~/.claude.json` to add MCP servers. Minimum recommended:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/your/projects"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    },
    "github-git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    },
    "desktop-commander": {
      "command": "npx",
      "args": ["-y", "@wonderwhy-er/desktop-commander"]
    }
  }
}
```

## Step 7 — Create Goals File (Optional)

```bash
cat > ~/.claude/goals.md << 'EOF'
# Goals — Jarvis

## Active

*(no active goals yet — use /goal to add one)*

## Completed

*(none yet)*
EOF
```

## Step 8 — First Session

Open Claude Code in any project. Jarvis will:

1. Read `~/.claude/CLAUDE.md` — core configuration loaded
2. Read `~/.claude/cerebro/index.md` — accumulated context loaded
3. Load active goals from `~/.claude/goals.md`
4. Be ready

## Verification

```
# In Claude Code:
/goal My first Jarvis goal
/goal list
/snapshot create
/insights
```

If all commands respond correctly, Jarvis is fully operational.

## Troubleshooting

**Skills not activating** — Ensure files are at `~/.claude/skills/<name>/SKILL.md`.
**Cerebro index not found** — Run `python ~/.claude/cerebro/search.py index`.
**MCP errors** — Verify Node.js installed (`node --version`).
