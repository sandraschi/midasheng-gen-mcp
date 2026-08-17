# Generate the 256x256 MCPB icon (assets/icon.png) if missing.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$OutDir = Join-Path $Root "assets"
$OutFile = Join-Path $OutDir "icon.png"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(256, 256)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias

# Dark zinc background with rounded feel
$bg = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 24, 24, 27))
$g.FillRectangle($bg, 0, 0, 256, 256)

# Amber waveform bars (left to right, varying heights)
$bar = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 245, 158, 11))
$heights = @(40, 90, 140, 70, 110, 170, 60, 120, 80, 40)
for ($i = 0; $i -lt $heights.Count; $i++) {
    $x = 40 + $i * 20
    $h = $heights[$i]
    $g.FillRectangle($bar, $x, (128 - $h / 2), 12, $h)
}

# Text
$font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 228, 228, 231))
$g.DrawString("MiDashengLM", $font, $brush, 32, 208)

$bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Host "Icon written: $OutFile" -ForegroundColor Green
