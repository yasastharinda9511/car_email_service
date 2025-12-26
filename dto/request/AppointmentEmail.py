from pydantic import BaseModel, EmailStr


class AppointmentEmail(BaseModel):
    to_email: EmailStr
    customer_name: str = "Customer"
    date: str
    time: str
    service: str