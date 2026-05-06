# Jarvis Environment Installer - Windows (PowerShell)
# This script synchronizes the Jarvis AI Engineering environment into your local .claude directory.

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $colors = @{ "INFO" = "Cyan"; "SUCCESS" = "Green"; "WARN" = "Yellow"; "ERROR" = "Red" }
    Write-Host "[$Level] $(Get-Date -Format 'HH:mm:ss') - $Message" -ForegroundColor $colors[$Level]
}

Write-Log "Starting Jarvis Environment Synchronization..." "INFO"

# 1. Setup Paths
$homeDir = $HOME
$claudeDir = Join-Path $homeDir ".claude"
$repoRoot = Get-Location

Write-Log "Target Directory: $claudeDir" "INFO"

# 2. Create Essential Directories
$dirs = @("skills", "commands", "design-systems", "scripts", "cerebro/sessions")
foreach ($dir in $dirs) {
    $path = Join-Path $claudeDir $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Log "Created: $dir" "SUCCESS"
    }
}

# 3. Sync Functional Assets (Direct Copy)
$syncMap = @{
    "skills"         = "skills"
    "commands"       = "commands"
    "design-systems" = "design-systems"
    "model_router.py" = "scripts/model_router.py"
}

foreach ($entry in $syncMap.GetEnumerator()) {
    $src = Join-Path $repoRoot $entry.Key
    $dest = Join-Path $claudeDir $entry.Value
    
    if ($entry.Key -eq "model_router.py") {
        Copy-Item -Path $src -Destination $dest -Force
    } else {
        # Using robocopy for efficient directory mirroring
        robocopy $src $dest /E /NFL /NDL /NJH /NJS
    }
    Write-Log "Synced: $($entry.Key)" "SUCCESS"
}

# 4. Inject Configuration Templates
$configs = @{
    "config/settings.json.tpl"         = "settings.json"
    "config/settings.local.json.tpl"   = "settings.local.json"
}

foreach ($entry in $configs.GetEnumerator()) {
    $src = Join-Path $repoRoot $entry.Key
    $dest = Join-Path $claudeDir $entry.Value
    
    # Backup existing config
    if (Test-Path $dest) {
        Move-Item -Path $dest -Destination "$dest.bak" -Force
        Write-Log "Backed up existing $($entry.Value)" "WARN"
    }
    
    $content = Get-Content -Path $src -Raw
    $content = $content.Replace("{{HOME}}", $homeDir)
    
    Set-Content -Path $dest -Value $content -Encoding UTF8
    Write-Log "Injected Config: $($entry.Value)" "SUCCESS"
}

# 5. Bootstrap Cerebro Memory
$cerebroIndex = Join-Path $claudeDir "cerebro/index.md"
if (-not (Test-Path $cerebroIndex)) {
    $tpl = Get-Content -Path (Join-Path $repoRoot "memory/index_template.md") -Raw
    Set-Content -Path $cerebroIndex -Value $tpl -Encoding UTF8
    Write-Log "Initialized Cerebro Index" "SUCCESS"
}

$cerebroSchema = Join-Path $claudeDir "cerebro/CLAUDE.md"
if (-not (Test-Path $cerebroSchema)) {
    Copy-Item -Path (Join-Path $repoRoot "memory/cerebro_protocol.md") -Destination $cerebroSchema -Force
    Write-Log "Injected Cerebro Protocol" "SUCCESS"
}

Write-Log "JARVIS ENVIRONMENT SYNC COMPLETE!" "SUCCESS"
Write-Host "`nRestart Claude Code to apply changes.`n" -ForegroundColor Cyan
