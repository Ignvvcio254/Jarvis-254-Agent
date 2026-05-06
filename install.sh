#!/bin/bash

# Jarvis Environment Installer - Linux/macOS (Bash)
# This script synchronizes the Jarvis AI Engineering environment into your local .claude directory.

set -e

# --- Helper Functions ---
write_log() {
    local level=$1
    local message=$2
    local color=""

    case $level in
        "INFO")    color="\033[0;36m" ;; # Cyan
        "SUCCESS") color="\033[0;32m" ;; # Green
        "WARN")    color="\033[0;33m" ;; # Yellow
        "ERROR")   color="\033[0;31m" ;; # Red
    esac

    echo -e "${color}[$level] $(date +'%H:%M:%S') - $message\033[0m"
}

write_log "INFO" "Starting Jarvis Environment Synchronization..."

# 1. Setup Paths
HOME_DIR="$HOME"
CLAUDE_DIR="$HOME_DIR/.claude"
REPO_ROOT="$(pwd)"

write_log "INFO" "Target Directory: $CLAUDE_DIR"

# 2. Create Essential Directories
DIRS=("skills" "commands" "design-systems" "scripts" "cerebro/sessions")
for dir in "${DIRS[@]}"; do
    mkdir -p "$CLAUDE_DIR/$dir"
    write_log "SUCCESS" "Ensured directory: $dir"
done

# 3. Sync Functional Assets
# Sync directories
cp -r "$REPO_ROOT/skills/." "$CLAUDE_DIR/skills/"
cp -r "$REPO_ROOT/commands/." "$CLAUDE_DIR/commands/"
cp -r "$REPO_ROOT/design-systems/." "$CLAUDE_DIR/design-systems/"

# Sync specific files
cp "$REPO_ROOT/model_router.py" "$CLAUDE_DIR/scripts/model_router.py"

write_log "SUCCESS" "Synced functional assets (Skills, Commands, Design-Systems, Model Router)"

# 4. Inject Configuration Templates
declare -A CONFIGS=(
    ["config/settings.json.tpl"]="settings.json"
    ["config/settings.local.json.tpl"]="settings.local.json"
)

for src_rel in "${!CONFIGS[@]}"; do
    dest_file=${CONFIGS[$src_rel]}
    src_path="$REPO_ROOT/$src_rel"
    dest_path="$CLAUDE_DIR/$dest_file"

    # Backup existing config
    if [ -f "$dest_path" ]; then
        mv "$dest_path" "$dest_path.bak"
        write_log "WARN" "Backed up existing $dest_file"
    fi

    # Replace {{HOME}} and write to destination
    sed "s|{{HOME}}|$HOME_DIR|g" "$src_path" > "$dest_path"
    write_log "SUCCESS" "Injected Config: $dest_file"
done

# 5. Bootstrap Cerebro Memory
CEREBRO_INDEX="$CLAUDE_DIR/cerebro/index.md"
if [ ! -f "$CEREBRO_INDEX" ]; then
    cp "$REPO_ROOT/memory/index_template.md" "$CEREBRO_INDEX"
    write_log "SUCCESS" "Initialized Cerebro Index"
fi

CEREBRO_SCHEMA="$CLAUDE_DIR/cerebro/CLAUDE.md"
if [ ! -f "$CEREBRO_SCHEMA" ]; then
    cp "$REPO_ROOT/memory/cerebro_protocol.md" "$CEREBRO_SCHEMA"
    write_log "SUCCESS" "Injected Cerebro Protocol"
fi

write_log "SUCCESS" "JARVIS ENVIRONMENT SYNC COMPLETE!"
echo -e "\n\033[0;36mRestart Claude Code to apply changes.\033[0m\n"
