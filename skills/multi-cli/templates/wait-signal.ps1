# Generic signal monitor for the multi-CLI workspace.
# Usage: pwsh wait-signal.ps1 -Files "ws\logs\T-1.done","ws\logs\T-2.done" [-Minutes 9] [-TtsMsg "..."]
# Launch in the background; when it returns it prints the content of each signal.
param(
  [Parameter(Mandatory)] [string[]]$Files,
  [double]$Minutes = 9,
  [string]$TtsMsg = ''
)
$deadline = (Get-Date).AddMinutes($Minutes)
while ((Get-Date) -lt $deadline) {
  if (($Files | Where-Object { -not (Test-Path $_) }).Count -eq 0) { break }
  Start-Sleep 8
}
foreach ($f in $Files) {
  if (Test-Path $f) { "$(Split-Path $f -Leaf): $(Get-Content $f -Raw)" } else { "$(Split-Path $f -Leaf): TIMEOUT, no signal" }
}
if ($TtsMsg) {
  $tts = Join-Path (Split-Path $PSScriptRoot) 'notify-tts.ps1'
  if (Test-Path $tts) { pwsh -File $tts -msg $TtsMsg }
}
