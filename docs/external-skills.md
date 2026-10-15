# Recommended community skills (installed from their authors)

These skills are excellent but belong to their authors and have their own licences, so Jarvis does
**not** vendor them — install them straight from the source with the [`skills`](https://github.com/vercel-labs/skills)
CLI (works for Claude Code, Codex, OpenCode, Cursor and more):

```bash
npx skills add <owner/repo> -g --skill '*' -y     # all skills of a package, user-level
npx skills add <owner/repo> -g --skill <name> -y  # just one
npx skills update -g                              # keep them current
```

| Package | What you get | Pairs with Jarvis |
|---|---|---|
| `vercel-labs/agent-skills` | React/Next.js best practices, composition patterns, view transitions, React Native, web design guidelines, deploy-to-vercel | BUILD / DESIGN archetypes |
| `vercel-labs/skills` | `find-skills`: search the open skills ecosystem from inside the agent | Skills discovery protocol |
| `google-labs-code/stitch-skills` | Stitch design generation, design-md, enhance-prompt, stitch-loop | DESIGN archetype |
| `heygen-com/hyperframes` | HTML-to-video: motion graphics, captions, product-launch and PR-to-video | Content / video work |
| `stablyai/orca` | Orca orchestration, computer use, emulators, Linear | SWARM / multi-agent |
| `intellectronica/agent-skills` | Notion API | Docs / knowledge bases |
| [`AgustinGoniDev/claude-brain-skill`](https://github.com/AgustinGoniDev/claude-brain-skill) | Installer for a per-project LLM wiki (`/brain ingest \| query \| lint`). The global wiki in `cerebro/` works without it. — `git clone https://github.com/AgustinGoniDev/claude-brain-skill ~/.claude/skills/claude-brain` | Memory |
| [`JuliusBrussee/caveman`](https://github.com/JuliusBrussee/caveman) | Progressive output compression (used by the CAVEMAN section of `CLAUDE.md`) — `git clone https://github.com/JuliusBrussee/caveman ~/.claude/skills/caveman` | Token economy |

Rule of thumb: install a package when a task needs it, not all at once — every skill's description is loaded
into context, so fewer, relevant skills beat many idle ones.
