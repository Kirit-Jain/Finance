from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.transaction import Transaction
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionFilters

def create_transaction(data: TransactionCreate, created_by: int, db: Session) -> Transaction:
    tx = Transaction(**data.model_dump(), created_by=created_by)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def list_transactions(filters: TransactionFilters, db: Session) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.is_deleted == False)

    if filters.type:
        query = query.filter(Transaction.type == filters.type)
    if filters.category:
        query = query.filter(Transaction.category.ilike(f"%{filters.category}%"))
    if filters.date_from:
        query = query.filter(Transaction.date >= filters.date_from)
    if filters.date_to:
        query = query.filter(Transaction.date <= filters.date_to)

    return query.order_by(Transaction.date.desc()).all()

def get_transaction(tx_id: int, db: Session) -> Transaction:
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.is_deleted == False).first()
    
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {tx_id} not found"
        )
    
    return tx

def update_transaction(tx_id: int, data: TransactionUpdate, db: Session) -> Transaction:
    tx = get_transaction(tx_id, db)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)

    tx.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(tx)
    return tx

def soft_delete_transaction(tx_id: int, db: Session) -> None:
    tx = get_transaction(tx_id, db)
    tx.is_deleted = True
    tx.updated_at = datetime.now(timezone.utc)
    db.commit()
