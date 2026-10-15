# Multi-CLI runner template. Replace: T-XXX, CLI-COMMAND, GOAL, TARGET-FILE (if it edits), EXTRA-CHECKS.
$ws = $PSScriptRoot
Set-Location (Split-Path $ws)   # project root
$task = Get-Content "$ws\tasks\T-XXX.md" -Raw
# --- only if the task EDITS a file: snapshot + backup ---
$pre = (Get-Item .\TARGET-FILE -ErrorAction SilentlyContinue).Length
if (Test-Path .\TARGET-FILE) { Copy-Item .\TARGET-FILE "$ws\backup-T-XXX" -Force }
Write-Host "=== T-XXX · CLI · GOAL · $(Get-Date -Format HH:mm:ss) ===" -ForegroundColor Cyan
# AGY:      agy -p $task --print-timeout 30m 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
# OpenCode: opencode run [-m model] $task 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
# Codex:    codex exec $task 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
CLI-COMMAND $task 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
$post = (Get-Item .\TARGET-FILE -ErrorAction SilentlyContinue).Length
"exit=$LASTEXITCODE end=$(Get-Date -Format HH:mm:ss) size_pre=$pre size_post=$post edited=$($post -ne $pre) EXTRA-CHECKS" | Set-Content "$ws\logs\T-XXX.done"
pwsh -File "$ws\notify-tts.ps1" -msg "Task T XXX finished. File edited: $($post -ne $pre)."
Write-Host "=== T-XXX finished (exit $LASTEXITCODE, edited=$($post -ne $pre)) ===" -ForegroundColor Green
