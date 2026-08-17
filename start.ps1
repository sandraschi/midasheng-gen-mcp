# start.ps1 - MiDashengLM-Gen MCP full stack launcher
# Naked-PC safe: installs uv + Node + bun via winget on demand.
param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser,
    [switch]$SkipModelCheck
)
$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $PSCommandPath
$BackendPort = 11159
$FrontendPort = 11160

$Host.UI.RawUI.WindowTitle = "midasheng-gen-mcp - backend :$BackendPort / frontend :$FrontendPort"
if (-not $Headless) {
    Write-Host ""
    Write-Host "  MiDashengLM-Gen MCP" -ForegroundColor Cyan
    Write-Host "  BACKEND   http://127.0.0.1:$BackendPort   (REST /api + MCP /mcp)" -ForegroundColor Gray
    Write-Host "  FRONTEND  http://127.0.0.1:$FrontendPort  (webapp UI)" -ForegroundColor Gray
    Write-Host ""
}

# ---- Require-Command: winget installs for naked PCs ----
function Require-Command {
    param([string]$Name, [string]$WingetId, [string]$Hint)
    if (Get-Command $Name -ErrorAction SilentlyContinue) { return }
    Write-Host "  Installing $Name (required)..." -ForegroundColor Yellow
    winget install --id $WingetId -e --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install $Name automatically. $Hint"
    }
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

Require-Command -Name "uv" -WingetId "astral-sh.uv" -Hint "Install uv from https://docs.astral.sh/uv/"
Require-Command -Name "node" -WingetId "OpenJS.NodeJS" -Hint "Install Node.js from https://nodejs.org/"
Require-Command -Name "bun" -WingetId "Oven-sh.Bun" -Hint "Install bun from https://bun.sh/"

# ---- Local tool guards ----
$ViteBin = Join-Path $ScriptRoot "webapp\node_modules\.bin\vite.cmd"
if (-not (Test-Path $ViteBin) -and (Test-Path (Join-Path $ScriptRoot "webapp\package.json"))) {
    Write-Host "-> Installing webapp dependencies (bun install)..." -ForegroundColor Yellow
    Push-Location (Join-Path $ScriptRoot "webapp")
    bun install
    Pop-Location
}

# ---- Import smoke test ----
$VenvPython = Join-Path $ScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "-> Creating virtualenv + installing dependencies..." -ForegroundColor Yellow
    uv sync --extra model --extra dev
}

# ---- Model download gate (onboarding) ----
if (-not $SkipModelCheck) {
    $torchOk = & $VenvPython -c "import torch; print('ok')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "-> Installing the inference stack (torch + transformers, ~3 GB)..." -ForegroundColor Yellow
        uv sync --extra model --extra dev
    }
    $modelOk = & $VenvPython -c "from huggingface_hub import hf_hub_download; hf_hub_download('mispeech/midashenglm-gen', 'config.json', local_files_only=True)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  The MiDashengLM-Gen checkpoint (~6 GB) is not downloaded yet." -ForegroundColor DarkYellow
        if (-not $Headless) {
            $choice = Read-Host "  Download now from Hugging Face? [y/N]"
            if ($choice -match "^[yY]") {
                Write-Host "-> Downloading model (first run only)..." -ForegroundColor Yellow
                uv run python -c "from huggingface_hub import snapshot_download; print('Downloaded to', snapshot_download('mispeech/midashenglm-gen'))"
            } else {
                Write-Host "  Skipping download. The webapp will show a model-missing state; use Settings > Download Model later." -ForegroundColor Gray
            }
        } else {
            Write-Host "  Headless mode: skipping model download (use: just model-download)" -ForegroundColor Gray
        }
    }
}

# ---- Port zombie clearing ----
foreach ($Port in @($BackendPort, $FrontendPort)) {
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

# ---- Start backend ----
Write-Host "-> Starting backend on :$BackendPort ..." -ForegroundColor Yellow
$BackendJob = Start-Job -Name "midasheng-backend" -ScriptBlock {
    param($Root, $Port)
    Set-Location $Root
    $env:MIDASHENG_BACKEND_PORT = "$Port"
    uv run python -m midasheng_gen_mcp --mode http --host 127.0.0.1 --port $Port
} -ArgumentList $ScriptRoot, $BackendPort

# Readiness poll
$BackendReady = $false
for ($i = 0; $i -lt 90; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $BackendReady = $true; break }
    } catch { }
    Start-Sleep 1
}
if (-not $BackendReady) {
    Write-Host "!! Backend did not become healthy on :$BackendPort within 90s." -ForegroundColor Red
    Receive-Job $BackendJob
    Write-Host "Fix the startup error, then re-run start.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "   Backend healthy: http://127.0.0.1:$BackendPort/api/health" -ForegroundColor Green

if ($BackendOnly) {
    Write-Host "Backend-only mode. Ctrl+C to stop." -ForegroundColor Cyan
    while ($true) { Start-Sleep 10 }
}

# ---- Start frontend ----
Write-Host "-> Starting frontend on :$FrontendPort ..." -ForegroundColor Yellow
$WebRoot = Join-Path $ScriptRoot "webapp"
Start-Process -NoNewWindow -FilePath "bun" -ArgumentList "run dev --port $FrontendPort --host" -WorkingDirectory $WebRoot

$FrontReady = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$FrontendPort" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($r.StatusCode -eq 200) { $FrontReady = $true; break }
    } catch { }
    Start-Sleep 1
}
if (-not $FrontReady) {
    Write-Host "!! Frontend did not come up on :$FrontendPort within 60s." -ForegroundColor Red
    exit 1
}
Write-Host "   Frontend ready: http://127.0.0.1:$FrontendPort" -ForegroundColor Green

# ---- Open browser ----
if (-not $Headless -and -not $NoBrowser) {
    Start-Process "http://127.0.0.1:$FrontendPort"
}

# ---- Keep alive ----
Write-Host ""
Write-Host "  midasheng-gen-mcp is running. Ctrl+C to stop everything." -ForegroundColor Cyan
while ($true) {
    if ($BackendJob.State -eq "Completed" -or $BackendJob.State -eq "Failed") {
        Write-Host "Backend exited. Stopping." -ForegroundColor Red
        Receive-Job $BackendJob
        break
    }
    Start-Sleep 2
}
