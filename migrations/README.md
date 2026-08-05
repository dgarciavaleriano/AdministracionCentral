# Persistencia: SQLAlchemy 2.0 + Alembic

Stack: PostgreSQL 17 · SQLAlchemy 2.0 **síncrono** · driver **psycopg 3** · Alembic · pydantic-settings.
Nada de async engine ni de psycopg2.

Las rutas de este documento son relativas a la raíz del repositorio.

## Arranque

```powershell
docker compose up -d --wait
uv sync
uv run alembic upgrade head
```

No hace falta tocar el `.env`: `settings.database_url` trae por defecto la URL del compose local.
Para apuntar a otra base, exporta `DATABASE_URL` (las variables de entorno ganan al `.env`).

| Servicio | Puerto | Base | Persistencia |
|---|---|---|---|
| `db` | 5432 | `administracion` | volumen `postgres_data` |
| `db_test` | 5433 | `administracion_test` | tmpfs, se pierde al parar |

## Mapa de ficheros

```
alembic.ini                        prepend_sys_path = %(here)s/src ; sin URL
migrations/env.py                  URL desde settings, target_metadata, compare_*
migrations/versions/               una migración por fichero
src/config/settings.py             configuración tipada
src/storage/connectors/db.py       engine, SessionLocal, get_db, Base
src/storage/entities/              entidades ORM
src/storage/entities/__init__.py   registro: cada entidad nueva, una línea más
```

`src/models/` son los esquemas Pydantic de la API. No confundir.

## Flujo por cada cambio de esquema

```powershell
# 1. editar la entidad
uv run alembic check                                          # ¿detecta el cambio?
uv run alembic revision --autogenerate -m "descripción corta"
# 2. REVISAR el fichero generado a mano
uv run alembic upgrade head
uv run alembic downgrade -1 ; uv run alembic upgrade head     # el downgrade debe funcionar
uv run alembic check                                          # debe salir limpio
```

El paso 2 no es opcional. El autogenerate se equivoca en los casos de abajo.

Para ver el DDL sin ejecutarlo, modo offline **con rango**:

```powershell
uv run alembic current                        # p.ej. 92836a21d07d
uv run alembic upgrade 92836a21d07d:head --sql
```

Sin `<desde>:<hasta>` arranca desde `base` y vuelca todo el historial. Los rangos solo se aceptan con `--sql`.

## Comandos

| Comando | Para qué |
|---|---|
| `alembic current` | revisión aplicada en ESTA base |
| `alembic history` | cadena completa (`--verbose` para rutas y fechas) |
| `alembic heads` | ramas abiertas; debe salir **una** |
| `alembic upgrade head` / `+1` | aplicar todo / un paso |
| `alembic downgrade -1` / `base` | deshacer un paso / todo |
| `alembic check` | ¿modelo y base divergen? exit 0 si coinciden, ≠0 si no |
| `alembic stamp <rev>` | mover el marcador **sin ejecutar DDL** |
| `alembic merge -m "..." <rev1> <rev2>` | unir dos heads |

## Donde el autogenerate se equivoca

**Renombrar columna.** Genera `drop_column` + `add_column`: pérdida total de datos. Reescribir:

```python
def upgrade():   op.alter_column("users", "phone", new_column_name="telefono")
def downgrade(): op.alter_column("users", "telefono", new_column_name="phone")
```

**Cambiar tipo.** Postgres necesita la conversión explícita:

```python
op.alter_column("users", "nif", type_=sa.String(20), postgresql_using="nif::varchar(20)")
```

(El patrón "tabla de respaldo + copiar + renombrar" es de SQLite. Aquí no aplica.)

**NOT NULL sobre tabla con filas.** Falla. Tres pasos:

```python
op.add_column("users", sa.Column("pais", sa.String(2), nullable=True))
op.execute("UPDATE users SET pais = 'ES' WHERE pais IS NULL")
op.alter_column("users", "pais", nullable=False)
```

**Índices parciales.** Alembic no compara `postgresql_where`: `alembic check` da OK aunque diverja. Revisar a mano.

**Triggers y funciones.** Invisibles para el autogenerate. Van con `op.execute()` y no los detecta ningún check.

## Convenciones del proyecto

- **`NAMING_CONVENTION` en `db.py` está congelada** desde la primera migración. Cambiarla obliga a renombrar restricciones a mano en todos los entornos.
- Con la plantilla `ck`, **toda `CheckConstraint` debe llevar `name=`**. Si falta, `InvalidRequestError` al importar el módulo, no al generar DDL.
- `Mapped[datetime]` → `TIMESTAMPTZ` automáticamente vía `type_annotation_map` en `Base`. No lo declares a mano.
- `server_default` siempre con `text("...")`. La cadena pelada se guarda como valor literal.
- **Prohibido `ENUM` nativo de Postgres.** `op.create_table` emite el `CREATE TYPE` pero `op.drop_table` no emite el `DROP TYPE`: el ciclo `downgrade base` + `upgrade head` aborta con `DuplicateObject`. Usar `String(n)` + `CheckConstraint`.
- Entidad nueva sin línea en `entities/__init__.py` → migración vacía, sin aviso.
- **Toda columna JSONB va envuelta en `MutableDict.as_mutable(JSONB(none_as_null=True))`.** Sin
  `MutableDict`, `obj.campo["x"] = 1` + `commit()` **no emite UPDATE y el cambio se pierde sin error**
  (SQLAlchemy detecta cambios por identidad del objeto, no por contenido). Solo rastrea el primer
  nivel: para dicts anidados, reasignar el atributo entero. Sin `none_as_null`, asignar `None`
  guarda el literal JSON `null`, que satisface el `NOT NULL` y se relee como `None` en vez de dict.
  Ninguna de las dos cosas cambia el DDL, así que no requieren migración.
- **`connect_args={"connect_timeout": N}` en todo `create_engine`.** `pool_timeout` solo limita la
  espera por un hueco libre del pool, no el connect TCP: sin `connect_timeout`, psycopg espera **130 s**
  (su valor por defecto) aunque el sistema operativo rechace la conexión al instante.

## Problemas

| Síntoma | Causa / solución |
|---|---|
| Comando colgado ~30 s sin error | Alguien usó `localhost`. Debe ser `127.0.0.1`: `localhost` resuelve primero a `::1` y docker publica solo en IPv4 |
| `connection refused` | Falta `docker compose up -d --wait`. `-d` a secas retorna antes de que Postgres acepte conexiones |
| `ValidationError` al importar Settings | Un valor del `.env` no casa con el tipo declarado (p. ej. `PORT=abc`). Las claves **no** declaradas no dan error: `settings.py` usa `extra="ignore"` |
| Migración vacía | Falta el import en `entities/__init__.py` |
| `Can't locate revision '...'` | El marcador apunta a un fichero borrado. **`alembic stamp head --purge`** (`stamp head` a secas falla igual: resuelve la revisión actual antes de escribir). Solo si el esquema ya coincide con head |
| `database "..." does not exist` con compose correcto | `initdb` solo aplica `POSTGRES_*` con el datadir vacío. `docker compose down -v` (destruye los datos locales) |
| Dos heads | Dos ramas migraron en paralelo. `alembic heads` → `alembic merge` |
| `uv run uvicorn` bloqueado en Windows | Smart App Control. Usar `uv run python -m uvicorn` |
| `psql` se queda en `--More--` | Añadir `-P pager=off` |
| Un cambio en un campo JSONB no se guarda, sin error | Falta `MutableDict` en esa columna |
| Cualquier cosa tarda exactamente ~130 s en fallar | Falta `connect_timeout` en ese `create_engine` |

`uv run pytest` **sin** `--test-alembic` recolecta solo 2 tests y da verde sin ejecutar ninguno de
los 4 de migraciones. El CI sí pasa el flag. Para reproducir el CI en local: `uv run pytest --test-alembic`.

`alembic.ini` se lee con `encoding="locale"`, no UTF-8: sus comentarios van **sin tildes** o salen como mojibake en Linux.

## Reglas de equipo

1. Una migración = un cambio lógico.
2. Migraciones de datos separadas de las de esquema.
3. Toda operación que borre datos lleva comentario `# DESTRUCTIVE:` explicando qué y por qué.
4. **Una migración publicada no se edita.** Se corrige con otra encima (roll-forward).
5. `pyproject.toml` y `uv.lock` se commitean juntos, siempre.
6. Prohibido `alembic downgrade`, `pytest --test-alembic` o `docker compose down -v` contra un host que no sea `127.0.0.1`. Comprobar el destino con `alembic current` antes.
7. Los ficheros van en LF. Editando en Windows es fácil escribir CRLF sin darse cuenta y entonces la
   PR muestra el fichero entero reescrito. Comprobar con `git diff --numstat` antes de commitear.

## Pendiente de decidir

Nada de esto está implementado. Son decisiones abiertas, no instrucciones.

- **Sembrar un plan por defecto.** `users.plan_id` es NOT NULL y `plans` nace vacía, así que hoy no
  se puede dar de alta a nadie sin crear antes un plan a mano. Falta decidir si va en una migración
  de datos o en un script de arranque.
- **Estrategia de anonimización.** `status = 'anonymized'` existe, pero las columnas de identidad
  (`name`, `surname_1`, `nif`, `birthdate`, `email`, `password_hash`) son NOT NULL por decisión del
  issue: habrá que **sobrescribirlas**, no vaciarlas. Falta definir con qué valores, teniendo en
  cuenta que `nif` y `email` son UNIQUE y dos anonimizados no pueden colisionar.
- **Validar `status`.** Es `String(32)` sin CHECK: hoy entra cualquier cadena, incluido un typo.
- **Normalizar `email` y `nif`.** El UNIQUE de Postgres distingue mayúsculas, así que `12345678z` y
  `12345678Z` conviven como dos personas. Arreglarlo después exige migración de datos con deduplicación.
- **Embeddings del RAG:** `pgvector` en esta misma base o almacén aparte.

## Cuando haya despliegue

Todavía no aplica: no hay ningún entorno desplegado. Escrito para cuando lo haya.

- `DATABASE_URL` sale de los secretos del entorno, nunca de un `.env` ni del default de `settings.py`.
  Las variables de entorno ya ganan al fichero, no hay que cambiar nada en el código.
- `alembic upgrade head` como paso del despliegue, antes de arrancar la aplicación.
- **Backup antes de migrar.** En producción se hace roll-forward, no `downgrade`.
- **Tablas grandes:** `ALTER TABLE` toma un lock `ACCESS EXCLUSIVE` que bloquea lecturas y escrituras.
  Para añadir índices, `CREATE INDEX CONCURRENTLY` (no funciona dentro de una transacción, así que la
  migración necesita `op.get_context().autocommit_block()`). Para cambios incompatibles, patrón
  expand/contract: añadir lo nuevo → escribir en ambos → migrar datos → dejar de usar lo viejo → borrar.
- **PgBouncer** en modo `transaction` es incompatible con psycopg 3 por defecto: prepara en el servidor
  toda consulta ejecutada 5 veces (`prepare_threshold=5`) y esos prepared statements no sobreviven al
  reciclado de conexión. Haría falta `connect_args={"prepare_threshold": None}` y `poolclass=NullPool`.
- Fuera de alcance de este issue: backups automatizados y object storage para los avatares.
