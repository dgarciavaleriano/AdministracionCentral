# Cómo trabajar con las migraciones

Todo lo que se teclea en una terminal o se escribe en `migrations/versions/`.
El porqué de cada pieza está en [docs/modelo-de-datos.md](../docs/modelo-de-datos.md).
Rutas relativas a la raíz del repositorio.

> **Las secciones 1 a 7 son todo lo que necesitas para trabajar.** De la 8 en adelante, consulta.

| Tengo que… | Ve a |
|---|---|
| Crear una tabla | [§4](#4-crear-una-tabla) |
| Añadir, cambiar o renombrar una columna | [§5](#5-modificar-una-tabla) |
| Borrar una columna o una tabla | [§6](#6-eliminar-una-columna-o-una-tabla) |
| Entender el `# DESTRUCTIVE:` que me pide el CI | [§7](#7-cómo-funciona--destructive) |
| Salir de un error | [§8](#8-desatascarse) |
| Arrancar el entorno, o cambiar de rama | [§10](#10-arrancar-parar-y-cambiar-de-rama) |
| Buscar un comando | [§11](#11-tabla-de-comandos) |

## 1. Modelo mental

- **Entidad** — clase de `src/storage/entities/`. Describe una tabla, no la crea.
- **`Base.metadata`** — la lista de tablas que *deberían* existir. Se rellena importando entidades.
- **Migración** — fichero de `versions/` con el DDL de un cambio y cómo deshacerlo.
- **Head** — el último eslabón de la cadena. Debe haber **uno**.
- **Autogenerate** — compara `Base.metadata` con la base real y escribe la diferencia.

**Git versiona ficheros; Alembic versiona tu base.** Revertir el commit que creó una tabla no ejecuta el
`DROP TABLE` ([§10](#10-arrancar-parar-y-cambiar-de-rama)). Y **el `downgrade` devuelve la estructura,
no los datos**: el inverso de `drop_column` es `add_column`, y te da la columna vacía.

## 2. Reglas que no se negocian

1. **Una migración publicada no se edita.** Se corrige con otra encima.
2. **El fichero autogenerado se revisa siempre** ([§13](#13-dónde-el-autogenerate-se-equivoca)). La
   pregunta al leerlo es *¿se pierde algún dato?*
3. **Todo borrado lleva copia antes y marca dentro** ([§6](#6-eliminar-una-columna-o-una-tabla)).
4. **Un solo head.** `alembic heads` antes de abrir la PR: ni git ni `alembic check` ven la bifurcación.
5. **Entidad, `__init__.py` y migración van en el mismo commit.** Entidad sin migración deja el CI en
   rojo; migración sin entidad la resucita el próximo autogenerate.
6. **Una migración = un cambio lógico.** Las de datos, separadas de las de esquema.
7. **`pyproject.toml` y `uv.lock` se commitean juntos.** El CI corre `uv sync --locked`.
8. **Nada destructivo contra una base que no sea la tuya.** Comprueba el destino con `alembic current`.
9. **Los ficheros van en LF**, o la PR aparece entera reescrita. `git diff --numstat`.

## 3. Antes de tocar nada

```powershell
docker compose up -d --wait      # --wait espera a que Postgres acepte conexiones
uv sync
uv run alembic upgrade head
uv run alembic current           # debe terminar en (head)
uv run alembic heads             # debe salir una sola línea
```

**Si `current` no termina en `(head)`, para**: el autogenerate compararía tu modelo contra una base
atrasada y escribiría diferencias que no existen.

Para mirar la base a mano, `docker compose exec db psql -U app -d administracion -P pager=off`
(`\dt`, `\d users`, `\q`); sin el `pager=off`, `psql` se queda en `--More--` y parece colgado.

## 4. Crear una tabla

**1. La entidad**, un fichero por tabla:

```python
# src/storage/entities/document.py
class Document(UUIDPrimaryKey, Timestamped, Base):
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    storage_key: Mapped[str] = mapped_column(String(512))
```

Los mixins ya ponen `id`, `created_at` y `updated_at`; `Mapped[str]` es NOT NULL y `Mapped[str | None]`
admite NULL. Resto de reglas en [modelo-de-datos §1](../docs/modelo-de-datos.md#1-las-reglas-de-modelado).

**2. Registrarla** en `entities/__init__.py` (import y `__all__`), o Alembic no la ve. Si lo olvidas y
la migración quedaría vacía, `env.py` aborta con `SystemExit: Nada que migrar…`; **pero si lleva otro
cambio, no aborta y tu tabla se omite en silencio.**

**3. El ciclo:**

```powershell
uv run alembic check                                          # ¿ve el cambio?
uv run alembic revision --autogenerate -m "crear documents"
# --- revisar a mano el fichero generado ---
uv run alembic upgrade head
uv run alembic downgrade -1 ; uv run alembic upgrade head     # seguro: esta migración solo crea
uv run alembic check                                          # debe salir limpio
```

`FAILED: New upgrade operations detected` en el primer `check` es lo **correcto**: ve tu cambio.
`No new upgrade operations detected` significa que no ha llegado (fichero sin guardar, o falta el paso 2).

## 5. Modificar una tabla

| Caso | ¿Acierta el autogenerate? | Qué haces |
|---|---|---|
| Añadir columna nullable, o NOT NULL a tabla vacía | Sí | El ciclo de [§4](#4-crear-una-tabla) |
| Añadir NOT NULL a tabla **con filas** | No, falla al aplicar | Tres pasos, abajo |
| Alargar un tipo (`String(16)`→`String(20)`, `int`→`bigint`) | Sí, Postgres convierte solo | Igual |
| Cambiar a un tipo distinto (`varchar`→`int`) | Le falta la conversión | `postgresql_using`, [§13](#13-dónde-el-autogenerate-se-equivoca) |
| **Renombrar** una columna | **No: `drop` + `add`, pérdida total** | Reescribir, abajo |
| Índice, unique, FK | Sí | Igual |
| Trigger, vista, función | **Invisible** | `op.execute()`, [§13](#13-dónde-el-autogenerate-se-equivoca) |

```python
# NOT NULL sobre tabla con filas: tres pasos en la misma migración
op.add_column("users", sa.Column("pais", sa.String(2), nullable=True))
op.execute("UPDATE users SET pais = 'ES' WHERE pais IS NULL")
op.alter_column("users", "pais", nullable=False)

# Renombrar: sustituye entero el drop+add que genera el autogenerate
def upgrade():   op.alter_column("users", "phone", new_column_name="telefono")
def downgrade(): op.alter_column("users", "telefono", new_column_name="phone")
```

## 6. Eliminar una columna o una tabla

El único flujo que destruye datos. El orden es a propósito.

**1. Copia, antes de nada.** El `cp` no es un rodeo: en PowerShell, `> fichero.dump` reescribe la salida
como texto y corrompe un dump binario.

```powershell
docker compose exec db pg_dump -U app -d administracion -Fc -f /tmp/pre-borrado.dump
docker compose cp db:/tmp/pre-borrado.dump .\pre-borrado.dump
```

**2.** Quita la columna o la clase de la entidad, y de `entities/__init__.py` si borras la tabla.

**3.** `uv run alembic revision --autogenerate -m "borrar ..."`.

**4. Lee el fichero.** Un `drop_table` arrastra sus índices, sus restricciones y las filas de otras
tablas que dependan de ella.

**5. Escribe la marca dentro de `upgrade()`**, diciendo qué se pierde:

```python
def upgrade() -> None:
    # DESTRUCTIVE: elimina users.phone y todos los teléfonos guardados.
    # Copia previa en pre-borrado.dump.
    op.drop_column("users", "phone")
```

**6.** `uv run alembic upgrade head`.

> **Aquí no hagas el `downgrade -1 ; upgrade head` de [§4](#4-crear-una-tabla)**: aplicaría el borrado
> dos veces. Para probar la ida y vuelta, contra `db_test` ([§15](#15-probar-una-migración-sin-riesgo)).

## 7. Cómo funciona `# DESTRUCTIVE:`

[El vigilante](../scripts/check_destructive_migrations.py) corre en el CI antes de que ninguna migración
toque una base. En local se lanza a mano, no hay hook:
`uv run python scripts/check_destructive_migrations.py`.

**La marca es literal**: `# DESTRUCTIVE:`, con un espacio y dos puntos. `#DESTRUCTIVE:`,
`# destructive:` y `# DESTRUCTIVE` no valen y dejan la PR en rojo igual.

**Detecta** `op.drop_table`, `op.drop_column` y `op.execute("...")` con `DELETE`, `TRUNCATE` o `DROP` en
el SQL literal. Solo en `upgrade()`: los `drop` de `downgrade()` se ignoran a propósito, son el inverso
normal de un `create_table`.

**No detecta.** Todo esto destruye datos y hoy pasa en verde:

| Se cuela | Por qué |
|---|---|
| `op.execute(sa.text("DELETE ..."))`, o el SQL en una variable | Deja de ser un literal pegado a `execute` |
| `f"DROP TABLE {tabla}"` | Un f-string no es una constante |
| El `drop` en una función auxiliar del fichero | Solo se recorre el cuerpo de `upgrade()` |
| `UPDATE users SET nif = NULL` | El patrón no cubre `UPDATE` |
| `alter_column` a un tipo más corto | No está entre las operaciones vigiladas |

**La marca se busca en el fichero entero**: si la cadena aparece en cualquier punto —docstring, string,
`downgrade()`— esa migración queda exenta **para siempre**, incluidas las operaciones que alguien añada
después. Hoy [cc9184fc36d1](versions/cc9184fc36d1_create_plans_and_users.py) la tiene en su
`downgrade()` y ya está fuera del chequeo.

Escríbela siempre **dentro de `upgrade()` y pegada a la operación**: es lo que se espera leer en la
revisión, aunque el script se conforme con menos. Sus falsos positivos, en [§9](#9-anatomía-del-vigilante).

---

> **Fin de lo imprescindible.** De aquí abajo, consulta.

## 8. Desatascarse

| Síntoma | Causa / solución |
|---|---|
| Colgado ~30 s sin error | Alguien usó `localhost`. Debe ser `127.0.0.1`: `localhost` resuelve primero a `::1` y docker publica solo en IPv4 |
| `connection refused` | Falta `--wait`. `-d` a secas retorna antes de que Postgres acepte conexiones |
| `SystemExit: Nada que migrar` | Falta la línea en `entities/__init__.py`, o el fichero sin guardar |
| Migración vacía **sin** ese error | Llevaba otro cambio, la salvaguarda no saltó. Revisa el registro |
| `Can't locate revision` | El marcador apunta a un fichero borrado. `alembic stamp head --purge` (`stamp head` a secas falla igual: resuelve la revisión actual antes de escribir). Solo si el esquema ya coincide |
| `database "..." does not exist` | `initdb` solo aplica `POSTGRES_*` con el datadir vacío. `down -v` y volver a migrar |
| Sobran tablas de otra rama | Cambiaste de rama sin deshacer ([§10](#10-arrancar-parar-y-cambiar-de-rama)). En desarrollo, `down -v` es más rápido y seguro que borrarlas a mano |
| Dos heads | [§18](#18-dos-heads) |
| El vigilante salta y no borras nada | Falso positivo ([§9](#9-anatomía-del-vigilante)). Pon la marca explicando por qué no se pierde nada |
| `ValidationError` en `Settings` | Un valor del `.env` no casa con su tipo. Las no declaradas no dan error: `extra="ignore"` |
| `uv run uvicorn` bloqueado | Smart App Control. Usar `uv run python -m uvicorn` |
| Un cambio JSONB no se guarda, sin error | Falta `MutableDict` en esa columna |
| Algo tarda ~130 s en fallar | Falta `connect_timeout` en ese `create_engine`: manda el timeout TCP del sistema |

## 9. Anatomía del vigilante

Análisis estático puro, sin conectar a ninguna base: el interruptor de fichero de
[§7](#7-cómo-funciona--destructive) es un `in` sobre el texto, antes de parsear. Evita despistes, no
sabotajes; leer la migración sigue siendo del que aprueba la PR. Endurecerlo está pendiente.

También da **falsos positivos**: `ADD CONSTRAINT ... ON DELETE CASCADE`, `DROP NOT NULL`, `DROP INDEX` o
un `COMMENT ON` que mencione DELETE saltan sin destruir nada. Si te toca uno, la marca es la salida
correcta: explica en ella por qué no se pierde nada.

## 10. Arrancar, parar y cambiar de rama

```powershell
docker compose up -d --wait
uv run python src/main.py        # la API, en otra terminal
```

`settings.database_url` apunta por defecto al compose local. Para otra base, exporta `DATABASE_URL`.
De las formas de parar, **solo `docker compose down -v` borra datos**, y no avisa; es también la forma
de arreglar una base creada con la configuración equivocada, porque `initdb` solo aplica las variables
`POSTGRES_*` sobre un datadir vacío. `db_test` vive en tmpfs y se vacía con cualquier parada.

**Al cambiar de rama, el orden importa**, porque tu base no se mueve con git. Si cambias primero, las
migraciones desaparecen del disco pero sus tablas siguen ahí, y `downgrade` ya no puede deshacerlas:

```powershell
uv run alembic downgrade <revision-comun>   # PRIMERO deshacer
git switch otra-rama                        # DESPUÉS cambiar
uv run alembic upgrade head
```

## 11. Tabla de comandos

| Comando | Para qué | Riesgo |
|---|---|---|
| `alembic current` / `heads` / `check` | Dónde está la base · ramas abiertas · ¿modelo y base divergen? | — |
| `alembic history` / `show <rev>` | La cadena completa · el detalle de una revisión | — |
| `alembic upgrade head` / `+1` | Aplicar todo / un paso | Aplica DDL |
| `alembic downgrade -1` / `base` | Deshacer un paso / todo | **Borra datos** |
| `alembic revision [--autogenerate] -m "..."` | Migración vacía / con las diferencias detectadas | — |
| `alembic stamp <rev>` | Mover el marcador **sin ejecutar DDL** | **Lo deja mintiendo si te equivocas** |
| `alembic merge -m "..." <r1> <r2>` | Unir dos heads | — |
| `docker compose down -v` | Parar y borrar los volúmenes | **Destruye la base local** |

## 12. Anatomía de una migración

`revision` es su id y `down_revision` de quién viene: esa referencia forma la cadena, y **el orden lo da
ella**, no el nombre ni la fecha del fichero. Dentro se usa `op`, que emite el DDL:
`create_table`/`drop_table`, `add_column`/`drop_column`, `alter_column`, `create_index`/`drop_index`,
`create_unique_constraint`/`create_check_constraint`/`create_foreign_key`, `rename_table`,
`bulk_insert` y `execute` para SQL a pelo. Las firmas, en la documentación de Alembic.

- **`op.f("...")`** marca un nombre como definitivo para que no se le reaplique la plantilla. Lo pone el
  autogenerate; respétalo.
- **`sa.text("...")`** es obligatorio en los `server_default`, o se guarda la cadena literal.
- **El orden importa**: Postgres no deja borrar `plans` mientras `users` la referencie, así que el
  `downgrade` es el `upgrade` leído del revés.
- **Sin formateo automático**: los `post_write_hooks` están comentados, así que los
  `### commands auto generated by Alembic ###` se quitan a mano.

## 13. Dónde el autogenerate se equivoca

**Cambio de tipo con conversión no automática** (`varchar`→`int` con valores sucios). Se limpia antes:

```python
op.execute("UPDATE users SET edad = NULL WHERE edad !~ '^[0-9]+$'")
op.alter_column("users", "edad", type_=sa.Integer, postgresql_using="edad::integer")
```

**No hace falta tabla de respaldo.** El patrón "crear tabla nueva, copiar, borrar la vieja, renombrar"
es de **SQLite**, que no sabe modificar una columna. Postgres convierte en el sitio, y si algún valor no
se puede convertir la migración falla entera y no se aplica nada.

**`CheckConstraint`** lleva siempre `name=`; al borrarla, el `drop_constraint` necesita `type_="check"`.
**Los índices parciales** no comparan `postgresql_where` de forma fiable, así que `alembic check` puede
dar OK aunque diverja. **Triggers, funciones y vistas** son invisibles: van con `op.execute()`.

**Migraciones de datos.** Solo mira estructura. Van aparte (regla 6 de
[§2](#2-reglas-que-no-se-negocian)): `alembic revision -m "..."` sin `--autogenerate` da el fichero
vacío, y dentro van `op.bulk_insert` o `op.execute`.

## 14. expand/contract

El único patrón que hace reversible un cambio con pérdida: la columna vieja es la copia de seguridad
hasta que decidas borrarla, en otra migración. En producción será obligatorio para cualquier cambio
incompatible.

```python
op.add_column("users", sa.Column("nif_nuevo", sa.String(20)))     # migración 1
op.execute("UPDATE users SET nif_nuevo = upper(trim(nif))")
# DESTRUCTIVE: elimina users.nif, ya migrado a nif_nuevo.         # migración 2, días después
op.drop_column("users", "nif")
```

## 15. Probar una migración sin riesgo

**1. Ver el SQL sin ejecutarlo:** `uv run alembic upgrade <current>:head --sql`. El rango no es opcional
en la práctica: sin él arranca desde `base` y vuelca todo el historial. Solo vale con `--sql`.

**2. Contra `db_test`**, que vive en tmpfs y es desechable. Cierra la terminal al terminar: mientras
`DATABASE_URL` valga eso, `pytest --test-alembic` se negará a arrancar, que es la salvaguarda del
`conftest.py` funcionando.

```powershell
docker compose up -d --wait db_test
$env:DATABASE_URL = "postgresql+psycopg://app:app@127.0.0.1:5433/administracion_test"
uv run alembic upgrade head
```

**3. Contra una copia de los datos reales.** Lo único que detecta lo que solo falla con filas dentro: un
NOT NULL incumplido, una conversión que revienta con un valor sucio, un UNIQUE ya duplicado. Saca la
copia como en [§16](#16-copia-de-seguridad-y-restauración) y métela **en `db_test`, no en `db`**:

```powershell
docker compose cp .\backup.dump db_test:/tmp/copia.dump
docker compose exec db_test pg_restore -U app -d administracion_test --clean --if-exists /tmp/copia.dump
# y migrar con DATABASE_URL apuntando a 5433, como en el punto 2
```

## 16. Copia de seguridad y restauración

```powershell
docker compose exec db pg_dump -U app -d administracion -Fc -f /tmp/backup.dump
docker compose cp db:/tmp/backup.dump .\backup.dump
docker compose cp .\backup.dump db:/tmp/backup.dump
docker compose exec db pg_restore -U app -d administracion --clean --if-exists /tmp/backup.dump
```

Restaura siempre entera: por tablas sueltas no se comprueban las FK de las demás, y quedan referencias
a filas que ya no existen. **No hay backups automatizados**: hoy la copia la haces tú.

## 17. Tests de migraciones

```powershell
docker compose up -d --wait          # los tests EXIGEN las bases levantadas
uv run pytest --test-alembic
```

`pytest-alembic` comprueba que hay un solo head, que la cadena sube desde cero, que el modelo coincide
con el DDL resultante y que **todos los `downgrade` funcionan**. Sin el flag no se ejecuta ninguno y la
suite da verde igualmente; el CI sí lo pasa.

Corren contra `db_test` (5433), **nunca** contra desarrollo: el test de ida y vuelta hace `downgrade`
hasta base. Dos salvaguardas lo impiden: `alembic_engine` aborta si `TEST_DATABASE_URL` coincide con
`DATABASE_URL`, y `env.py` usa la conexión que le inyecta pytest. (`test_health_db.py` es la excepción:
apunta a `DATABASE_URL`.)

> **El agujero:** esa comparación es por igualdad exacta de cadena. Dos URLs distintas apuntando a la
> misma base (`localhost` frente a `127.0.0.1`) la burlan, y el `downgrade base` cae sobre tu base de
> trabajo. Otra razón para la regla 8 de [§2](#2-reglas-que-no-se-negocian).

## 18. Dos heads

Dos ramas partieron de la misma revisión, así que sus migraciones comparten `down_revision`. Git las
mergea sin protestar —los ficheros no se tocan entre sí— y la cadena queda con dos finales. Se arregla
con `alembic merge`, que crea una revisión de unión sin DDL. Se evita con la regla 4 de
[§2](#2-reglas-que-no-se-negocian).

## 19. Qué hace el CI con tu PR

Solo se dispara `on: pull_request`. Un commit directo a `main` no pasa por aquí.

| Paso | Qué has hecho mal si falla |
|---|---|
| `uv sync --locked` | Tocaste `pyproject.toml` sin regenerar `uv.lock` |
| `check_destructive_migrations.py` (estático, falla en segundos) | Un `upgrade()` borra datos sin marca ([§7](#7-cómo-funciona--destructive)) |
| `alembic upgrade head` | La migración no aplica sobre una base limpia |
| `alembic check` | Cambiaste una entidad y no generaste su migración |
| `pytest --test-alembic` | Un test rojo, o un `downgrade` que no deshace |

Las migraciones se aplican contra `db` (5432) y los tests de migración contra `db_test` (5433). Los
tests corren con `continue-on-error` para que el log se suba siempre como artefacto y un paso posterior
falle el job; ese paso va con `shell: bash` a propósito, porque sin `pipefail` el código de salida sería
el del `tee` y **un test roto pasaría en verde**.
