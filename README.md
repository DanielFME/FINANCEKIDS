# FinanceKids

Aplicación web educativa construida con Django para aprendizaje financiero infantil.

## Resumen
FinanceKids es una plataforma monolítica con autenticación, progreso por temas y contenido educativo sobre finanzas básicas para niños y jóvenes.

## Stack
- Python 3.11+
- Django 5
- HTML, CSS y JavaScript para la interfaz
- PostgreSQL en producción (Render)
- SQLite en desarrollo local rápido
- MySQL como compatibilidad/fallback
- GitHub Actions para CI

## Estructura principal
- `financekids/`: configuración del proyecto Django
- `core/`: vistas, templates, lógica principal y páginas educativas
- `game/`: modelos de dominio (temas y perfil)
- `scripts/`: utilidades operativas locales
- `CONTRIBUTING.md`: guía de trabajo en equipo y checklist de PR
- `ARCHITECTURE.md`: documentación de arquitectura del proyecto

## Qué incluye la aplicación
- Página de inicio con progreso global y acceso a temas
- Lecciones educativas por tema
- Sistema de avance/desbloqueo de contenidos
- Pantallas de login y registro mejoradas
- Validaciones en JavaScript
- Diseño responsive para móvil y escritorio

## Requisitos
- Python instalado
- Git instalado
- Dependencias del proyecto en `requirements.txt`
- MySQL solo si vas a usar ese motor en local o en un entorno legado

## Inicio rápido para desarrollo local
1. Clona el repositorio.
2. Crea un entorno virtual:
   - `python -m venv .venv`
3. Activa el entorno virtual:
   - PowerShell: `.venv\Scripts\Activate.ps1`
   - Bash: `source .venv/bin/activate`
4. Instala dependencias:
   - `pip install -r requirements.txt`
5. Copia `.env.example` a `.env`.
6. Ejecuta migraciones:
   - `python manage.py migrate`
7. Ejecuta tests:
   - `python manage.py test`
8. Levanta el servidor:
   - `python manage.py runserver`

- App: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

### Opción rápida en Windows
Puedes usar los scripts incluidos:
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_local_windows.ps1`
- `powershell -ExecutionPolicy Bypass -File .\scripts\start_local_windows.ps1`

También hay accesos directos `.bat` en `scripts/`.

## Configuración de entorno
Usa `.env.example` como plantilla.

Variables destacadas:
- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `USE_SQLITE`
- `DATABASE_URL`
- `MYSQL_ADDON_*` o `DB_*` si usas MySQL

## Base de datos
La aplicación usa una estrategia flexible definida en `financekids/settings.py`.

Orden de prioridad actual:
1. `USE_SQLITE=True`
2. `DATABASE_URL` (PostgreSQL, recomendado en Render)
3. Variables `MYSQL_ADDON_*`
4. Variables `DB_*` (MySQL manual)

Interpretación práctica:
- Si `USE_SQLITE=True`, se usa `db.sqlite3`.
- Si `USE_SQLITE=False` y existe `DATABASE_URL`, se usa PostgreSQL.
- Si no existe `DATABASE_URL`, intenta MySQL.

## Trabajo en equipo
Consulta `CONTRIBUTING.md` para el flujo de ramas y checklist de PR.

Flujo sugerido:
1. Crear rama desde `develop`: `feat/<nombre>` o `fix/<nombre>`
2. Hacer commits pequeños y descriptivos
3. Abrir Pull Request hacia `develop`
4. Esperar CI en verde y review
5. Merge

## CI
Archivo: `.github/workflows/ci.yml`

El pipeline ejecuta:
1. Instalación de dependencias
2. Migraciones
3. Tests de Django

## Notas
- No subas secretos al repositorio.
- Versiona cambios de esquema con migraciones de Django.
- Valida backups antes de cambios destructivos.
- Si trabajas con MySQL y necesitas unificar esquema, puedes usar:
  - `python manage.py unify_mysql_schema`
