# Jarvis Framework Installer - Windows (PowerShell)
# This script bootstraps the Jarvis AI Engineering environment into the local .claude directory.

$ErrorActionPreference = "Stop"

function Write-JarvisLog {
    param([string]$Message, [string]$Level = "INFO")
    $colors = @{ "INFO" = "Cyan"; "SUCCESS" = "Green"; "WARN" = "Yellow"; "ERROR" = "Red" }
    Write-Host "[$Level] $(Get-Date -Format 'HH:mm:ss') - $Message" -ForegroundColor $colors[$Level]
}

Write-JarvisLog "Starting Jarvis Framework Installation..." "INFO"

# 1. Environment Detection
$homeDir = $HOME
$claudeDir = Join-Path $homeDir ".claude"
$frameworkRoot = Resolve-Path ".\*" | Select-Object -ExpandProperty Path # Assumes running from framework root

Write-JarvisLog "Detected Home Directory: $homeDir" "INFO"
Write-JarvisLog "Target Claude Directory: $claudeDir" "INFO"

# 2. Create Directory Structure
$requiredDirs = @(
    "scripts",
    "design-systems",
    "cerebro/sessions",
    "cerebro/concepts",
    "cerebro/adr"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $claudeDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-JarvisLog "Created directory: $dir" "SUCCESS"
    }
}

# 3. Inject Core Scripts
$scriptsToCopy = @(
    "core/routing/model_router.py"
)

foreach ($script in $scriptsToCopy) {
    $src = Join-Path "jarvis-framework" $script
    $dest = Join-Path $claudeDir "scripts/model_router.py"
    Copy-Item -Path $src -Destination $dest -Force
    Write-JarvisLog "Injected script: $script" "SUCCESS"
}

# 4. Inject Design Systems
robocopy "jarvis-framework\design-systems" (Join-Path $claudeDir "design-systems") /E /NFL /NDL /NJH /NJS

# 5. Configuration Template Injection
$configs = @{
    "templates/config/settings.json.tpl" = "settings.json"
    "templates/config/settings.local.json.tpl" = "settings.local.json"
}

foreach ($entry in $configs.GetEnumerator()) {
    $srcPath = Join-Path "jarvis-framework" $entry.Key
    $destPath = Join-Path $claudeDir $entry.Value
    
    $content = Get-Content -Path $srcPath -Raw
    $content = $content.Replace("{{HOME}}", $homeDir)
    
    Set-Content -Path $destPath -Value $content -Encoding UTF8
    Write-JarvisLog "Injected and generalized config: $($entry.Value)" "SUCCESS"
}

# 6. Initialize Cerebro Memory
$cerebroIndex = Join-Path $claudeDir "cerebro/index.md"
if (-not (Test-Path $cerebroIndex)) {
    $indexTpl = Get-Content -Path "jarvis-framework\templates\cerebro\index_template.md" -Raw
    Set-Content -Path $cerebroIndex -Value $indexTpl -Encoding UTF8
    Write-JarvisLog "Initialized Cerebro Root Index" "SUCCESS"
}

$cerebroSchema = Join-Path $claudeDir "cerebro/CLAUDE.md"
if (-not (Test-Path $cerebroSchema)) {
    # We use the protocol file as the operating schema for the local instance
    Copy-Item -Path "jarvis-framework\memory\protocols\cerebro_protocol.md" -Destination $cerebroSchema -Force
    Write-JarvisLog "Injected Cerebro Operational Schema" "SUCCESS"
}

# 7. Validation
Write-JarvisLog "Validating installation..." "INFO"
$valid = $true
if (-not (Test-Path (Join-Path $claudeDir "scripts/model_router.py"))) { $valid = $false; Write-JarvisLog "Missing model_router.py" "ERROR" }
if (-not (Test-Path (Join-Path $claudeDir "settings.json"))) { $valid = $false; Write-JarvisLog "Missing settings.json" "ERROR" }

if ($valid) {
    Write-JarvisLog "JARVIS FRAMEWORK INSTALLED SUCCESSFULLY!" "SUCCESS"
    Write-Host "`nRestart Claude Code to apply changes.`n" -ForegroundColor Cyan
} else {
    Write-JarvisLog "Installation failed. Please check the errors above." "ERROR"
    exit 1
}
