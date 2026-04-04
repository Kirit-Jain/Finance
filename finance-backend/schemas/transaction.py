from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from models.transaction import TransactionType

class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: datetime
    note: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be empty")
        return v.strip
    
class TransactionUpdate(BaseModel):
    amount: float | None = None
    type: TransactionType | None = None
    category: str | None = None
    date: datetime | None = None
    notes: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v is not None and v <= 0:
            raise ValueError("Amount must be positive")
        return v

class TransactionOut(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: datetime
    note: str | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TransactionFilters(BaseModel):
    type: TransactionType | None = None
    category: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    