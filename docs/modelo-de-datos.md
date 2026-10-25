# Modelo de datos

Las tablas se definen con SQLAlchemy en `src/storage/entities/`, una clase por tabla. Se crean y se cambian con migraciones de Alembic (`migrations/versions/`).

## Tablas

### `plans`

Planes de suscripción y sus límites de uso.

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID | Clave primaria |
| `name` | texto | Único |
| `max_drafts` | entero | Borradores de declaración permitidos |
| `max_sessions_per_day` | entero | |
| `history_retention_days` | entero | Días que se guarda el historial |
| `is_active` | booleano | Por defecto `true` |
| `created_at` | fecha y hora | La pone la base de datos |

### `users`

| Columna | Tipo | Notas |
|---|---|---|
| `id` | UUID | Clave primaria |
| `name`, `surname_1` | texto | Obligatorios |
| `surname_2` | texto | Opcional (hay extranjeros sin segundo apellido) |
| `nif` | texto | Único. NIF o NIE, todavía sin validar |
| `birthdate` | fecha | |
| `marital_status` | texto | Opcional |
| `email` | texto | Único |
| `email_verified` | booleano | Por defecto `false` |
| `phone`, `fiscal_address` | texto | Opcionales |
| `password_hash` | texto | Nunca se guarda la contraseña en claro |
| `status` | texto | Por defecto `active` |
| `plan_id` | UUID | Plan del usuario (`plans.id`). Opcional mientras no haya planes creados |
| `created_at`, `updated_at` | fecha y hora | Los pone la base de datos |

## Decisiones

| Decisión | Motivo |
|---|---|
| PostgreSQL y no MongoDB | Datos fiscales con muchas relaciones (usuario, documentos, trámites). Se puede replicar en cualquier cloud (tutoría del 21-07) |
| `id` UUID y no autoincremental | No revela cuántos usuarios hay ni permite ir probando ids |
| Fechas con zona horaria | Si no, la hora guardada depende de la zona de quien la inserta |
| Sin orientación sexual | Es un dato especialmente protegido por el RGPD (art. 9). Decisión de equipo |

## Cambiar una tabla

1. Edita (o crea) la clase en `src/storage/entities/`. Si es una tabla nueva, impórtala en `src/storage/entities/__init__.py`.
2. Genera la migración, revísala y aplícala:

   ```powershell
   uv run python -m alembic revision --autogenerate -m "descripción del cambio"
   uv run python -m alembic upgrade head
   ```

3. Sube el fichero de `migrations/versions/` en la misma PR que el cambio de la clase.

Más detalle en la sección *Migraciones* del [README](../README.md).
