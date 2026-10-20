$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$python = 'C:\Users\SARANYA\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = (Get-Command python -ErrorAction Stop).Source }
& $python (Join-Path $PSScriptRoot 'ollama_workflow.py')
