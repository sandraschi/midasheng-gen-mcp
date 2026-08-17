# mcpb-pack.ps1 - fresh-stage MCPB bundle (MCPB_PACKAGING_STANDARDS.md)
# 1. Wipe + recopy src/ -> mcpb/src/ (never stale twins)
# 2. Verify 3-4-100 prompts
# 3. mcpb pack
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Pkg = "midasheng_gen_mcp"
$Stage = Join-Path $Root "mcpb\src\$Pkg"
$RepoRoot = $Root

Write-Host "=== midasheng-gen-mcp MCPB pack ===" -ForegroundColor Cyan

# 1. Fresh stage (wipe + recopy, preserve package dir)
if (Test-Path (Join-Path $Root "mcpb\src")) {
    Remove-Item -Recurse -Force (Join-Path $Root "mcpb\src")
}
New-Item -ItemType Directory -Force -Path (Split-Path $Stage) | Out-Null
Copy-Item -Recurse -Force (Join-Path $Root "src\$Pkg") $Stage
Write-Host "  Staged $Stage" -ForegroundColor Green

# 2. Verify 3-4-100 prompts (word counts + examples)
function Word-Count([string]$Path) {
    (@(Get-Content -Raw $Path) -split '\s+' | Where-Object { $_ }).Count
}
$sys = Word-Count (Join-Path $Root "assets\prompts\system.md")
$user = Word-Count (Join-Path $Root "assets\prompts\user.md")
$ex = (Get-Content (Join-Path $Root "assets\prompts\examples.json") -Raw | ConvertFrom-Json).Count
Write-Host "  prompts: system=$sys user=$user examples=$ex (need 3000 / 4000 / 100)" -ForegroundColor Yellow
if ($sys -lt 3000 -or $user -lt 4000 -or $ex -lt 100) {
    throw "3-4-100 FAIL: system=$sys user=$user examples=$ex"
}
Write-Host "  3-4-100 verified" -ForegroundColor Green

# 3. No pollution check
$pollution = Get-ChildItem -Path (Join-Path $Root "mcpb") -Recurse -Include "*.pyc", "*.bak", "*.bak.*" -ErrorAction SilentlyContinue
if ($pollution) {
    throw "Pollution under mcpb/: $($pollution.Count) files"
}

# 4. Pack (bunx mcpb; Node fallback)
Push-Location $Root
$mcpb = "bunx.cmd"
if (-not (Get-Command $mcpb -ErrorAction SilentlyContinue)) { $mcpb = "npx.cmd" }
New-Item -ItemType Directory -Force -Path (Join-Path $Root "dist") | Out-Null
& $mcpb @anthropic-ai/mcpb pack . "dist\midasheng-gen-mcp-v0.1.0.mcpb"
if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed with exit code $LASTEXITCODE" }
Pop-Location

# 5. Cleanup stage so the next run cannot reuse it
Remove-Item -Recurse -Force (Join-Path $Root "mcpb\src")
Write-Host "=== Pack complete: dist\midasheng-gen-mcp-v0.1.0.mcpb ===" -ForegroundColor Green
