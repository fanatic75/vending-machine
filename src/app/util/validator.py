from fastapi import HTTPException
from pydantic import BaseModel, validator

class CoinsValidation(BaseModel):
    denomination: int

    @validator("denomination")
    def validate_denomination(cls, v):
        allowed_values = {0, 5, 10, 20, 50, 100}
        if v not in allowed_values:
            raise HTTPException(
                400,
                "Invalid Denomination value. Allowed values are: 5, 10, 20, 50, 100"
            )
        return v
