from sqlalchemy.orm import Session

from src.app.users.user_schema import UserCreate
from src.app.users.auth import get_password_hash
from src.core.models import User

def add_user(user: UserCreate, db: Session):
    try:
        user = User(
            username=user.username,
            password=get_password_hash(user.password),
            role=user.role.value,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except:
        return None


def get_user(id: int, db: Session):
    try:
        return db.query(User).filter(User.id == id).first()
    except:
        return None


def get_user_by_username(username: str, db: Session):
    try:
        return db.query(User).filter(User.username == username).first()
    except:
        return None


def add_amount(id: int, amount: int, db: Session):
    try:
        rowsUpdated = (
            db.query(User)
            .filter(User.id == id)
            .update({User.balance: User.balance + amount})
        )
        if rowsUpdated == 0:
            return None
        db.commit()
        return rowsUpdated
    except:
        return None


def reset_amount(id: int, db: Session):
    try:
        rowsUpdated = db.query(User).filter(User.id == id).update({User.balance: 0})
        if rowsUpdated == 0:
            return None
        db.commit()
        return rowsUpdated
    except:
        return None


def update_user(id: int, new_username: str, new_password: str, db: Session):
    update_data = {}

    if new_username:
        update_data[User.username] = new_username
    if new_password:
        update_data[User.password] = get_password_hash(new_password)

    try:
        rows_updated = db.query(User).filter(User.id == id).update(update_data)

        if rows_updated == 0:
            return None

        db.commit()
        return rows_updated
    except:
        return None


def delete_user(id: int, db: Session):
    try:
        user = db.query(User).filter(User.id == id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return None
    except:
        return None
