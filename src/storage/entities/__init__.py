# Cada tabla nueva se importa aquí: así Base la conoce y create_all la crea.
from storage.entities.plan import Plan
from storage.entities.user import User

__all__ = ["Plan", "User"]
