# Cada tabla nueva se importa aquí: así Base la conoce y Alembic la ve.
from storage.entities.plan import Plan
from storage.entities.user import User

__all__ = ["Plan", "User"]
