"""Pydantic schemas for auth and user administration."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ActionOut(BaseModel):
    code: str
    description: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    is_active: bool
    actions: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    is_admin: bool = False
    actions: list[str] = Field(default_factory=list)


class UpdateUserActionsRequest(BaseModel):
    actions: list[str]


class UpdateUserRequest(BaseModel):
    is_active: bool | None = None
    is_admin: bool | None = None
    password: str | None = Field(default=None, min_length=6)
