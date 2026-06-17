from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Permission ──────────────────────────────────────────────────────────────
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: int

    class Config:
        from_attributes = True


# ── Role ────────────────────────────────────────────────────────────────────
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleRead(RoleBase):
    id: int
    permissions: List[PermissionRead] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ── User ────────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    roles: List[RoleRead] = []

    class Config:
        from_attributes = True


class AssignRole(BaseModel):
    user_id: int
    role_id: int


# ── Token ───────────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
