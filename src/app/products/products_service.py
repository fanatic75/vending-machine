import asyncio
from typing import List
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.app.products.product_schema import (
    ProductCreate,
    ProductUpdateBody,
)
from src.core.models import Product, user_products
from src.app.users.user_service import get_user
from src.app.users.user_schema import User


def add_product(product: ProductCreate, owner_id: int, db: Session):
    try:
        product = Product(
            title=product.title,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            owner_id=owner_id,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception:
        db.rollback()
        raise HTTPException(400, "Error while creating product")


def get_all_available_products(pagenum: int, db: Session):
    limit = 20
    offset = (pagenum - 1) * limit
    try:
        return (
            db.query(Product)
            .filter(Product.quantity > 0)
            .offset(offset)
            .limit(limit)
            .all()
        )
    except Exception:
        raise HTTPException(400, "Error while fetching products")


def get_product_by_id(product_id: int, db: Session):
    try:
        return db.query(Product).filter(Product.id == product_id).first()
    except Exception:
        raise HTTPException(400, "Error while fetching product")


def update_product(product_id: int, product: ProductUpdateBody, db: Session):
    product_data = {}
    if product.title:
        product_data["title"] = product.title
    if product.price:
        product_data["price"] = product.price
    if product.description:
        product_data["description"] = product.description
    if product.quantity:
        product_data["quantity"] = product.quantity
    try:
        rowsUpdated = (
            db.query(Product).filter(Product.id == product_id).update(product_data)
        )
        if rowsUpdated == 0:
            return None
        db.commit()
        return rowsUpdated
    except Exception:
        db.rollback()
        raise HTTPException(400, "Error while updating product")


def buy_product(product_id: int, quantity: int, user_id: int, db: Session):
    try:
        product = get_product_by_id(product_id, db)
        user = get_user(user_id, db)
        if product:
            minQuantity = min(product.quantity, quantity)
            product.quantity -= minQuantity
            cost = minQuantity * product.price
            if user.balance < cost:
                return None
            user.balance -= minQuantity * product.price
            insertion = user_products.insert().values(
                user_id=user.id, product_id=product.id, quantity=minQuantity
            )
            db.execute(insertion)
            db.commit()
            query = text(
                """
                SELECT 
                    p.id as id,
                    p.title as title,
                    p.description as description,
                    p.price as price,
                    SUM(p.price * up.quantity) as total_spent_on_product,
                    SUM(up.quantity) as total_quantity_bought,
                    u.balance as balance,
                    u.username as username,
                    u.id as user_id
                FROM 
                    user_products up
                    JOIN products p ON up.product_id = p.id
                    JOIN users u ON up.user_id = u.id
                WHERE 
                    up.user_id = :user_id
                GROUP BY
                    p.id, p.title, p.price, u.balance, u.username, u.id
                order by p.id
                """
            )
            data = db.execute(query, {"user_id": user.id}).fetchall()
            return data
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(400, "Error while buying product")


def delete_product(product_id: int, db: Session):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
            return True
        return None
    except Exception:
        db.rollback()
        raise HTTPException(400, "Error while deleting product")
