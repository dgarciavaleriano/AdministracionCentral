"""Registro de entidades.

Alembic solo ve las tablas cuyas clases se hayan importado: si falta una, no
entra en `Base.metadata` y el autogenerate no la propone. Si la migración
quedaría vacía, `env.py` aborta y avisa; pero si lleva cualquier otro cambio,
la tabla que falta se omite en silencio.
"""

from storage.entities.plan import Plan
from storage.entities.user import User

__all__ = ["Plan", "User"]
