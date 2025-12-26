from pydantic import BaseModel, EmailStr
from typing import Optional


class CarServiceStatusEmail(BaseModel):
    # Customer details
    to_email: EmailStr
    customer_name: str

    # Car details
    car_make: str
    car_model: str
    car_year: Optional[str] = None
    chassis_number: Optional[str] = None

    # Status details
    old_status: Optional[str] = None
    new_status: str
