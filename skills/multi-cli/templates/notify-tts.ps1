# Notificación por voz al terminar tareas del workspace multi-CLI.
# Cadena de fallback según CLAUDE.md: edge_tts (neural) -> ffplay; si falla -> SAPI nativo -> beep.
param([string]$msg = "Tarea completada.")
$mp3 = Join-Path $env:TEMP "jarvis_workspace_tts.mp3"
$ok = $false
try {
  python -m edge_tts --voice "es-MX-JorgeNeural" --text $msg --write-media $mp3 2>$null
  if ((Test-Path $mp3) -and (Get-Item $mp3).Length -gt 0) {
    ffplay -nodisp -autoexit $mp3 -loglevel quiet 2>$null
    if ($LASTEXITCODE -eq 0) { $ok = $true }
  }
} catch {}
Remove-Item $mp3 -Force -ErrorAction SilentlyContinue
if (-not $ok) {
  try {
    Add-Type -AssemblyName System.Speech
    $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $s.Rate = 1
    $s.Speak($msg)
  } catch { [console]::beep(880, 400); [console]::beep(1100, 400) }
}
