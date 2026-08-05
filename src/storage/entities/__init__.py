"""Cada entidad nueva, una línea más aquí.

Alembic solo ve las tablas cuyas clases se hayan importado: si falta una, el
autogenerate produce una migración vacía sin avisar.
"""

from storage.entities.plan import Plan
from storage.entities.user import User

__all__ = ["Plan", "User"]
