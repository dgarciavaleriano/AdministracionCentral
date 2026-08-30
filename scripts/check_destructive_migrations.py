"""Falla si una migración destruye datos en `upgrade()` sin marcarlo.

Solo mira `upgrade()`: los `drop_table` de `downgrade()` son el inverso normal de un
`create_table`, y marcarlos entrenaría a poner la marca en todas partes.

Uso:  python scripts/check_destructive_migrations.py
"""

import ast
import io
import re
import sys
from pathlib import Path

VERSIONS = Path(__file__).resolve().parents[1] / "migrations" / "versions"
OPERACIONES_DESTRUCTIVAS = {"drop_table", "drop_column"}
SQL_DESTRUCTIVO = re.compile(r"\b(DELETE|TRUNCATE|DROP)\b", re.IGNORECASE)
MARCA = "# DESTRUCTIVE:"


def operaciones_destructivas(funcion: ast.FunctionDef) -> set[str]:
    encontradas: set[str] = set()

    for nodo in ast.walk(funcion):
        if not isinstance(nodo, ast.Call) or not isinstance(nodo.func, ast.Attribute):
            continue

        if nodo.func.attr in OPERACIONES_DESTRUCTIVAS:
            encontradas.add(f"op.{nodo.func.attr}")
        elif nodo.func.attr == "execute":
            for argumento in nodo.args:
                if isinstance(argumento, ast.Constant) and isinstance(argumento.value, str):
                    if SQL_DESTRUCTIVO.search(argumento.value):
                        encontradas.add("op.execute con SQL destructivo")

    return encontradas


def main() -> int:
    # El isinstance no es adorno: stderr puede estar redirigido a algo sin reconfigure.
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")

    problemas: list[tuple[str, set[str]]] = []

    for fichero in sorted(VERSIONS.glob("*.py")):
        fuente = fichero.read_text(encoding="utf-8")
        if MARCA in fuente:
            continue

        for nodo in ast.parse(fuente, filename=str(fichero)).body:
            if isinstance(nodo, ast.FunctionDef) and nodo.name == "upgrade":
                if operaciones := operaciones_destructivas(nodo):
                    problemas.append((fichero.name, operaciones))

    if not problemas:
        return 0

    print("Migraciones que destruyen datos sin marcar:\n", file=sys.stderr)
    for nombre, operaciones in problemas:
        print(f"  migrations/versions/{nombre}", file=sys.stderr)
        print(f"    upgrade() usa: {', '.join(sorted(operaciones))}", file=sys.stderr)
    print(
        "\nAñade en el upgrade() un comentario `# DESTRUCTIVE:` explicando qué se pierde,\n"
        "y haz copia antes de aplicarla:\n"
        "  docker compose exec db pg_dump -U app -d administracion -Fc -f /tmp/backup.dump",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
