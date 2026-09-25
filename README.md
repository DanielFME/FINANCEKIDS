# FinanceKids

Aplicacion web educativa construida con Django para aprendizaje financiero infantil.

## Stack
- Python 3.11+
- Django 5
- PostgreSQL en produccion (Render)
- SQLite en desarrollo local rapido
- MySQL como compatibilidad/fallback y despliegue en Railway
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
2. `DATABASE_URL` (PostgreSQL en Render o MySQL en Railway si la asignas manualmente)
3. `MYSQL_URL`
4. Variables `MYSQLHOST` / `MYSQLPORT` / `MYSQLUSER` / `MYSQLPASSWORD` / `MYSQLDATABASE`
5. Variables `MYSQL_ADDON_*`
6. Variables `DB_*` (MySQL manual)

Interpretacion practica:
- Si `USE_SQLITE=True`, se ignora todo lo demas y se usa `db.sqlite3` local.
- Si `USE_SQLITE=False` y existe `DATABASE_URL`, se conecta usando esa URL (PostgreSQL o MySQL).
- Si no existe `DATABASE_URL`, intenta MySQL con `MYSQL_URL`, `MYSQL*`, `MYSQL_ADDON_*` o `DB_*`.

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
- `ssl_require=not DEBUG`: en produccion fuerza SSL solo para URLs PostgreSQL.

### Que base se usa en cada escenario
- Laptop local (setup rapido): SQLite (`USE_SQLITE=True`).
- Render produccion: PostgreSQL (`USE_SQLITE=False` + `DATABASE_URL`).
- Railway produccion: MySQL (`DATABASE_URL` apuntando al valor de `MYSQL_URL`, `MYSQL_URL` directo o variables `MYSQL*`).
- Entorno legado/especial: MySQL (`MYSQL_ADDON_*` o `DB_*`).

## Despliegue en Railway (paso a paso)

Configuracion validada para este proyecto Django:
- WSGI: `financekids.wsgi:application`
- Build Railway: instala `requirements.txt` y ejecuta `collectstatic`
- Pre-deploy Railway: ejecuta `migrate`
- Start Railway: ejecuta `gunicorn` en `0.0.0.0:$PORT`

### 1) Conectar el repositorio
1. En Railway, crea un proyecto nuevo.
2. Elige **Deploy from GitHub repo**.
3. Selecciona este repositorio en la lista de GitHub.

### 2) Agregar MySQL administrado
1. En el proyecto, agrega un servicio **MySQL**.
2. Railway creara variables como:
   - `MYSQL_URL`
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

### 3) Configurar variables del servicio web
En el servicio Django define al menos:
- `DEBUG=False`
- `SECRET_KEY=<clave larga y aleatoria>`
- `USE_SQLITE=False`

Recomendado:
- `DATABASE_URL` con el mismo valor que Railway expone como `MYSQL_URL` en el servicio MySQL (usa el selector de referencias/variables de Railway para enlazarlo)

Alternativa soportada si prefieres no mapear `DATABASE_URL`:
- dejar `MYSQL_URL` tal como lo expone Railway, o
- usar directamente `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD` y `MYSQLDATABASE`

> La aplicacion da prioridad a `DATABASE_URL`. Si no existe, resuelve MySQL usando `MYSQL_URL`, luego completa o sobreescribe con `MYSQLHOST/MYSQLPORT/MYSQLUSER/MYSQLPASSWORD/MYSQLDATABASE`, y conserva como fallback `MYSQL_ADDON_URI`, `MYSQL_ADDON_*` y `DB_*`.

### 4) Hacer deploy
1. Guarda las variables.
2. Lanza el deploy.
3. Railway usara `railway.toml`:
   - build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - pre-deploy: `python manage.py migrate --noinput`
   - start: `gunicorn financekids.wsgi:application --bind 0.0.0.0:$PORT --workers 2`

### 5) Generar dominio publico
1. En Railway, abre el servicio web.
2. En **Networking**, genera un **Public Domain**.
3. Railway inyecta `RAILWAY_PUBLIC_DOMAIN` automaticamente. El proyecto ya lo agrega a `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`.

Si necesitas hosts/origenes extra, define:
- `ALLOWED_HOSTS=tu-app.up.railway.app,otro-dominio.com`
- `CSRF_TRUSTED_ORIGINS=https://tu-app.up.railway.app,https://otro-dominio.com`

## Verificacion local antes de subir

Con tu virtualenv activo:

```bash
pip install -r requirements.txt
python manage.py test core.tests.RailwayDatabaseSettingsTests -v 2
DEBUG=False SECRET_KEY="dev-only-strong-key" USE_SQLITE=True python manage.py check --deploy
DEBUG=False SECRET_KEY="dev-only-strong-key" USE_SQLITE=True python manage.py collectstatic --noinput
```

En PowerShell:

```powershell
$env:DEBUG="False"
$env:SECRET_KEY="dev-only-strong-key"
$env:USE_SQLITE="True"
python manage.py check --deploy
python manage.py collectstatic --noinput
```

## Troubleshooting Railway

### Ver logs
- Abre el servicio en Railway y revisa la pestaña **Deployments** / **Logs**.
- Si `gunicorn` no inicia, confirma que Railway este usando `railway.toml`.

### Migraciones
- Si el deploy falla en `migrate`, revisa que `USE_SQLITE=False`.
- Confirma que `DATABASE_URL` apunte al mismo valor de `MYSQL_URL` del servicio MySQL correcto.
- Si no usas `DATABASE_URL`, verifica que `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD` y `MYSQLDATABASE` existan en el servicio web.

### Archivos estaticos
- `WhiteNoise` ya esta activo cuando `DEBUG=False`.
- Si faltan estaticos, revisa que el build haya ejecutado `python manage.py collectstatic --noinput`.

### Conexion a base de datos
- Railway MySQL funciona por red privada; no uses `localhost`.
- Usa `DATABASE_URL` enlazado al valor de `MYSQL_URL` o las variables `MYSQL*` inyectadas por Railway.
- Si aparece error de autenticacion o host, vuelve a vincular/revisar la referencia a las variables del servicio MySQL.

## Buenas practicas
- No subir secretos (`.env` ya esta ignorado).
- Versionar cambios de esquema con migraciones Django.
- Validar backup antes de cambios destructivos.
