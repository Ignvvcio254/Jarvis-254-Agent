# Voice notification when a multi-CLI workspace task finishes.
# Fallback chain: edge_tts (neural) -> ffplay; if that fails -> native SAPI -> beep.
# Voice: $env:JARVIS_TTS_VOICE (default en-US-GuyNeural; e.g. es-MX-JorgeNeural).
param([string]$msg = "Task completed.")
$voice = if ($env:JARVIS_TTS_VOICE) { $env:JARVIS_TTS_VOICE } else { "en-US-GuyNeural" }
$mp3 = Join-Path ([IO.Path]::GetTempPath()) "jarvis_workspace_tts.mp3"
$ok = $false
try {
  python -m edge_tts --voice $voice --text $msg --write-media $mp3 2>$null
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
