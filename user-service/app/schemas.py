from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)