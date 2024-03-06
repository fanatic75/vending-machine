from sqlalchemy.orm import Session

from src.app.users.user_schema import UserCreate
from src.app.users.auth import get_password_hash
from src.core.models import User

def add_user(user: UserCreate, db: Session):
  user = User(username=user.username, password=get_password_hash(user.password), role=user.role.value)
  db.add(user)
  db.commit()
  db.refresh(user)
  return user

def get_user(id: int, db: Session):
  return db.query(User).filter(User.id == id).first()

def get_user_by_username(username: str, db: Session):
  return db.query(User).filter(User.username == username).first()

def add_amount(id: int, amount: int, db: Session):
  rowsUpdated = db.query(User).filter(User.id == id).update({User.balance: User.balance + amount})
  if rowsUpdated == 0:
    return None
  db.commit()
  return rowsUpdated

def reset_amount(id: int, db: Session):
  rowsUpdated = db.query(User).filter(User.id == id).update({User.balance: 0})
  if rowsUpdated == 0:
    return None
  db.commit()
  return rowsUpdated

def update_user(id: int, new_username: str, new_password: str, db: Session):
    update_data = {}
    
    if new_username:
        update_data[User.username] = new_username
    if new_password:
        update_data[User.password] = get_password_hash(new_password)
    
    rows_updated = db.query(User).filter(User.id == id).update(update_data)
    
    if rows_updated == 0:
        return None
    
    db.commit()
    return rows_updated

def delete_user(id: int, db: Session):
  user = db.query(User).filter(User.id == id).first()
  if user:
    db.delete(user)
    db.commit()
    return True
  return None