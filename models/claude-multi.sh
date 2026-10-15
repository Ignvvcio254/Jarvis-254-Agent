#!/usr/bin/env bash
# Claude Code with EVERY model in the same /model picker (macOS / Linux / WSL / Git Bash).
#   Your Claude models (subscription, untouched) + other providers through the local gateway.
# Usage:  claude-multi.sh [claude args]
#
# Guarantees (none of this can leave you without Claude):
#   - If the gateway does not start, or the port is held by something else, plain Claude runs.
#   - CLAUDE_PLAIN=1 skips the gateway entirely.
#   - The gateway shuts itself down after MODELO_PROXY_IDLE_MIN minutes idle.
# Security:
#   - Session token in ~/.cache/claude-gateway/token (mode 600), sent as x-gateway-token.
#   - Before sending anything, the launcher checks the process on the port is THIS proxy (HMAC proof).
#   - The proxy gets a MINIMAL environment: system paths + provider keys only.
set -euo pipefail

PORT="${MODELO_PROXY_PORT:-8787}"
BASE="http://127.0.0.1:$PORT"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
PROFILE="$CLAUDE_DIR/profiles/multi.settings.json"
PROXY="$CLAUDE_DIR/scripts/modelo-proxy.mjs"
TOKEN_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/claude-gateway"
TOKEN_FILE="$TOKEN_DIR/token"
ENV_FILE="${JARVIS_ENV_FILE:-$CLAUDE_DIR/.env}"
KEYS=(OPENROUTER_API_KEY NVIDIA_API_KEY NVIDIA_BASE_URL GEMINI_API_KEY ZAI_API_KEY XAI_API_KEY GROQ_API_KEY MISTRAL_API_KEY CEREBRAS_API_KEY)

plain() { exec claude "$@"; }

[[ "${CLAUDE_PLAIN:-}" == "1" ]] && plain "$@"
if [[ ! -f "$PROFILE" || ! -f "$PROXY" ]]; then echo "gateway not installed; running plain Claude" >&2; plain "$@"; fi
command -v node >/dev/null || { echo "node not found; running plain Claude" >&2; plain "$@"; }
command -v curl >/dev/null || { echo "curl not found; running plain Claude" >&2; plain "$@"; }

if [[ ! -s "$TOKEN_FILE" ]]; then
  mkdir -p "$TOKEN_DIR" && chmod 700 "$TOKEN_DIR"
  (umask 077; node -e 'process.stdout.write(require("crypto").randomBytes(32).toString("hex"))' > "$TOKEN_FILE")
fi
TOKEN="$(cat "$TOKEN_FILE")"

proxy_ok() {
  local nonce body proof expected
  nonce="$(node -e 'process.stdout.write(require("crypto").randomBytes(16).toString("hex"))')"
  body="$(curl -fsS --max-time 2 "$BASE/__proxy_health?n=$nonce" 2>/dev/null)" || return 1
  proof="$(printf '%s' "$body" | node -e 'let d="";process.stdin.on("data",c=>d+=c).on("end",()=>{try{const j=JSON.parse(d);process.stdout.write(j.ok===true?String(j.proof||""):"")}catch{}})')"
  expected="$(TOKEN="$TOKEN" NONCE="$nonce" node -e 'process.stdout.write(require("crypto").createHmac("sha256",process.env.TOKEN).update(process.env.NONCE).digest("hex"))')"
  [[ -n "$proof" && "$proof" == "$expected" ]]
}

read_key() {  # environment first, then the env file; never printed
  local name="$1" val="${!1:-}"
  if [[ -z "$val" && -f "$ENV_FILE" ]]; then
    val="$(grep -E "^[[:space:]]*$name[[:space:]]*=" "$ENV_FILE" | head -1 | cut -d= -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^["'\'']//' -e 's/["'\'']$//')"
  fi
  printf '%s' "$val"
}

if ! proxy_ok; then
  env_args=(PATH="$PATH" HOME="$HOME" TMPDIR="${TMPDIR:-/tmp}" MODELO_PROXY_PORT="$PORT" MODELO_PROXY_TOKEN="$TOKEN")
  found=0
  for k in "${KEYS[@]}"; do
    v="$(read_key "$k")"
    if [[ -n "$v" ]]; then env_args+=("$k=$v"); found=$((found + 1)); fi
  done
  env -i "${env_args[@]}" nohup node "$PROXY" >/dev/null 2>&1 &
  for _ in $(seq 1 24); do proxy_ok && break; sleep 0.25; done
  if ! proxy_ok; then
    echo "gateway did not start (or port $PORT is taken); running plain Claude without extra models" >&2
    plain "$@"
  fi
  [[ "$found" -eq 0 ]] && echo "no provider keys found: Claude models work, the others will error" >&2
fi

# Only the base URL and the session header change. ANTHROPIC_AUTH_TOKEN is NOT set: your login still rules.
ANTHROPIC_BASE_URL="$BASE" ANTHROPIC_CUSTOM_HEADERS="x-gateway-token: $TOKEN" exec claude --settings "$PROFILE" "$@"
