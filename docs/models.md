# Multi-model gateway — any model in Claude Code's `/model` picker

Claude Code talks to **one** `ANTHROPIC_BASE_URL` per session. `models/modelo-proxy.mjs` is a local
gateway that looks at the `model` field of each request:

| Model name | Goes to |
|---|---|
| `claude-*`, `sonnet`, `opus`… | `api.anthropic.com` **byte for byte** with your own credentials (subscription login passes untouched, never read or stored). |
| `provider/model` (e.g. `nim/z-ai/glm-5.3`, `gem/gemini-3-flash`) | That provider from `gateway.json`. OpenAI-compatible providers (NVIDIA NIM, Gemini, Groq, Mistral, Cerebras, xAI, Ollama, Kilo) are translated Anthropic ⇄ OpenAI, including streaming and tool calls. |
| `auto/<chain>` (e.g. `auto/barato`, `auto/codigo`) | A fallback chain: on 429/5xx/network/timeout it moves to the next model without Claude Code noticing. |

## Security model

- Listens on `127.0.0.1` only; rejects non-loopback `Host`, any `Origin`/`Sec-Fetch-Site` (no CSRF / DNS rebinding).
- Routes that spend provider keys require a session token (`x-gateway-token`); the launcher proves the
  process on the port is *this* proxy (HMAC challenge) before sending anything.
- A provider's key never travels to another provider; base URLs are restricted to an allowlist (https).
- No bodies, headers or keys are logged. Per-provider quotas (`cuota_tokens_dia`, `cuota_peticiones_hora`) cap spend.
- Shuts itself down after `MODELO_PROXY_IDLE_MIN` minutes idle.

## Setup

1. `python install.py` (copies the proxy to `~/.claude/scripts/` and, only if absent,
   `~/.claude/profiles/gateway.json` + `multi.settings.json`).
2. Put your keys in environment variables or in `~/.claude/.env` (or point `JARVIS_ENV_FILE` elsewhere).
   `gateway.json` only references them as `"key": "env:NVIDIA_API_KEY"` — **never** write keys in it.

   ```
   NVIDIA_API_KEY=...        # build.nvidia.com — free tier
   NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
   GEMINI_API_KEY=...        # aistudio.google.com — free tier
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```
3. Launch:
   - **Windows:** `pwsh ~/.claude/scripts/claude-multi.ps1` — starts the proxy if needed, verifies it, and opens
     Claude Code with the extra models in `/model`. If anything fails it falls back to plain Claude.
     `CLAUDE_PLAIN=1` skips the gateway entirely.
   - **macOS/Linux:**
     ```bash
     export MODELO_PROXY_TOKEN=$(openssl rand -hex 32)
     node ~/.claude/scripts/modelo-proxy.mjs &
     ANTHROPIC_BASE_URL=http://127.0.0.1:8787 \
     ANTHROPIC_CUSTOM_HEADERS="x-gateway-token: $MODELO_PROXY_TOKEN" \
       claude --settings ~/.claude/profiles/multi.settings.json
     ```

## Adding a provider or model

1. Add a provider in `gateway.json → providers`:
   ```json
   "myprov": { "kind": "openai", "base": "https://api.example.com/v1", "key": "env:MYPROV_API_KEY", "maxOut": 8192, "maxTools": 128 }
   ```
   (`kind: "anthropic"` for providers that speak the Anthropic Messages API natively.)
   Add its host to `MODELO_PROXY_HOSTS_OK` if it isn't in the default allowlist.
2. Add the model to the picker in `multi.settings.json → modelPicker.options` as `"myprov/model-id"`.
3. Optionally add it to a chain in `gateway.json → combos`.
4. Check it: `node ~/.claude/scripts/salud-modelos.mjs` (health of every model; reads the launcher's token, Windows) and
   `node ~/.claude/scripts/model_radar.mjs` (discovers new free models on OpenRouter/Kilo/Gemini).

## Other tools

- `cli-modelos.mjs` — expose another CLI's subscription as a model (e.g. `cli/codex`).
- Tests: `node --test models/*.test.mjs` (translator + proxy security).
