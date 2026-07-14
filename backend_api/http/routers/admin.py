"""Admin routes for managing users and actions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend_api.db.models import Action, User
from backend_api.db.session import get_db
from backend_api.http.dependencies import require_admin
from backend_api.http.schemas.auth import (
    ActionOut,
    CreateUserRequest,
    UpdateUserActionsRequest,
    UpdateUserRequest,
    UserOut,
)
from backend_api.http.services.auth_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    hash_password,
    set_user_actions,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        is_active=user.is_active,
        actions=user.action_codes(),
        created_at=user.created_at,
    )


@router.get("/actions", response_model=list[ActionOut])
def list_actions(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[ActionOut]:
    actions = db.query(Action).order_by(Action.code).all()
    return [ActionOut(code=a.code, description=a.description) for a in actions]


@router.get("/users", response_model=list[UserOut])
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    users = db.query(User).order_by(User.email).all()
    return [_user_out(user) for user in users]


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    request: CreateUserRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserOut:
    if get_user_by_email(db, request.email) is not None:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(
        db,
        email=request.email,
        password=request.password,
        action_codes=request.actions,
        is_admin=request.is_admin,
    )
    return _user_out(user)


@router.put("/users/{user_id}/actions", response_model=UserOut)
def update_user_actions(
    user_id: int,
    request: UpdateUserActionsRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserOut:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user = set_user_actions(db, user, request.actions)
    return _user_out(user)


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserOut:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.is_admin is not None:
        user.is_admin = request.is_admin
    if request.password is not None:
        user.password_hash = hash_password(request.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_out(user)
