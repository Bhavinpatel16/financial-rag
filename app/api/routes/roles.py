from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.user import Role, Permission, User
from app.schemas.user import RoleCreate, RoleRead, AssignRole, UserRead
from app.core.security import get_current_user

router = APIRouter(tags=["Roles & Permissions"])


@router.post("/roles/create", response_model=RoleRead, status_code=201)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new role (Admin only)."""
    _require_admin(current_user)

    if db.query(Role).filter(Role.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Role(name=payload.name, description=payload.description)

    if payload.permission_ids:
        perms = db.query(Permission).filter(Permission.id.in_(payload.permission_ids)).all()
        role.permissions = perms

    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/roles", response_model=List[RoleRead])
def list_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Role).all()


@router.post("/users/assign-role", response_model=UserRead)
def assign_role(
    payload: AssignRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign a role to a user (Admin only)."""
    _require_admin(current_user)

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)

    return user


@router.get("/users/{user_id}/roles", response_model=List[RoleRead])
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.roles


@router.get("/users/{user_id}/permissions")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    permissions = {}
    for role in user.roles:
        for perm in role.permissions:
            permissions[perm.name] = perm.description

    return {"user_id": user_id, "username": user.username, "permissions": permissions}


def _require_admin(user: User):
    role_names = [r.name.lower() for r in user.roles]
    if "admin" not in role_names:
        raise HTTPException(status_code=403, detail="Admin role required")
