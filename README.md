# AdministracionCentral
Proyecto Jupiter - Administración Central

## Arranque

### Desde VSCode (recomendado)

**Ctrl+Shift+B** ejecuta la tarea «Arrancar todo»: levanta las bases de datos,
aplica las migraciones y arranca la API y el frontal en paralelo. Las tareas
están versionadas en [.vscode/tasks.json](.vscode/tasks.json) y usan
`${workspaceFolder}`, así que funcionan igual en cualquier máquina.

El resto de tareas (bases de datos, migraciones, API, frontal y tests por
separado) están en *Ctrl+Shift+P > Tasks: Run Task*.

### A mano

La API y el frontal son dos proyectos `uv` independientes, cada uno con sus
dependencias y su entorno.

```powershell
Copy-Item .env.example .env         # opcional: todo tiene valor por defecto
docker compose up -d --wait         # bases de datos: db (5432) y db_test (5433)
uv run python -m alembic upgrade head
uv run python src/main.py           # API en http://127.0.0.1:8080
```

En otra terminal, el frontal:

```powershell
Copy-Item ui\.env.example ui\.env   # opcional: todo tiene valor por defecto
cd ui
uv run python main.py               # frontal en http://127.0.0.1:8000
```

`uv run` crea el entorno solo la primera vez, así que no hace falta `uv sync`.

> Los comandos usan `uv run python -m <herramienta>` en vez de `uv run <herramienta>`:
> los ejecutables que `uv` deja en `.venv/Scripts` no van firmados y Smart App
> Control de Windows puede bloquearlos (`os error 4551`). Como módulo no pasan
> por ese intermediario.

`docker compose up` levanta solo las bases de datos. Para arrancar además la API
dentro de un contenedor (en vez de con `main.py` en local):

```powershell
docker compose --profile app up -d --wait
```

## Configuración

Cada proyecto lee su configuración con `pydantic-settings`, con la misma
prioridad: **variables de entorno > fichero `.env` > valores por defecto**.
Todas las claves tienen valor por defecto, así que el proyecto arranca sin
`.env`; los ficheros `.env.example` documentan qué se puede tocar.

| Proyecto | Configuración | Plantilla |
|---|---|---|
| API | [src/config/settings.py](src/config/settings.py) | [.env.example](.env.example) |
| Frontal | [ui/config/settings.py](ui/config/settings.py) | [ui/.env.example](ui/.env.example) |

## Tests

```powershell
uv run python -m pytest --test-alembic   # API y migraciones (necesita las bases levantadas)
cd ui; uv run python -m pytest           # frontal (no necesita nada levantado)
```

## Documentación

- [Modelo de datos](docs/modelo-de-datos.md) — esquema, decisiones y cómo funciona la capa de persistencia.
- [Migraciones](migrations/Guide.md) — cómo trabajar con Alembic: flujo, comandos y cómo escribir una migración.
