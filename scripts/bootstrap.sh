#!/usr/bin/env sh
# One-line install (macOS / Linux / WSL):
#   curl -fsSL https://raw.githubusercontent.com/Ignvvcio254/Jarvis-254-Agent/main/scripts/bootstrap.sh | sh
# Clones (or updates) the repo into $JARVIS_HOME (default ~/.jarvis-254) and runs the merging installer.
set -eu
REPO="${JARVIS_REPO:-https://github.com/Ignvvcio254/Jarvis-254-Agent.git}"
DEST="${JARVIS_HOME:-$HOME/.jarvis-254}"
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
PY=""; for p in python3 python py; do if command -v "$p" >/dev/null 2>&1 && "$p" -c "import sys; sys.exit(sys.version_info < (3, 8))" >/dev/null 2>&1; then PY="$p"; break; fi; done
[ -n "$PY" ] || { echo "Python 3.8+ is required" >&2; exit 1; }
if [ -d "$DEST/.git" ]; then git -C "$DEST" pull --ff-only --quiet; else git clone --depth 1 --quiet "$REPO" "$DEST"; fi
"$PY" "$DEST/install.py" "$@"
"$PY" "$DEST/jarvis_doctor.py" || true
echo "Jarvis-254 installed. Open Claude Code in any project; update later by re-running this command."
