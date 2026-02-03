import uuid

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=128)


class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    id: uuid.UUID


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
