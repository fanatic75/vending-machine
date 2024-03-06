from enum import Enum
from typing import Annotated, Union

from pydantic import BaseModel, validator

from src.app.products.product_schema import Product
from src.app.util.validator import CoinsValidation


class Role(Enum):
    buyer = "buyer"
    seller = "seller"


class UserBase(BaseModel):
    username: str
    role: Role = Role.buyer


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    balance: int = 0
    products: list[Product] = []

    class Config:
        orm_mode = True


class UpdateUserBody(BaseModel):
    new_username: Union[str, None] = None
    new_password: Union[str, None] = None


class NewUserResponse(BaseModel):
    access_token: str
    user: Annotated[User, "User object associated with the token"]


class DeletedUserResponse(BaseModel):
    message: str

class TokenData(UserBase):
    id: int

class LoginBody(BaseModel):
    username: str
    password: str