# Plantilla de runner multi-CLI. Reemplazar: T-XXX, <CLI+flags>, <OBJETIVO>, <archivo-objetivo (si edita)>, <checks de entregables>.
$ws = $PSScriptRoot
Set-Location (Split-Path $ws)   # raíz del proyecto
$task = Get-Content "$ws\tasks\T-XXX.md" -Raw
# --- solo si la tarea EDITA un archivo: snapshot + backup ---
$pre = (Get-Item .\ARCHIVO-OBJETIVO -ErrorAction SilentlyContinue).Length
if (Test-Path .\ARCHIVO-OBJETIVO) { Copy-Item .\ARCHIVO-OBJETIVO "$ws\backup-T-XXX" -Force }
Write-Host "=== T-XXX · CLI · OBJETIVO · $(Get-Date -Format HH:mm:ss) ===" -ForegroundColor Cyan
# AGY:      agy -p $task --print-timeout 30m 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
# OpenCode: opencode run [-m modelo] $task 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
CLI-COMANDO $task 2>&1 | Tee-Object "$ws\logs\T-XXX.log"
$post = (Get-Item .\ARCHIVO-OBJETIVO -ErrorAction SilentlyContinue).Length
"exit=$LASTEXITCODE end=$(Get-Date -Format HH:mm:ss) size_pre=$pre size_post=$post edited=$($post -ne $pre) CHECKS-EXTRA" | Set-Content "$ws\logs\T-XXX.done"
pwsh -File "$ws\notify-tts.ps1" -msg "terminó la tarea T XXX. Archivo editado: $($post -ne $pre)."
Write-Host "=== T-XXX terminado (exit $LASTEXITCODE, edited=$($post -ne $pre)) ===" -ForegroundColor Green
