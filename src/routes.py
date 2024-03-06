from fastapi import APIRouter

from src.app.users.user_controller import router as users
from src.app.products.products_controller import router as products

api_router = APIRouter()

api_router.include_router(users, prefix="/users", tags=["users"])
api_router.include_router(products, prefix="/products", tags=["products"])