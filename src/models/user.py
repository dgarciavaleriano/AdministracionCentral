from pydantic import BaseModel, EmailStr
from user_status import UserStatus
from invalid_user_status_transition_exception import InvalidUserStatusTransition

class User:
    _user_id: str
    _username: str
    _password_hash: str
    _display_name: str
    _email: str
    _status: UserStatus

    def __init__(
            self,
            some_user_id: str,
            some_username: str,
            some_password_hash: str,
            some_display_name: str,
            some_email: str,
            some_status: UserStatus
        ):
        self._user_id = some_user_id

        self._guard_username(some_username=some_username)
        self._username = some_username

        self._password_hash = some_password_hash

        self._guard_display_name(some_display_name=some_display_name)
        self._display_name = some_display_name

        self._guard_email(some_email=some_email)
        self._email = some_email

        self._

    def _guard_username(self, some_username: str):
        if some_username.strip() == "":
            raise ValueError("El nombre de usuario no puede estar vacío")

    def _guard_display_name(self, some_display_name: str):
            if some_display_name.strip() == "":
                raise ValueError("El nombre para mostrar del usuario no puede estar vacío")

    def _guard_email(self, some_email: str):
        if "@" not in some_email:
            raise ValueError("Email con formato erróneo")

    def _guard_status(self, some_status: UserStatus):
        if not self._status.can_transition_to(some_status):
            raise InvalidUserStatusTransition(self._status, some_status)
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self._user_id == other._user_id

    def __hash__(self) -> int:
        return hash(self._user_id)

    def __repr__(self):
        return f"User(user_id={self._user_id!r}, username={self._username!r}, display_name={self._display_name!r}, email={self.email!r})"

    def change_password(self, some_password_hash: str):
        self._password_hash = some_password_hash

    def change_display_name(self, some_display_name: str):
        self._display_name = some_display_name
        return

    def change_email(self, some_email: str):
        self._guard_email(some_email=some_email)
        self.email = some_email

class UserCreate(BaseModel):
    username: str
    password_hash: str

class UserPut(BaseModel):
    user_id: str
    username: str
    password_hash: str
    display_name: str
    email: EmailStr

class UserPatch(BaseModel):
    user_id: str
    username: str
    password_hash: str
    display_name: str
    email: EmailStr
