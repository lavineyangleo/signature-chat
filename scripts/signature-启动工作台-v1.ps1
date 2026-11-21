param([int]$Port = 8780)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot 'venv-3.12\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Create venv-3.12 and follow README.md installation steps first.'
}
& $pythonPath -m signature_chat.cli serve --port $Port
