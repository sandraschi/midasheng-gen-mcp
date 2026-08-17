# scripts/verify-model.ps1 - model availability checks for CI/dev
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "No venv yet; run start.ps1 or 'uv sync --extra model' first." -ForegroundColor Yellow
    exit 2
}

& $VenvPython -c "from huggingface_hub import hf_hub_download; hf_hub_download('mispeech/midashenglm-gen', 'config.json', local_files_only=True)" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "MODEL_MISSING" -ForegroundColor Red
    exit 1
}
Write-Host "MODEL_PRESENT" -ForegroundColor Green
exit 0
