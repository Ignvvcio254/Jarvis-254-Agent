param(
    [switch]$Reclone
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$upstreamRoot = Join-Path $repoRoot "upstream"
$hermesPath = Join-Path $upstreamRoot "hermes-agent"
$hermesUrl = "https://github.com/NousResearch/hermes-agent.git"

if (-not (Test-Path -LiteralPath $upstreamRoot)) {
    New-Item -ItemType Directory -Path $upstreamRoot -Force | Out-Null
}

if ($Reclone -and (Test-Path -LiteralPath $hermesPath)) {
    Remove-Item -LiteralPath $hermesPath -Recurse -Force
}

if (-not (Test-Path -LiteralPath $hermesPath)) {
    git clone --depth 1 $hermesUrl $hermesPath
    exit $LASTEXITCODE
}

git -C $hermesPath fetch --depth 1 origin main
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

git -C $hermesPath reset --hard origin/main
exit $LASTEXITCODE
