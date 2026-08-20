from pydantic import BaseModel, EmailStr, Field

from shared.password_hashing import Password

_MINIMUM_PASSWORD_LENGTH = 4


class UserCreate(BaseModel):
    username: str
    email: str
    password: Password


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: Password = Field(
        ..., min_length=_MINIMUM_PASSWORD_LENGTH
    )
