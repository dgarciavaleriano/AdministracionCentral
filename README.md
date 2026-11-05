# AdministracionCentral
Proyecto Jupiter - Administración Central

Asistente que acompaña al ciudadano en sus trámites administrativos, empezando por la declaración del IRPF.

Este repositorio es la API. El frontal está en [AdministracionCentral-UI](https://github.com/alchemistC137/AdministracionCentral-UI).

| Carpeta | Qué hay |
|---|---|
| `src/` | API con FastAPI y SQLAlchemy sobre PostgreSQL |
| `tests/` | Tests de la API con pytest |
| `docs/` | Documentación del proyecto |

## Arranque

**Desde VSCode:** `Ctrl+Shift+B` levanta la base de datos, aplica las migraciones y arranca la API.

**A mano:**

```powershell
docker compose up -d --wait db           # PostgreSQL en el puerto 5432
uv run python -m alembic upgrade head    # crea o actualiza las tablas
uv run python src/main.py                # API en http://127.0.0.1:8080 (documentación en /docs)
```

`uv run` instala las dependencias la primera vez. Para levantar también la API dentro de Docker: `docker compose up -d --wait` (el contenedor aplica las migraciones al arrancar).

## Migraciones (Alembic)

Las tablas se definen en `src/storage/entities/` y se crean o cambian con migraciones, que viven en `migrations/versions/`.

**Después de hacer pull**, por si alguien ha cambiado alguna tabla:

```powershell
uv run python -m alembic upgrade head
```

**Si cambias o creas una tabla:**

```powershell
uv run python -m alembic revision --autogenerate -m "añadir tabla documents"
# revisa el fichero que se genera en migrations/versions/ y súbelo con tu PR
uv run python -m alembic upgrade head
```

- Una tabla nueva hay que importarla en `src/storage/entities/__init__.py`. Si no, Alembic no la ve.
- Revisa siempre el fichero generado: si renombras una columna, Alembic lo entiende como borrar una y crear otra, y se pierden los datos. En ese caso, cámbialo a mano por `op.alter_column(..., new_column_name=...)`.
- Para deshacer la última migración: `uv run python -m alembic downgrade -1`.
- Si `upgrade` dice *Can't locate revision*, tu base tiene aplicada una migración que no está en tu rama. Bórrala con `docker compose down -v` y vuelve a levantarla y migrar.
- La CI falla si cambias una tabla y no subes su migración.

## Configuración

Todo tiene un valor por defecto, así que no hace falta ningún `.env`. Para cambiar algo, copia `.env.example` a `.env`.

## Tests

```powershell
uv run python -m pytest            # necesita la base levantada y migrada
```

> Usamos `uv run python -m ...` porque Smart App Control de Windows puede bloquear los ejecutables que `uv` deja en `.venv/Scripts`.

## Documentación

- [Modelo de datos](docs/modelo-de-datos.md)
