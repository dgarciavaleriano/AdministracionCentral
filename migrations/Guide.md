# Cómo trabajar con las migraciones

Manual de uso: arrancar, cambiar el esquema, escribir una migración y salir de los errores frecuentes.

**Qué es Alembic, cómo funciona por dentro y cómo está organizada la carpeta** está en
[docs/modelo-de-datos.md](../docs/modelo-de-datos.md). Aquí solo hay comandos y reglas de trabajo.

Las rutas de este documento son relativas a la raíz del repositorio.

## Arrancar y parar

```powershell
docker compose up -d --wait   # Postgres; --wait espera a que acepte conexiones
uv sync                       # dependencias
uv run alembic upgrade head   # crea o actualiza las tablas
uv run alembic current        # debe imprimir la revisión, no vacío
```

La API, en otra terminal: `uv run python src/main.py` (host y puerto salen de `settings`).

No hace falta tocar el `.env`: `settings.database_url` apunta por defecto al compose local.
Para otra base, exporta `DATABASE_URL` (las variables de entorno ganan al `.env`).

Para parar, **la diferencia entre los cuatro comandos es si pierdes los datos o no**:

| Comando | Qué hace | Los datos de `db` |
|---|---|---|
| `Ctrl+C` en la terminal de la API | para la API, la base sigue | intactos |
| `docker compose stop` | para los contenedores | **se conservan** |
| `docker compose start` | los vuelve a arrancar | — |
| `docker compose down` | para y borra los contenedores | **se conservan**, viven en el volumen |
| `docker compose down -v` | además borra los volúmenes | **se destruyen** |

`down -v` es el único que borra datos, y no avisa. Después hay que volver a `up` y a
`alembic upgrade head`, porque la base nace vacía: `initdb` solo aplica las variables `POSTGRES_*`
sobre un datadir vacío, así que también es la forma de arreglar una base creada con la configuración
equivocada.

`db_test` es la excepción: vive en tmpfs, así que su contenido desaparece con cualquier parada. Es
deliberado, no hay nada que conservar ahí.

## Flujo por cada cambio de esquema

```powershell
# 1. editar la entidad en src/storage/entities/
uv run alembic check                                          # ¿detecta el cambio?
uv run alembic revision --autogenerate -m "descripción corta"
# 2. REVISAR a mano el fichero generado
uv run alembic upgrade head
uv run alembic downgrade -1 ; uv run alembic upgrade head     # el downgrade debe funcionar
uv run alembic check                                          # debe salir limpio
```

Un `alembic check` que responde `FAILED: New upgrade operations detected` en el primer paso es la
respuesta correcta: significa que ve tu cambio. Si dice `No new upgrade operations detected`, el cambio
no ha llegado (fichero sin guardar, o entidad nueva sin su línea en `entities/__init__.py`).

El paso 2 no es opcional: el autogenerate se equivoca en los casos de más abajo. La pregunta a hacerse
al leerlo es *¿se pierde algún dato con esto?*

La migración se commitea **en el mismo commit** que la entidad. Una entidad sin su migración deja el CI
en rojo (`alembic check` corre allí); una migración sin su entidad la resucita el próximo autogenerate.

Antes de aplicarla contra algo que importe, ver **Probar una migración sin riesgo** más abajo.

### Crear una tabla nueva

Igual que el flujo de arriba, más un paso que es el fallo más frecuente del proyecto: **registrar la
entidad**. Sin él, el autogenerate no la ve y genera una migración vacía sin avisar.

```python
# src/storage/entities/document.py
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from storage.connectors.db import Base
from storage.entities.mixins import Timestamped, UUIDPrimaryKey


class Document(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    storage_key: Mapped[str] = mapped_column(String(512))
```

```python
# src/storage/entities/__init__.py   <-- SIN ESTO LA MIGRACIÓN SALE VACÍA
from storage.entities.document import Document

__all__ = ["Document", "Plan", "User"]
```

Los mixins de [mixins.py](../src/storage/entities/mixins.py) ponen `id` UUID, `created_at` y
`updated_at`, así que no se declaran a mano. `UUIDPrimaryKey` + `CreatedAt` si la tabla no necesita
`updated_at`.

Recordatorios al declarar columnas:

- `Mapped[str]` es NOT NULL; `Mapped[str | None]` admite NULL. No se escribe `nullable=`.
- `ondelete` va en `ForeignKey`, nunca en `relationship()`: `relationship` no emite DDL.
- Una FK a `users` indexada: Postgres **no** crea índice automático en el lado que apunta, y sin él
  cada borrado o comprobación de integridad hace un recorrido completo de la tabla.

Después, el flujo normal: `alembic check` → `revision --autogenerate` → revisar → `upgrade head`.

## Comandos

| Comando | Para qué |
|---|---|
| `alembic current` | revisión aplicada en ESTA base. Lo primero que mirar siempre |
| `alembic history` | cadena completa (`--verbose` para rutas y fechas) |
| `alembic show <rev>` | detalle de una revisión |
| `alembic heads` | ramas abiertas; debe salir **una** |
| `alembic upgrade head` / `+1` | aplicar todo / un paso |
| `alembic downgrade -1` / `base` | deshacer un paso / todo |
| `alembic check` | ¿modelo y base divergen? exit 0 si coinciden, ≠0 si no |
| `alembic revision -m "..."` | migración vacía para escribirla a mano |
| `alembic revision --autogenerate -m "..."` | migración con las diferencias detectadas |
| `alembic stamp <rev>` | mover el marcador **sin ejecutar DDL** |
| `alembic merge -m "..." <rev1> <rev2>` | unir dos heads |

`stamp` merece cuidado: no toca el esquema, solo reescribe `alembic_version`. Sirve para decirle a
Alembic "esta base ya está como tú crees". Usado por error, deja el marcador mintiendo.

## Cómo se escribe una migración

```python
revision: str = "a1b2c3d4e5f6"          # mi id
down_revision: ... = "cc9184fc36d1"     # de quién vengo: esto forma la cadena

def upgrade() -> None:   ...   # llevar la base hacia adelante
def downgrade() -> None: ...   # dejarla exactamente como estaba
```

Dentro se usa `op`, la API de operaciones de esquema:

| Operación | Llamada |
|---|---|
| Crear / borrar tabla | `op.create_table("t", sa.Column(...), ...)` · `op.drop_table("t")` |
| Añadir / quitar columna | `op.add_column("t", sa.Column("c", sa.String(50)))` · `op.drop_column("t", "c")` |
| Cambiar columna | `op.alter_column("t", "c", type_=..., nullable=..., new_column_name=...)` |
| Índice | `op.create_index(op.f("ix_t_c"), "t", ["c"])` · `op.drop_index(op.f("ix_t_c"), table_name="t")` |
| UNIQUE / CHECK / FK | `op.create_unique_constraint` · `op.create_check_constraint` · `op.create_foreign_key` |
| Renombrar tabla | `op.rename_table("vieja", "nueva")` |
| Insertar datos | `op.bulk_insert(tabla, [{...}])` |
| SQL a pelo | `op.execute("UPDATE users SET ...")` |

- **`op.f("...")`** marca un nombre como definitivo para que no se le reaplique la plantilla de nombres.
  Lo pone el autogenerate; respétalo.
- **`sa.text("...")`** es obligatorio en los `server_default`. Sin él, `server_default="now()"` guarda
  la cadena literal `now()` en vez de llamar a la función.
- **El orden importa.** Postgres no deja borrar `plans` mientras `users` la referencie: el `downgrade`
  es el `upgrade` leído del revés.

### Donde el autogenerate se equivoca

**Renombrar columna.** Genera `drop_column` + `add_column`: pérdida total de datos. Reescribir:

```python
def upgrade():   op.alter_column("users", "phone", new_column_name="telefono")
def downgrade(): op.alter_column("users", "telefono", new_column_name="phone")
```

**Cambiar tipo.** Postgres necesita la conversión explícita:

```python
op.alter_column("users", "nif", type_=sa.String(20), postgresql_using="nif::varchar(20)")
```

**No hace falta tabla de respaldo.** El patrón "crear tabla nueva, copiar, borrar la vieja, renombrar"
es de **SQLite**, que no sabe modificar una columna. Postgres sí: `ALTER TABLE ... ALTER COLUMN ... TYPE`
convierte los datos en el sitio, y si algún valor no se puede convertir la migración falla entera y no
se aplica nada. Copiar ese patrón aquí es trabajo de más y riesgo de más.

Solo hay dos casos en los que sí hacen falta varios pasos:

- **La conversión no es automática** (p. ej. `varchar` → `int` con valores sucios). Se limpia antes:

  ```python
  op.execute("UPDATE users SET edad = NULL WHERE edad !~ '^[0-9]+$'")
  op.alter_column("users", "edad", type_=sa.Integer, postgresql_using="edad::integer")
  ```

- **Quieres conservar los valores originales.** Entonces es expand/contract, y la columna vieja es tu
  copia de seguridad hasta que decidas borrarla en otra migración:

  ```python
  op.add_column("users", sa.Column("nif_nuevo", sa.String(20)))
  op.execute("UPDATE users SET nif_nuevo = upper(trim(nif))")
  # la columna `nif` sigue ahí: si algo sale mal, los datos originales no se han tocado
  ```

**NOT NULL sobre tabla con filas.** Falla. Tres pasos:

```python
op.add_column("users", sa.Column("pais", sa.String(2), nullable=True))
op.execute("UPDATE users SET pais = 'ES' WHERE pais IS NULL")
op.alter_column("users", "pais", nullable=False)
```

**Índices parciales.** No compara `postgresql_where` de forma fiable: `alembic check` puede dar OK
aunque diverja. Revisar a mano.

**Triggers, funciones y vistas.** Invisibles para el autogenerate. Van con `op.execute()` y no los
detecta ningún check.

**Migraciones de datos.** Solo mira estructura. Rellenar o mover datos lo escribes tú.

## Convenciones al escribir código

- **No cambies `NAMING_CONVENTION` de `db.py`.** Está congelada desde la primera migración: tocarla
  obliga a renombrar restricciones a mano en todos los entornos.
- Con la plantilla `ck`, **toda `CheckConstraint` debe llevar `name=`**. Si falta, `InvalidRequestError`
  al importar el módulo, no al generar DDL.
- `Mapped[datetime]` ya es `TIMESTAMPTZ`. No lo declares a mano.
- `server_default` siempre con `text("...")`.
- **Prohibido `ENUM` nativo de Postgres.** `op.create_table` emite el `CREATE TYPE` pero `op.drop_table`
  no emite el `DROP TYPE`: el ciclo `downgrade base` + `upgrade head` aborta con `DuplicateObject`.
  Usar `String(n)` + `CheckConstraint`.
- **Entidad nueva → una línea en `entities/__init__.py`.** Si falta, la migración sale vacía sin aviso.
- **Toda columna JSONB va envuelta en `MutableDict.as_mutable(JSONB(none_as_null=True))`.** Sin
  `MutableDict`, `obj.campo["x"] = 1` + `commit()` **no emite UPDATE y el cambio se pierde sin error**
  (SQLAlchemy detecta cambios por identidad del objeto, no por contenido). Solo rastrea el primer
  nivel: para dicts anidados, reasignar el atributo entero. Sin `none_as_null`, asignar `None` guarda
  el literal JSON `null`, que satisface el `NOT NULL` y se relee como `None` en vez de dict. Ninguna
  de las dos cosas cambia el DDL, así que no requieren migración.
- **`connect_args={"connect_timeout": N}` en todo `create_engine`.** `pool_timeout` solo limita la
  espera por un hueco libre del pool, no el connect TCP. Y sin `connect_timeout` no hay límite propio:
  manda el sistema operativo, que tarda **~130 s** en agotar los reintentos TCP cuando los paquetes se
  pierden (contenedor caído, IP equivocada). Un puerto que rechaza activamente sí falla al instante.

## Tests

```powershell
docker compose up -d --wait db_test
uv run pytest --test-alembic
```

`pytest-alembic` aporta cuatro tests que no hay que escribir: que hay un solo head, que la cadena sube
desde cero, que el modelo coincide con el DDL resultante y que **todos los `downgrade` funcionan**.

Corren contra `db_test` (5433), **nunca** contra la base de desarrollo: el test de ida y vuelta hace
`downgrade` hasta base, o sea DROP de todas las tablas. Dos salvaguardas lo impiden: el fixture
`alembic_engine` de `tests/conftest.py` aborta si `TEST_DATABASE_URL` coincide con `DATABASE_URL`, y
`env.py` usa la conexión que le inyecta pytest en vez de abrir la suya.

`uv run pytest` **sin** `--test-alembic` recolecta solo 2 tests y da verde sin ejecutar ninguno de los
4 de migraciones. El CI sí pasa el flag.

## Probar una migración sin riesgo

Nunca hace falta estrenar una migración contra la base buena. Hay tres niveles, de menos a más real.

**1. Ver el SQL sin ejecutarlo.** Modo offline: imprime el DDL y no aplica nada.

```powershell
uv run alembic current                        # p.ej. cc9184fc36d1
uv run alembic upgrade cc9184fc36d1:head --sql
```

El rango `<desde>:<hasta>` no es opcional en la práctica: sin él arranca desde `base` y vuelca todo el
historial en vez de lo que falta por aplicar. Los rangos solo se aceptan con `--sql`.

**2. Contra la base desechable.** `db_test` vive en tmpfs: se rompe, se para y desaparece.

```powershell
docker compose up -d --wait db_test
$env:DATABASE_URL = "postgresql+psycopg://app:app@127.0.0.1:5433/administracion_test"
uv run alembic upgrade head
```

Cierra esa terminal al terminar. Mientras `DATABASE_URL` valga eso, coincide con `TEST_DATABASE_URL` y
`pytest --test-alembic` se negará a arrancar (es la salvaguarda del `conftest.py` haciendo su trabajo).

**3. Contra una copia de los datos reales.** Es lo único que detecta los fallos que solo aparecen con
filas dentro: un `NOT NULL` que no se cumple, una conversión de tipo que revienta con un valor sucio,
un UNIQUE que ya está duplicado.

```powershell
# copiar la base de trabajo a db_test
docker compose exec db pg_dump -U app -d administracion -Fc -f /tmp/copia.dump
docker compose cp db:/tmp/copia.dump .\copia.dump
docker compose cp .\copia.dump db_test:/tmp/copia.dump
docker compose exec db_test pg_restore -U app -d administracion_test --clean --if-exists /tmp/copia.dump

# migrar SOLO la copia
$env:DATABASE_URL = "postgresql+psycopg://app:app@127.0.0.1:5433/administracion_test"
uv run alembic upgrade head
```

**El `docker compose cp` no es un rodeo.** En PowerShell, `... > fichero.dump` reescribe la salida como
texto y corrompe un dump binario (`-Fc`). Sacando el fichero con `cp` no pasa por la shell.

## Si algo se rompe

"Recuperar una tabla" son cuatro problemas distintos con cuatro respuestas distintas. Lo primero es
saber cuál tienes.

| Qué ha pasado | Cómo se recupera | Qué recuperas |
|---|---|---|
| Una migración **falla a mitad** | Nada que hacer: Postgres deshace la transacción entera | Todo. La base queda como antes |
| Aplicaste una migración **que no querías** | `alembic downgrade -1` | **La estructura, no los datos** |
| **Datos** borrados o machacados por error | Restaurar un backup | Lo que hubiera en el backup |
| La base local está **inservible** (solo desarrollo) | `docker compose down -v` y volver a migrar | Una base limpia y vacía |
| El **marcador** no cuadra con la realidad | `alembic stamp <rev>` | Solo el marcador; el esquema no se toca |

### El `downgrade` devuelve la estructura, no los datos

Es lo más importante de esta sección. Si una migración hizo `drop_column("users", "phone")`, su
`downgrade` hace `add_column("users", "phone")` y te devuelve **la columna vacía**: los teléfonos ya no
existen. Alembic versiona la estructura de la base, no su contenido.

Por eso:

- Cualquier migración que borre datos lleva comentario `# DESTRUCTIVE:` (regla 3) **y backup antes**.
- Cuando quieras poder volver atrás con los datos incluidos, usa expand/contract: añade la columna
  nueva y deja la vieja hasta estar seguro. La columna vieja es la copia de seguridad.

### Backup y restauración

```powershell
# Copia completa (esquema + datos)
docker compose exec db pg_dump -U app -d administracion -Fc -f /tmp/backup.dump
docker compose cp db:/tmp/backup.dump .\backup.dump

# Restaurar encima
docker compose cp .\backup.dump db:/tmp/backup.dump
docker compose exec db pg_restore -U app -d administracion --clean --if-exists /tmp/backup.dump
```

Una sola tabla, cuando solo se ha roto esa:

```powershell
docker compose exec db pg_dump -U app -d administracion -Fc -t users -f /tmp/users.dump
docker compose exec db pg_restore -U app -d administracion --clean --if-exists -t users /tmp/users.dump
```

Restaurar una tabla suelta **no comprueba las claves foráneas de las demás**: si `users` vuelve a un
estado anterior y `plans` no, puedes acabar con referencias a planes que ya no existen. Ante la duda,
restaura entera.

### Corrupción de verdad

Si Postgres devuelve errores de página o de checksum, eso no es Alembic ni SQLAlchemy: es el
almacenamiento. Se sale de ahí restaurando un backup, y no hay atajo. En este proyecto **no hay backups
automatizados todavía** — hoy, en desarrollo, la copia la haces tú antes de tocar algo delicado.

En el momento en que haya un entorno desplegado, `pg_dump` programado y point-in-time recovery
(`archive_mode` + WAL) dejan de ser opcionales. Está anotado como pendiente.

## Problemas

| Síntoma | Causa / solución |
|---|---|
| Comando colgado ~30 s sin error | Alguien usó `localhost`. Debe ser `127.0.0.1`: `localhost` resuelve primero a `::1` y docker publica solo en IPv4 |
| `connection refused` | Falta `docker compose up -d --wait`. `-d` a secas retorna antes de que Postgres acepte conexiones |
| `ValidationError` al importar Settings | Un valor del `.env` no casa con el tipo declarado (p. ej. `PORT=abc`). Las claves **no** declaradas no dan error: `settings.py` usa `extra="ignore"` |
| Migración vacía | Falta el import en `entities/__init__.py` |
| `Can't locate revision '...'` | El marcador apunta a un fichero borrado. **`alembic stamp head --purge`** (`stamp head` a secas falla igual: resuelve la revisión actual antes de escribir). Solo si el esquema ya coincide con head |
| `database "..." does not exist` con compose correcto | `initdb` solo aplica `POSTGRES_*` con el datadir vacío. `docker compose down -v` (destruye los datos locales) |
| Dos heads | Ver abajo |
| `uv run uvicorn` bloqueado en Windows | Smart App Control. Usar `uv run python -m uvicorn` |
| `psql` se queda en `--More--` | Añadir `-P pager=off` |
| Un cambio en un campo JSONB no se guarda, sin error | Falta `MutableDict` en esa columna |
| Cualquier cosa tarda ~130 s en fallar | Falta `connect_timeout` en ese `create_engine`: manda el timeout TCP del sistema operativo |

`alembic.ini` se lee con `encoding="locale"`, no UTF-8: sus comentarios van **sin tildes** o salen como mojibake en Linux.

### Dos heads

Dos ramas partieron de la misma revisión y cada una creó la suya, así que las dos tienen el mismo
`down_revision`. Git las mergea sin protestar —los ficheros no se tocan entre sí— y queda una cadena
con dos finales, así que `upgrade head` no sabe cuál aplicar. Se arregla con una revisión de unión,
que no contiene DDL:

```powershell
uv run alembic heads                              # confirma que hay dos
uv run alembic merge -m "merge a1b2c3 y d4e5f6" a1b2c3 d4e5f6
uv run alembic upgrade head
```

Se evita coordinando: quien vaya a migrar, que parta de `develop` actualizado.

## Reglas de equipo

1. Una migración = un cambio lógico.
2. Migraciones de datos separadas de las de esquema.
3. Toda operación que borre datos lleva comentario `# DESTRUCTIVE:` explicando qué y por qué.
4. **Una migración publicada no se edita.** Se corrige con otra encima (roll-forward): editarla después
   de que alguien la haya aplicado deja su base en un estado que ya no corresponde a su id.
5. `pyproject.toml` y `uv.lock` se commitean juntos, siempre.
6. Prohibido `alembic downgrade`, `pytest --test-alembic` o `docker compose down -v` contra un host que
   no sea `127.0.0.1`. Comprobar el destino con `alembic current` antes.
7. Los ficheros van en LF. Editando en Windows es fácil escribir CRLF sin darse cuenta y entonces la PR
   muestra el fichero entero reescrito. Comprobar con `git diff --numstat` antes de commitear.

## Cuando haya despliegue

Todavía no aplica, no hay ningún entorno desplegado.

- `DATABASE_URL` desde los secretos del entorno, nunca desde un `.env` ni del default de `settings.py`.
- `alembic upgrade head` como paso del despliegue, antes de arrancar la aplicación.
- **Backup antes de migrar.** En producción se hace roll-forward, no `downgrade`.
- Tablas grandes: `ALTER TABLE` toma un lock `ACCESS EXCLUSIVE`. Índices con `CREATE INDEX CONCURRENTLY`
  dentro de `op.get_context().autocommit_block()`; cambios incompatibles con patrón expand/contract.
- **PgBouncer** en modo `transaction` es incompatible con psycopg 3 por defecto (`prepare_threshold=5`):
  haría falta `connect_args={"prepare_threshold": None}` y `poolclass=NullPool`.
