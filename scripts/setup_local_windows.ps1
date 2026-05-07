$ErrorActionPreference = 'Stop'

Write-Host '== FinanceKids | Setup local (Windows) ==' -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error 'Python no esta disponible en PATH. Instala Python 3.11+ y vuelve a ejecutar este script.'
}

$pythonExe = 'python'
$venvPython = Join-Path '.venv' 'Scripts\python.exe'

if (-not (Test-Path '.venv')) {
    Write-Host 'Creando entorno virtual .venv...' -ForegroundColor Yellow
    & $pythonExe -m venv .venv
}

if (-not (Test-Path $venvPython)) {
    Write-Error 'No se encontro .venv\Scripts\python.exe. El entorno virtual no se creo correctamente.'
}

Write-Host 'Instalando dependencias...' -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path '.env')) {
    Write-Host 'Creando .env desde .env.example...' -ForegroundColor Yellow
    Copy-Item '.env.example' '.env'

    # Forzar modo local sencillo para companeros sin MySQL.
    $envText = Get-Content '.env' -Raw
    $envText = $envText -replace '(?m)^USE_SQLITE\s*=\s*.*$', 'USE_SQLITE=True'
    $envText = $envText -replace '(?m)^DEBUG\s*=\s*.*$', 'DEBUG=True'
    Set-Content '.env' $envText -Encoding UTF8
}
else {
    Write-Host '.env ya existe. No se sobrescribe.' -ForegroundColor DarkYellow
}

Write-Host 'Aplicando migraciones...' -ForegroundColor Yellow
& $venvPython manage.py migrate

Write-Host ''
Write-Host 'Setup completado.' -ForegroundColor Green
Write-Host 'Para iniciar la app ejecuta:' -ForegroundColor Green
Write-Host '  powershell -ExecutionPolicy Bypass -File .\scripts\start_local_windows.ps1' -ForegroundColor White
