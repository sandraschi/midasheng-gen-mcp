$ErrorActionPreference = "Stop"
Set-Location "D:\Dev\repos\midasheng-gen-mcp"
Write-Host "== step 1: uv sync --extra model --extra dev =="
& "C:\Users\sandr\.local\bin\uv.exe" sync --extra model --extra dev
Write-Host "== step 2: snapshot_download =="
& "C:\Users\sandr\.local\bin\uv.exe" run python -c "from huggingface_hub import snapshot_download; print('DOWNLOADED_TO', snapshot_download('mispeech/midashenglm-gen'))"
Write-Host "== DONE =="
