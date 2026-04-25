# FinanceKids

Aplicacion web educativa construida con Django para aprendizaje financiero infantil.

## Stack
- Python 3.11+
- Django 5
- SQLite (por defecto para desarrollo)
- MySQL (opcional / produccion)
- GitHub Actions para CI

## Estructura base
- `financekids/`: configuracion del proyecto Django
- `core/`: vistas, templates y logica principal
- `game/`: modelos de dominio (temas y perfil)
- `scripts/`: utilidades operativas locales

## Requisitos
- Python instalado
- Git instalado
- MySQL solo si deseas usarlo localmente

## Inicio rapido (local)
1. Clonar repositorio.
2. Crear virtualenv:
	- `python -m venv .venv`
3. Activar virtualenv:
	- PowerShell: `.venv\\Scripts\\Activate.ps1`
	- Bash: `source .venv/bin/activate`
4. Instalar dependencias:
	- `pip install -r requirements.txt`
5. Crear `.env` a partir de `.env.example`.
6. Ejecutar migraciones:
	- `python manage.py migrate`
7. Ejecutar tests:
	- `python manage.py test`
8. Levantar servidor:
	- `python manage.py runserver`

App: `http://127.0.0.1:8000/`
Admin: `http://127.0.0.1:8000/admin/`

## Configuracion de entorno
Usa `.env.example` como plantilla.

### Modo recomendado para empezar (sin errores)
- No configures variables de MySQL.
- El proyecto usara SQLite automaticamente y funcionara al clonar.

### Usar MySQL (opcional)
- Define `DB_ENGINE=mysql`.
- Configura `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

## Trabajo en equipo
Consulta `CONTRIBUTING.md` para flujo de ramas y checklist de PR.

Flujo sugerido:
1. Crear rama desde `develop`: `feat/<nombre>` o `fix/<nombre>`
2. Commits pequenos y descriptivos
3. Abrir Pull Request hacia `develop`
4. Esperar CI en verde y review
5. Merge

## CI (GitHub Actions)
Archivo: `.github/workflows/ci.yml`

El pipeline ejecuta:
1. Instalacion de dependencias
2. Migraciones
3. Tests de Django

## Base de datos y sincronizacion
Si trabajas con MySQL y esquema unificado:
- `python manage.py unify_mysql_schema`

## Buenas practicas
- No subir secretos (`.env` ya esta ignorado).
- Versionar cambios de esquema con migraciones Django.
- Validar backup antes de cambios destructivos.
