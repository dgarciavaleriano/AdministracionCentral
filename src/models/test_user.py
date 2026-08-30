import pytest

from user import User
from user_status import UserStatus

from invalid_user_status_transition_exception import InvalidUserStatusTransition

from uuid import UUID, uuid4, uuid5
from datetime import datetime, timezone

class UserMother:
    """Object Mother: instancias canónicas de User para los tests."""

    USERNAME = "bruce.wayne"
    PASSWORD_HASH = "$2y$12$yQ7fXKtR3mLpZs2vBnW9uOe5c8DkT1jV6bHqA4wRxYzP0gLmNsCiU"
    DISPLAY_NAME = "Batman"
    EMAIL = "batman@gotham.com"
    CREATED_AT = datetime(2026, 5, 19, 12, 0, 0, tzinfo=timezone.utc)

    # Constructor interno con overrides ----------------------------------------

    @classmethod
    def _create(
        cls,
        *,
        user_id: UUID | None = None,
        username: str | None = None,
        password_hash: str | None = None,
        display_name: str | None = None,
        email: str | None = None,
        status: UserStatus | None = None,
        created_at: datetime | None = None,
    ) -> User:
        return User(
            user_id=user_id if user_id is not None else uuid4(),
            username=username if username is not None else cls.USERNAME,
            password_hash=password_hash if password_hash is not None else cls.PASSWORD_HASH,
            display_name=display_name if display_name is not None else cls.DISPLAY_NAME,
            email=email if email is not None else cls.EMAIL,
            status=status if status is not None else UserStatus.ACTIVE,
            created_at=created_at if created_at is not None else cls.CREATED_AT,
        )

    @classmethod
    def registered(cls) -> User:
        """Pasa por la factoría de dominio, no por el constructor."""
        return User.register(
            username=cls.USERNAME,
            password_hash=cls.PASSWORD_HASH,
            display_name=cls.DISPLAY_NAME,
            email=cls.EMAIL,
        )

    @classmethod
    def with_id(cls, user_id: UUID) -> User:
        return cls._create(user_id=user_id)

    @classmethod
    def twin_of(cls, user: User) -> User:
        """Mismo user_id, datos distintos: para probar la identidad del aggregate."""
        return cls._create(
            user_id=user.user_id,
            username="otro_username",
            email="otro@example.com",
        )

    @classmethod
    def with_username(cls, username: str) -> User:
        return cls._create(username=username)

    @classmethod
    def with_display_name(cls, display_name: str) -> User:
        return cls._create(display_name=display_name)

    @classmethod
    def with_password_hash(cls, password_hash: str) -> User:
        return cls._create(password_hash=password_hash)

    @classmethod
    def with_email(cls, email: str) -> User:
        return cls._create(email=email)

    @classmethod
    def active(cls) -> User:
        return cls._create(status=UserStatus.ACTIVE)

    @classmethod
    def suspended(cls) -> User:
        return cls._create(status=UserStatus.SUSPENDED)

    @classmethod
    def deactivated(cls) -> User:
        return cls._create(status=UserStatus.DEACTIVATED)

def test_user_has_valid_user_id():
    user = UserMother.active()
    assert isinstance(user.user_id, UUID), f"user_id no es UUID: {type(user.user_id)}"
    assert user.user_id.version == 4, f"UUID versión {user.user_id.version}, esperada 4"

def test_invalid_uuid_version_id_raises_error():
    with pytest.raises(TypeError):
        user = UserMother.with_id(uuid5())

def test_empty_username_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_username("")

def test_short_username_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_username("Ap")

def test_empty_display_name_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_display_name("")

def test_short_display_name_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_display_name("Ap")

def test_empty_password_hash_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_password_hash("")

def test_empty_email_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_email("")

def test_email_length_greater_than_254_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_email("hola@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.com")

def test_invalid_email_raises_error():
    with pytest.raises(ValueError):
        user = UserMother.with_email("hola")

def test_invalid_status_transition_raises_error():
    with pytest.raises(InvalidUserStatusTransition):
        user = UserMother.active()
        user.change_status_to(UserStatus.ACTIVE)