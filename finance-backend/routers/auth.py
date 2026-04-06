from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.auth import LoginRequest, TokenResponse
from schemas.user import UserCreate, UserOut
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Register a new user",
    description="Create a new user account. Role defaults to 'viewer', unless specified otherwise.",
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(data, db)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate a user and return an access token.",
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login_user(data.email, data.password, db)
    return TokenResponse(access_token=token)