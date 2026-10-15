# Claude Code con TODOS los modelos en el mismo selector /model:
#   los 5 Claude de siempre (suscripción, sin tocar) + los de otros proveedores vía el gateway local.
# Uso:  claude-multi.ps1 [argumentos de claude]      (también lo abre `claude-multi.cmd`)
#
# Garantías (nada de esto puede dejarle sin Claude):
#   · Si el gateway no arranca o NO es el nuestro, se ejecuta Claude normal y se avisa.
#   · CLAUDE_PLAIN=1 salta el gateway por completo.
#   · El gateway se levanta solo si hace falta y se apaga solo tras 10 min sin uso.
# Seguridad (auditoría 2026-10-03):
#   · Token de sesión en %LOCALAPPDATA%\claude-gateway\token (solo el usuario); Claude lo manda como cabecera
#     x-gateway-token y el proxy exige ese token en las rutas que gastan llaves. Una página web no lo conoce.
#   · Antes de mandar nada, se verifica que quien responde en el puerto es ESTE proxy (prueba HMAC del token):
#     si otro proceso ocupó el puerto, jamás recibe su credencial de Claude.
#   · El proxy recibe un entorno MÍNIMO (solo PATH/rutas del sistema + sus llaves), no el entorno completo.
$claudeReal = Join-Path $env:APPDATA "npm\claude.cmd"          # el binario real, no la función `claude`
$puerto = if ($env:MODELO_PROXY_PORT) { $env:MODELO_PROXY_PORT } else { 8787 }
$base = "http://127.0.0.1:$puerto"
$perfil = Join-Path $env:USERPROFILE ".claude\profiles\multi.settings.json"
$proxy = Join-Path $env:USERPROFILE ".claude\scripts\modelo-proxy.mjs"
$dirToken = Join-Path $env:LOCALAPPDATA "claude-gateway"
$archivoToken = Join-Path $dirToken "token"

function Ejecutar-Normal { & $claudeReal @args; exit $LASTEXITCODE }

function Obtener-Token {
  if (-not (Test-Path $archivoToken)) {
    New-Item -ItemType Directory -Force $dirToken | Out-Null
    $bytes = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    Set-Content -Path $archivoToken -Value (($bytes | ForEach-Object { $_.ToString("x2") }) -join "") -NoNewline
    icacls $dirToken /inheritance:r /grant:r "$($env:USERNAME):(OI)(CI)F" 2>&1 | Out-Null   # solo este usuario
  }
  (Get-Content $archivoToken -Raw).Trim()
}

function Test-Proxy($token) {
  # El proxy demuestra que conoce el token firmando un nonce nuestro (HMAC-SHA256). Un impostor no puede.
  try {
    $nonce = [guid]::NewGuid().ToString("N")
    $r = Invoke-RestMethod "$base/__proxy_health?n=$nonce" -TimeoutSec 2
    $hmac = New-Object Security.Cryptography.HMACSHA256 (, [Text.Encoding]::UTF8.GetBytes($token))
    $esperado = ($hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($nonce)) | ForEach-Object { $_.ToString("x2") }) -join ""
    return ($r.ok -eq $true -and $r.proof -eq $esperado)
  } catch { return $false }
}

if ($env:CLAUDE_PLAIN -eq "1") { Ejecutar-Normal @args }
if (-not (Test-Path $perfil) -or -not (Test-Path $proxy)) { Write-Warning "Gateway no instalado; abriendo Claude normal."; Ejecutar-Normal @args }
$nodeExe = (Get-Command node -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1).Source
if (-not $nodeExe) { Write-Warning "No encontré node; abriendo Claude normal."; Ejecutar-Normal @args }
$token = Obtener-Token

if (-not (Test-Proxy $token)) {
  # Las llaves de TODOS los proveedores viven solo en el entorno del proceso del proxy
  # (no en disco, no en argumentos). Salen del entorno o de .env.local, y solo estas variables.
  $nombres = 'OPENROUTER_API_KEY', 'NVIDIA_API_KEY', 'NVIDIA_BASE_URL', 'GEMINI_API_KEY', 'ZAI_API_KEY', 'XAI_API_KEY', 'GROQ_API_KEY', 'MISTRAL_API_KEY', 'CEREBRAS_API_KEY'
  $valores = @{}
  $envFile = $(if ($env:JARVIS_ENV_FILE) { $env:JARVIS_ENV_FILE } else { Join-Path $env:USERPROFILE ".claude\.env" })
  foreach ($n in $nombres) {
    $v = [Environment]::GetEnvironmentVariable($n)
    if (-not $v -and (Test-Path $envFile)) {
      $l = Select-String -Path $envFile -Pattern "^\s*$n\s*=" | Select-Object -First 1
      if ($l) { $v = ($l.Line -split '=', 2)[1].Trim().Trim('"').Trim("'") }
    }
    if ($v) { $valores[$n] = $v }
  }
  try {
    $psi = New-Object Diagnostics.ProcessStartInfo
    $psi.FileName = $nodeExe
    $psi.Arguments = "`"$proxy`""
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.EnvironmentVariables.Clear()                      # entorno MÍNIMO: nada de heredar todo lo del padre
    foreach ($k in 'PATH', 'SystemRoot', 'TEMP', 'TMP', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA', 'HOMEDRIVE', 'HOMEPATH') {
      $val = [Environment]::GetEnvironmentVariable($k); if ($val) { $psi.EnvironmentVariables[$k] = $val }
    }
    foreach ($kv in $valores.GetEnumerator()) { $psi.EnvironmentVariables[$kv.Key] = $kv.Value }
    $psi.EnvironmentVariables["MODELO_PROXY_PORT"] = "$puerto"
    $psi.EnvironmentVariables["MODELO_PROXY_TOKEN"] = $token
    [void][Diagnostics.Process]::Start($psi)
    for ($i = 0; $i -lt 24 -and -not (Test-Proxy $token); $i++) { Start-Sleep -Milliseconds 250 }
  } catch { }
  if (-not (Test-Proxy $token)) {
    Write-Warning "El gateway no arrancó (o el puerto $puerto lo ocupa otro proceso); abro Claude normal (sin los modelos extra)."
    Ejecutar-Normal @args
  }
  if ($valores.Count -eq 0) { Write-Warning "No encontré llaves de proveedores: los Claude funcionan; los demás darán error." }
}

# Solo la base URL y la cabecera de sesión cambian. NO se define ANTHROPIC_AUTH_TOKEN: el login de suscripción sigue mandando.
$env:ANTHROPIC_BASE_URL = $base
$env:ANTHROPIC_CUSTOM_HEADERS = "x-gateway-token: $token"
try { & $claudeReal --settings $perfil @args; $codigo = $LASTEXITCODE }
finally { Remove-Item Env:ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue; Remove-Item Env:ANTHROPIC_CUSTOM_HEADERS -ErrorAction SilentlyContinue }
exit $codigo
