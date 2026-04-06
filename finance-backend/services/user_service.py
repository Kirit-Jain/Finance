from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserCreate, UserUpdate

def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()

def get_user(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def update_user(user_id: int, data: UserUpdate, db: Session) -> User:
    user = get_user(user_id, db)

    updated_data = data.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

def delete_user(user_id: int, requesting_user_id: int, db: Session) -> None:
    user = get_user(user_id, db)

    if user.id == requesting_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Users cannot delete themselves")
    
    db.delete(user)
    db.commit()
