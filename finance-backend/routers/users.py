from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from middleware.access_control import get_current_user, require_role
from models.user import User, UserRole
from schemas.user import UserOut, UserUpdate
from services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get my profile",
    description="Returns the currently authenticated user's profile. All roles.",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get(
    "/",
    response_model=list[UserOut],
    summary="List all users",
    description="Returns all users in the system. Admin only.",
)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.list_users(db)


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get a user by ID",
    description="Fetch a single user by their ID. Admin only.",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.get_user_or_404(user_id, db)


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Update a user",
    description="Update a user's name, role, or active status. Admin only.",
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return user_service.update_user(user_id, data, db)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete a user",
    description="Permanently delete a user. Admin only. Cannot delete your own account.",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    user_service.delete_user(user_id, current_user.id, db)
