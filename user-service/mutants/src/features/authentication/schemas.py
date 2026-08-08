from pydantic import BaseModel, EmailStr, Field

_MINIMUM_PASSWORD_LENGTH = 4


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


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
    password: str = Field(..., min_length=_MINIMUM_PASSWORD_LENGTH)
