from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.app.users.user_schema import (
    UpdateUserBody,
    User as Userout,
    UserCreate,
    NewUserResponse,
    DeletedUserResponse,
    TokenData,
    LoginBody
)
from src.app.users.user_service import *
from src.app.users.auth import (
    RoleChecker,
    create_token,
    validate_user,
    authenticate_user,
)
from src.app.util.validator import CoinsValidation
from src.core.db import get_db

router = APIRouter()


@router.post("/", response_model=Userout)
def create(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_username(user.username, db)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = add_user(user, db)
    if user:
        return user
    raise HTTPException(500, detail="Error while creating user")


@router.post("/login", response_model=NewUserResponse)
def login(
    login_body: LoginBody,
    db: Session = Depends(get_db),
):
    user = get_user_by_username(login_body.username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not authenticate_user(login_body.password, user):
        raise HTTPException(status_code=404, detail="Invalid username or password")
    token = create_token({"sub": user.username, "role": user.role, "id": user.id})
    return {"access_token": token, "user": user}


@router.get("/", response_model=Userout)
def get(
    user: Annotated[TokenData, Depends(validate_user)], db: Session = Depends(get_db)
):

    user = get_user(user.id, db)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.patch("/", response_model=Userout)
def update(
    user: Annotated[User, Depends(validate_user)],
    update_data: UpdateUserBody,
    db: Session = Depends(get_db),
):
    new_username = update_data.new_username
    new_password = update_data.new_password

    userUpdated = update_user(user.id, new_username, new_password, db)
    if userUpdated > 0:
        if new_username:
            user.username = new_username
        if new_password:
            user.password = new_password
        return get_user(user.id, db)
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/deposit", response_model=Userout)
def deposit(
    user: Annotated[TokenData, Depends(RoleChecker(allowed_roles=["buyer"]))],
    amount: CoinsValidation,
    db: Session = Depends(get_db),
):

    rowsUpdated = add_amount(user.id, amount.denomination, db)
    if rowsUpdated > 0:
        return get_user(user.id, db)
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/login-by-form", response_model=NewUserResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = get_user_by_username(form_data.username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not authenticate_user(form_data.password, user):
        raise HTTPException(status_code=404, detail="Invalid username or password")
    token = create_token({"sub": user.username, "role": user.role, "id": user.id})
    return {"access_token": token, "user": user}


@router.post("/reset", response_model=Userout)
def reset(
    user: Annotated[TokenData, Depends(RoleChecker(allowed_roles=["buyer"]))],
    db: Session = Depends(get_db),
):

    rowsUpdated = reset_amount(user.id, db)
    if rowsUpdated > 0:
        return get_user(user.id, db)
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/", response_model=DeletedUserResponse)
def delete(
    user: Annotated[User, Depends(validate_user)],
    db: Session = Depends(get_db),
):

    userDeleted = delete_user(user.id, db)
    if userDeleted:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
