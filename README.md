# FinanceKids

Aplicacion web educativa construida con Django para aprendizaje financiero infantil.

## Stack
- Python 3.11+
- Django 5
- PostgreSQL en produccion (Render)
- SQLite en desarrollo local rapido
- MySQL como compatibilidad/fallback
- GitHub Actions para CI

## Estructura base
- `financekids/`: configuracion del proyecto Django
- `core/`: vistas, templates y logica principal
- `game/`: modelos de dominio (temas y perfil)
- `scripts/`: utilidades operativas locales

## Requisitos
- Python instalado
- Git instalado
- MySQL para entorno local y CI

## Onboarding rapido para companeros (Windows)
1. Clonar el repositorio.
2. Abrir PowerShell en la carpeta del proyecto.
3. Ejecutar setup automatico (crea `.venv`, instala dependencias, genera `.env`, activa SQLite y migra):
	- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_local_windows.ps1`
4. Iniciar la app:
	- `powershell -ExecutionPolicy Bypass -File .\scripts\start_local_windows.ps1`

Tambien puedes usar doble click en:
- `scripts\setup_local_windows.bat`
- `scripts\start_local_windows.bat`

URL local: `http://127.0.0.1:8000/`

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

### Notas para desarrollo local sencillo
- El setup automatico deja `USE_SQLITE=True` para evitar instalar MySQL en equipos nuevos.
- Si quieres MySQL local, cambia `USE_SQLITE=False` en `.env` y completa `DB_*`.

## Configuracion de entorno
Usa `.env.example` como plantilla.

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

## Arquitectura de base de datos (Render y local)

Esta app usa una estrategia de conexion flexible definida en `financekids/settings.py`.
No hay una sola base fija para todos los entornos: el motor se elige por variables de entorno.

### Como decide Django a que base conectarse
Orden de prioridad actual:

1. `USE_SQLITE=True`
2. `DATABASE_URL` (PostgreSQL, recomendado en Render)
3. Variables `MYSQL_ADDON_*`
4. Variables `DB_*` (MySQL manual)

Interpretacion practica:
- Si `USE_SQLITE=True`, se ignora todo lo demas y se usa `db.sqlite3` local.
- Si `USE_SQLITE=False` y existe `DATABASE_URL`, se conecta a PostgreSQL.
- Si no existe `DATABASE_URL`, intenta MySQL con `MYSQL_ADDON_*` o `DB_*`.

### Donde esta alojada la base de datos en produccion
En Render, la base de datos esta en un servicio separado de tipo PostgreSQL
(por ejemplo, `financekids-db`).

El servicio web Django (`financekids`) no almacena datos permanentes en su propio disco.
Solo se conecta por red a PostgreSQL usando `DATABASE_URL`.

Por eso, al hacer redeploy:
- el codigo de la app cambia,
- pero los datos de usuarios/progreso permanecen en la base PostgreSQL.

### Variables recomendadas en Render
En el servicio web:
- `DEBUG=False`
- `USE_SQLITE=False`
- `DATABASE_URL=<inyectada por Render al enlazar PostgreSQL>`
- `ALLOWED_HOSTS=.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://tu-servicio.onrender.com`
- `SECRET_KEY=<valor seguro>`

### Detalles de conexion usados por Django
Cuando usa `DATABASE_URL`, se aplica:
- `conn_max_age=600`: reutiliza conexiones (menos overhead).
- `ssl_require=not DEBUG`: en produccion fuerza SSL hacia la base.

### Que base se usa en cada escenario
- Laptop local (setup rapido): SQLite (`USE_SQLITE=True`).
- Render produccion: PostgreSQL (`USE_SQLITE=False` + `DATABASE_URL`).
- Entorno legado/especial: MySQL (`MYSQL_ADDON_*` o `DB_*`).

## Buenas practicas
- No subir secretos (`.env` ya esta ignorado).
- Versionar cambios de esquema con migraciones Django.
- Validar backup antes de cambios destructivos.
