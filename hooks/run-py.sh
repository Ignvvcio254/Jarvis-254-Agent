#!/usr/bin/env sh
# Runs a hook script with whichever Python 3 this machine has (python3 on macOS/Linux,
# python on Windows, where "python3" may be a Store stub). Never blocks Claude if Python is missing.
for py in python3 python py; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c "import sys; sys.exit(sys.version_info < (3, 8))" >/dev/null 2>&1; then
    exec "$py" "$@"
  fi
done
echo "[jarvis] Python 3.8+ not found; hook skipped" >&2
exit 0
