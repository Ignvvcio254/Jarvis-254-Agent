<#
.SYNOPSIS
  verify-gate.ps1 — Veredicto OBJETIVO de completitud de tarea.
  Núcleo del harness Jarvis-UPLIFT (F1). Porta el patrón anti-gaming de evolve-loop.

.DESCRIPTION
  Una tarea no está hecha porque el modelo lo diga, sino porque los checks pasan.
  Auto-detecta el tipo de proyecto, corre los checks aplicables (build/parse,
  typecheck, lint, test, behavior), y escribe .verify/verdict.json ligado a un
  stateHash (sha256 del estado del árbol). Exit 0 solo si TODO lo aplicable pasa.

.PARAMETER Path
  Directorio del proyecto a verificar. Default: directorio actual.

.PARAMETER Verifier
  Comando verificador específico de caso (ej. "node verify.js"). Opcional.

.PARAMETER MustContain
  Patrón que DEBE existir en -File (behavior check positivo). Opcional.

.PARAMETER MustNotContain
  Patrón que NO debe existir en -File (behavior check negativo). Opcional.

.PARAMETER File
  Archivo objetivo para -MustContain / -MustNotContain.

.EXAMPLE
  pwsh verify-gate.ps1 -Path .
  pwsh verify-gate.ps1 -Path . -Verifier "node verify.js"
  pwsh verify-gate.ps1 -Path . -MustContain "dayPhase" -File "zombieswar.html"

.OUTPUTS
  Exit 0 = pass (+ .verify/verdict.json).  Exit 1 = fail.  Exit 2 = error de setup.
#>
param(
  [string]$Path = ".",
  [string]$Verifier = "",
  [string]$MustContain = "",
  [string]$MustNotContain = "",
  [string]$File = ""
)

$ErrorActionPreference = "Continue"
$root = Resolve-Path $Path -ErrorAction SilentlyContinue
if (-not $root) { Write-Host "[gate] ruta no existe: $Path" -ForegroundColor Red; exit 2 }
Set-Location $root

$checks = @()          # cada check: @{ name; status; detail }
function Add-Check($name, $ok, $detail) {
  $script:checks += [pscustomobject]@{ name = $name; status = $(if ($ok) {"pass"} else {"fail"}); detail = $detail }
  $color = if ($ok) { "Green" } else { "Red" }
  $mark  = if ($ok) { "OK  " } else { "FAIL" }
  Write-Host ("  [{0}] {1} {2}" -f $mark, $name, $detail) -ForegroundColor $color
}
function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Write-Host ">>> verify-gate :: $root" -ForegroundColor Cyan

# ── Detección de tipo de proyecto ───────────────────────────────────────────
$hasNode   = Test-Path (Join-Path $root "package.json")
$hasPy     = (Test-Path (Join-Path $root "requirements.txt")) -or (Test-Path (Join-Path $root "pyproject.toml")) -or @(Get-ChildItem $root -Filter *.py -ErrorAction SilentlyContinue).Count -gt 0
$htmlFiles = @(Get-ChildItem $root -Filter *.html -ErrorAction SilentlyContinue)
$jsFiles   = @(Get-ChildItem $root -Filter *.js -ErrorAction SilentlyContinue)

# ── 1. BUILD / PARSE ────────────────────────────────────────────────────────
if ($hasNode) {
  $pkg = Get-Content (Join-Path $root "package.json") -Raw | ConvertFrom-Json
  if ($pkg.scripts -and $pkg.scripts.build) {
    $o = & npm run build 2>&1 | Out-String
    Add-Check "build" ($LASTEXITCODE -eq 0) "npm run build"
  }
}
# Parse de JS sueltos (sintaxis válida) via node --check
if ($jsFiles.Count -gt 0 -and (Have node)) {
  $bad = @()
  foreach ($f in $jsFiles) { & node --check $f.FullName 2>$null; if ($LASTEXITCODE -ne 0) { $bad += $f.Name } }
  Add-Check "parse-js" ($bad.Count -eq 0) $(if ($bad.Count) {"sintaxis inválida: $($bad -join ', ')"} else {"$($jsFiles.Count) archivos JS OK"})
}
# Parse de HTML embebido: extraer <script> y validar via node (heurística para juegos HTML)
if ($htmlFiles.Count -gt 0 -and (Have node)) {
  $bad = @()
  foreach ($h in $htmlFiles) {
    $content = Get-Content $h.FullName -Raw
    $scripts = [regex]::Matches($content, '(?s)<script[^>]*>(.*?)</script>')
    $i = 0
    foreach ($m in $scripts) {
      $code = $m.Groups[1].Value
      if ($code.Trim().Length -lt 5) { continue }
      if ($code -match 'src\s*=') { continue }
      $tmp = Join-Path $env:TEMP ("vg_{0}_{1}.js" -f $h.BaseName, $i)
      Set-Content $tmp $code -Encoding UTF8
      & node --check $tmp 2>$null
      if ($LASTEXITCODE -ne 0) { $bad += "$($h.Name)#script$i" }
      Remove-Item $tmp -ErrorAction SilentlyContinue
      $i++
    }
  }
  Add-Check "parse-html-js" ($bad.Count -eq 0) $(if ($bad.Count) {"JS embebido inválido: $($bad -join ', ')"} else {"$($htmlFiles.Count) HTML con JS válido"})
}
if ($hasPy -and (Have python)) {
  $pyFiles = @(Get-ChildItem $root -Filter *.py -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch 'node_modules|\.venv|venv|__pycache__' })
  $bad = @()
  foreach ($f in $pyFiles) { & python -m py_compile $f.FullName 2>$null; if ($LASTEXITCODE -ne 0) { $bad += $f.Name } }
  if ($pyFiles.Count -gt 0) { Add-Check "parse-py" ($bad.Count -eq 0) $(if ($bad.Count) {"sintaxis inválida: $($bad -join ', ')"} else {"$($pyFiles.Count) archivos .py OK"}) }
}

# ── 2. TYPECHECK ────────────────────────────────────────────────────────────
if ($hasNode -and (Test-Path (Join-Path $root "tsconfig.json")) -and (Have npx)) {
  $o = & npx tsc --noEmit 2>&1 | Out-String
  Add-Check "typecheck" ($LASTEXITCODE -eq 0) "tsc --noEmit"
}

# ── 3. LINT ─────────────────────────────────────────────────────────────────
if ($hasNode) {
  $pkg = Get-Content (Join-Path $root "package.json") -Raw | ConvertFrom-Json
  if ($pkg.scripts -and $pkg.scripts.lint -and (Have npm)) {
    $o = & npm run lint 2>&1 | Out-String
    Add-Check "lint" ($LASTEXITCODE -eq 0) "npm run lint"
  }
}

# ── 4. TEST ─────────────────────────────────────────────────────────────────
if ($hasNode) {
  $pkg = Get-Content (Join-Path $root "package.json") -Raw | ConvertFrom-Json
  if ($pkg.scripts -and $pkg.scripts.test -and (Have npm)) {
    $o = & npm test 2>&1 | Out-String
    $passed = ($LASTEXITCODE -eq 0) -and ($o -notmatch "no test specified")
    if ($o -notmatch "no test specified") { Add-Check "test" $passed "npm test" }
  }
}
if ($hasPy -and (Have python)) {
  if ((Test-Path (Join-Path $root "tests")) -or @(Get-ChildItem $root -Filter "test_*.py" -ErrorAction SilentlyContinue).Count -gt 0) {
    $o = & python -m pytest -q 2>&1 | Out-String
    Add-Check "test" ($LASTEXITCODE -eq 0) "pytest"
  }
}

# ── 5. VERIFIER específico de caso ──────────────────────────────────────────
if ($Verifier) {
  $o = Invoke-Expression $Verifier 2>&1 | Out-String
  # acepta verificadores que devuelven exit code, o JSON con score
  $ok = $LASTEXITCODE -eq 0
  $score = $null
  try { $score = ($o | ConvertFrom-Json).score } catch {}
  if ($null -ne $score) { $ok = ($score -ge 100) }
  Add-Check "verifier" $ok "$Verifier $(if($null -ne $score){"(score=$score)"})"
}

# ── 6. BEHAVIOR checks (grep de patrón) ─────────────────────────────────────
if ($MustContain -and $File) {
  $fp = Join-Path $root $File
  $found = (Test-Path $fp) -and (Select-String -Path $fp -Pattern $MustContain -Quiet -SimpleMatch)
  Add-Check "must-contain" $found "'$MustContain' en $File"
}
if ($MustNotContain -and $File) {
  $fp = Join-Path $root $File
  $absent = (-not (Test-Path $fp)) -or (-not (Select-String -Path $fp -Pattern $MustNotContain -Quiet -SimpleMatch))
  Add-Check "must-not-contain" $absent "'$MustNotContain' ausente de $File"
}

# ── stateHash: sha256 del estado del árbol (anti-gaming) ─────────────────────
function Get-StateHash($dir) {
  $files = Get-ChildItem $dir -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch 'node_modules|\.git|\.verify|__pycache__|\.venv|\.swarm|\.hive-mind|\.index$|\.db$|\.lock$' } |
    Sort-Object FullName
  $sb = New-Object System.Text.StringBuilder
  foreach ($f in $files) {
    try { $h = (Get-FileHash $f.FullName -Algorithm SHA256 -ErrorAction Stop).Hash } catch { $h = "locked" }
    [void]$sb.Append("$($f.FullName.Substring($dir.Path.Length)):$h;")
  }
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($sb.ToString())
  $sha = [System.Security.Cryptography.SHA256]::Create()
  return ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-','').ToLower()
}

# ── Veredicto ───────────────────────────────────────────────────────────────
$failed   = @($checks | Where-Object { $_.status -eq "fail" })
$verdict  = if ($checks.Count -eq 0) { "no-checks" } elseif ($failed.Count -eq 0) { "pass" } else { "fail" }
$stateHash = Get-StateHash $root

$verifyDir = Join-Path $root ".verify"
New-Item -ItemType Directory -Force $verifyDir | Out-Null
$result = [ordered]@{
  verdict   = $verdict
  stateHash = $stateHash
  timestamp = (Get-Date -Format "o")
  checks    = $checks
  note      = "Veredicto objetivo. El modelo no puede escribir este archivo a mano."
}
$result | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $verifyDir "verdict.json") -Encoding UTF8

Write-Host ""
if ($verdict -eq "pass") {
  Write-Host "=== VEREDICTO: PASS ($($checks.Count) checks) ===" -ForegroundColor Green
  exit 0
} elseif ($verdict -eq "no-checks") {
  Write-Host "=== VEREDICTO: SIN CHECKS APLICABLES — no se puede atestar ===" -ForegroundColor Yellow
  Write-Host "    Especifique -Verifier o -MustContain para una tarea sin build/test." -ForegroundColor Yellow
  exit 1
} else {
  Write-Host "=== VEREDICTO: FAIL ($($failed.Count)/$($checks.Count) checks) ===" -ForegroundColor Red
  Write-Host "    Fallaron: $(($failed | ForEach-Object { $_.name }) -join ', ')" -ForegroundColor Red
  exit 1
}