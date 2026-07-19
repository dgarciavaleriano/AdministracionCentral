from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
	username: str
    password_hash: str
