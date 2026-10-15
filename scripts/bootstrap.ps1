# One-line install (Windows PowerShell 7):
#   irm https://raw.githubusercontent.com/Ignvvcio254/Jarvis-254-Agent/main/scripts/bootstrap.ps1 | iex
# Clones (or updates) the repo into $env:JARVIS_HOME (default ~\.jarvis-254) and runs the merging installer.
$ErrorActionPreference = "Stop"
$repo = if ($env:JARVIS_REPO) { $env:JARVIS_REPO } else { "https://github.com/Ignvvcio254/Jarvis-254-Agent.git" }
$dest = if ($env:JARVIS_HOME) { $env:JARVIS_HOME } else { Join-Path $HOME ".jarvis-254" }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "git is required" }
$py = @("python", "py", "python3") | Where-Object { (Get-Command $_ -ErrorAction SilentlyContinue) -and ((& $_ -c "import sys; print(sys.version_info >= (3, 8))" 2>$null) -eq "True") } | Select-Object -First 1
if (-not $py) { throw "Python 3.8+ is required" }
if (Test-Path (Join-Path $dest ".git")) { git -C $dest pull --ff-only --quiet } else { git clone --depth 1 --quiet $repo $dest }
& $py (Join-Path $dest "install.py") @args
& $py (Join-Path $dest "jarvis_doctor.py")
Write-Host "Jarvis-254 installed. Open Claude Code in any project; update later by re-running this command."
