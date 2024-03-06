from typing import Union

from pydantic import BaseModel, validator

from src.app.util.validator import CoinsValidation


class ProductsBase(BaseModel):
    title: str
    price: int
    description: Union[str, None] = None
    quantity: int = 1

    @validator("price")
    def validate_balance(cls, v):
        CoinsValidation(denomination=v)
        return v


class ProductCreate(ProductsBase):
    pass


class Product(ProductsBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class ProductUpdateBody(BaseModel):
    title: Union[str, None] = None
    price: Union[int, None] = None
    description: Union[str, None] = None
    quantity: Union[int, None] = None


class ProductsBuyQueryResponse(BaseModel):
    id: int
    title: str
    price: int
    total_spent_on_product: int
    total_quantity_bought: int
    balance: int
    username: str
    user_id: int
    description: Union[str, None] = None

class ProductInfo(BaseModel):
    id: int
    title: str
    price: int
    description: Union[str, None] = None
    total_spent_on_product: int
    total_quantity_bought: int

class ProductsBuyResponse(BaseModel):
    user_id: int
    username: str
    balance: int
    products: list[ProductInfo]

class DeletedProductResponse(BaseModel):
    message: str