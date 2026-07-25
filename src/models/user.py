from pydantic import BaseModel, EmailStr

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
