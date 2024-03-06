from fastapi import FastAPI

from src.core.config import settings
from src.routes import api_router

from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi import Limiter, _rate_limit_exceeded_handler

summary = """ 
 API for a vending machine, allowing users with a “seller” role to add, update, or remove products, while users with a “buyer” role can deposit coins into the machine and make purchases. The vending machine should only accept 5, 10, 20, 50, and 100 cent coins
"""

limiter = Limiter(key_func=get_remote_address, default_limits=["50/minute"])
app = FastAPI(title="Vending Machine API", version="0.1", summary=summary)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)
