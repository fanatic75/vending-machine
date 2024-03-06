from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Row, Sequence
from src.app.products.product_schema import (
    DeletedProductResponse,
    ProductCreate,
    Product as Productout,
    ProductInfo,
    ProductsBuyQueryResponse,
    ProductsBuyResponse,
)

from src.app.users.user_schema import (
    TokenData,
)
from src.app.products.products_service import *
from src.app.users.auth import RoleChecker
from src.core.db import get_db

router = APIRouter()


@router.post("/", response_model=Productout)
def create(
    product: ProductCreate,
    user: Annotated[TokenData, Depends(RoleChecker(allowed_roles=["seller"]))],
    db: Session = Depends(get_db),
):
  return add_product(product, user.id, db)


@router.get("/buy/{product_id}", response_model=ProductsBuyResponse)
async def buy(
    product_id: int,
    quantity: str,
    user: Annotated[TokenData, Depends(RoleChecker(allowed_roles=["buyer"]))],
    db: Session = Depends(get_db),
):

    quantity = int(quantity)
    products = buy_product(product_id, quantity, user.id, db)
    if not products:
        raise HTTPException(
            status_code=404, detail="Product not found or insufficient balance"
        )
    productsInfo = []
    for product in products:
        product = product._mapping
        productInfo = ProductInfo(
            id=product.id,
            title=product.title,
            price=product.price,
            description=product.description,
            total_spent_on_product=product.total_spent_on_product,
            total_quantity_bought=product.total_quantity_bought,
        )
        productsInfo.append(productInfo)
    product = products[0]._mapping
    return ProductsBuyResponse(
        user_id=product.user_id,
        username=product.username,
        balance=product.balance,
        products=productsInfo,
    )


@router.get("/available-products", response_model=List[Productout])
def get_available(
    pagenum: int = 1,
    db: Session = Depends(get_db),
):

    return get_all_available_products(pagenum, db)


@router.get("/{product_id}", response_model=Productout)
def get_by_id(
    product_id: int,
    db: Session = Depends(get_db),
):

    product = get_product_by_id(product_id, db)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@router.patch("/{product_id}", response_model=Productout)
def update(
    product_id: int,
    product: ProductUpdateBody,
    user: Annotated[TokenData, Depends(RoleChecker(allowed_roles=["seller"]))],
    db: Session = Depends(get_db),
):

    existing_product = get_product_by_id(product_id, db)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if existing_product.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Product not found")
    rows = update_product(product_id, product, db)
    if rows is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return get_product_by_id(product_id, db)

@router.delete("/{product_id}", response_model=DeletedProductResponse)
def delete(
    product_id: int,
    user: Annotated[TokenData, Depends(RoleChecker(allowed_roles=["seller"]))],
    db: Session = Depends(get_db),
):

    existing_product = get_product_by_id(product_id, db)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if existing_product.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Product not found")
    productDeleted = delete_product(product_id, db)
    if productDeleted:
        return DeletedProductResponse(message="Product deleted")
    raise HTTPException(status_code=404, detail="Product not found")
