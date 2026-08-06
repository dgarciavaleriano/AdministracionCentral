# AdministracionCentral
Proyecto Jupiter - Administración Central

## Arranque

```powershell
Copy-Item .env.example .env     # opcional: todo tiene valor por defecto
docker compose up -d --wait
uv sync
uv run alembic upgrade head
uv run python src/main.py
```

## Documentación

- [Modelo de datos](docs/modelo-de-datos.md) — esquema, decisiones y cómo funciona la capa de persistencia.
- [Migraciones](migrations/README.md) — cómo trabajar con Alembic: flujo, comandos y cómo escribir una migración.
