from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from models.user import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.viewer

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if (len(v) < 8):
            raise ValueError("Password must be at least 8 characters long")
        return v

class UserUpdate(BaseModel):
    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
