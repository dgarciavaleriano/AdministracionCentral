from user_status import UserStatus
from invalid_user_status_transition_exception import InvalidUserStatusTransition

from uuid import UUID, uuid4
from datetime import datetime, timezone

import re

_EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s.]+$"
)

class User:
    """Aggregate root: identidad por user_id, invariantes garantizadas en construcción."""

    MIN_USERNAME_LENGTH = 3
    MIN_DISPLAY_NAME_LENGTH = 3

    def __init__(
            self,
            user_id: UUID,
            username: str,
            display_name: str,
            password_hash: str,
            email: str,
            status: UserStatus,
            created_at: datetime
        ) -> None:
        self._guard_user_id(user_id=user_id)
        self._guard_username(username=username)
        self._guard_display_name(display_name=display_name)
        self._guard_password_hash(password_hash=password_hash)
        self._guard_email(email=email)

        self._user_id = user_id
        self._username = username
        self._display_name = display_name
        self._password_hash = password_hash
        self._email = email
        self._status = status
        self._created_at = created_at

    # Factory ----------------------------------------

    @classmethod
    def register(
        cls,
        username: str,
        display_name: str,
        password_hash: str,
        email: str,
    ) -> User:
        return cls(
            user_id=uuid4(),
            username=username,
            display_name=display_name,
            password_hash=password_hash,
            email=email,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
        )

    # Invariants ----------------------------------------
    
    @staticmethod
    def _guard_user_id(user_id: UUID) -> None:
        if not isinstance(user_id, UUID):
            raise TypeError(
                f"El identificador de usuario debe ser un UUID, no {type(user_id).__name__}"
            )
        if user_id.version != 4:
            raise ValueError(
                f"El identificador de usuario debe ser un UUID v4, no v{user_id.version}"
            )
        
    @staticmethod
    def _guard_username(username: str) -> None:
        if not isinstance(username, str):
            raise TypeError(
                f"El nombre de usuario debe ser una cadena, no {type(username).__name__}"
            )

        candidate = username.strip()
        if len(candidate) < User.MIN_USERNAME_LENGTH:
            raise ValueError(
                f"El nombre de usuario debe tener al menos "
                f"{User.MIN_USERNAME_LENGTH} caracteres, tiene {len(candidate)}"
            )

    @staticmethod
    def _guard_display_name(display_name: str) -> None:
        if not isinstance(display_name, str):
            raise TypeError(
                f"El nombre para mostrar debe ser una cadena, no {type(display_name).__name__}"
            )

        candidate = display_name.strip()
        if len(candidate) < User.MIN_DISPLAY_NAME_LENGTH:
            raise ValueError(
                f"El nombre para mostrar debe tener al menos "
                f"{User.MIN_DISPLAY_NAME_LENGTH} caracteres, tiene {len(candidate)}"
            )

    @staticmethod
    def _guard_password_hash(password_hash: str) -> None:
        if not password_hash.strip():
            raise ValueError("El hash de la contraseña no puede estar vacío")

    @staticmethod
    def _guard_email(email: str) -> None:
        if not isinstance(email, str):
            raise TypeError(f"El email debe ser una cadena, no {type(email).__name__}")

        candidate = email.strip()
        if not candidate:
            raise ValueError("El email no puede estar vacío")
        if len(candidate) > 254:
            raise ValueError("El email excede la longitud máxima permitida")
        if not _EMAIL_PATTERN.match(candidate):
            raise ValueError(f"Email con formato erróneo: {email!r}")

    def _guard_status_transition(self, new_status: UserStatus) -> None:
        if not self._status.can_transition_to(new_status):
            raise InvalidUserStatusTransition(self._status, new_status)

    # Read ----------------------------------------
    
    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def email(self) -> str:
        return self._email

    @property
    def status(self) -> UserStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # Behaviour ----------------------------------------

    def change_password(self, password_hash: str) -> None:
        self._guard_password_hash(password_hash)
        self._password_hash = password_hash

    def change_display_name(self, display_name: str) -> None:
        self._guard_display_name(display_name)
        self._display_name = display_name

    def change_email(self, email: str) -> None:
        self._guard_email(email)
        self._email = email

    def change_status_to(self, status: UserStatus) -> None:
        self._guard_status_transition(status)
        self._status = status

    # Identity ----------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._user_id == other._user_id

    def __hash__(self) -> int:
        return hash(self._user_id)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"user_id={self._user_id!r}, "
            f"username={self._username!r}, "
            f"status={self._status.value!r}, "
            f"display_name={self._display_name!r}, "
            f"email={self._email!r})"
        )