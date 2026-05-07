$ErrorActionPreference = 'Stop'

Write-Host '== FinanceKids | Start local (Windows) ==' -ForegroundColor Cyan

$venvPython = Join-Path '.venv' 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    Write-Error 'No existe .venv. Ejecuta primero scripts\setup_local_windows.ps1'
}

if (-not (Test-Path '.env')) {
    Write-Host 'No existe .env. Se intentara continuar con valores por defecto.' -ForegroundColor DarkYellow
}

Write-Host 'Iniciando servidor en http://127.0.0.1:8000 ...' -ForegroundColor Green
& $venvPython manage.py runserver 0.0.0.0:8000
