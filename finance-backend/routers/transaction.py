from  datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from middleware.access_control import get_current_user, require_role
from models.transaction import TransactionType
from models.user import User, UserRole
from schemas.transaction import TransactionCreate, TransactionFilters, TransactionOut, TransactionUpdate
from services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/",
    response_model=TransactionOut,
    status_code=201,
    summary="Create a transaction",
    description="Create a new income or expense record. Admin only.",
)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
):
    return transaction_service.create_transaction(data, current_user.id, db)


@router.get(
    "/",
    response_model=list[TransactionOut],
    summary="List transactions",
    description=(
        "Returns all non-deleted transactions. "
        "Supports optional filters: type, category, date_from, date_to. "
        "Accessible to all authenticated roles."
    ),
)
def list_transactions(
    type: TransactionType | None = Query(None, description="Filter by income or expense"),
    category: str | None = Query(None, description="Partial, case-insensitive category match"),
    date_from: datetime | None = Query(None, description="Include records on or after this date"),
    date_to: datetime | None = Query(None, description="Include records on or before this date"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),  # viewer, analyst, admin all allowed
):
    filters = TransactionFilters(type=type, category=category, date_from=date_from, date_to=date_to)
    return transaction_service.list_transactions(filters, db)


@router.get(
    "/{tx_id}",
    response_model=TransactionOut,
    summary="Get a transaction",
    description="Fetch a single transaction by ID. All authenticated roles.",
)
def get_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return transaction_service.get_transaction(tx_id, db)


@router.patch(
    "/{tx_id}",
    response_model=TransactionOut,
    summary="Update a transaction",
    description="Update any field on a transaction. Admin only.",
)
def update_transaction(
    tx_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    return transaction_service.update_transaction(tx_id, data, db)


@router.delete(
    "/{tx_id}",
    status_code=204,
    summary="Delete a transaction",
    description="Soft-deletes a transaction (sets is_deleted=True). Admin only.",
)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    transaction_service.soft_delete_transaction(tx_id, db)
