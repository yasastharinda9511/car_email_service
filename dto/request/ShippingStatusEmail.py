from pydantic import BaseModel, EmailStr
from typing import Optional


class ShippingStatusEmail(BaseModel):
    # Customer details
    to_email: EmailStr
    customer_name: str

    # Car details
    car_make: str
    car_model: str
    car_year: Optional[str] = None
    chassis_number: Optional[str] = None

    # Shipping status details
    old_status: Optional[str] = None
    new_status: str  # e.g., "In Transit", "Arrived at Port", "Customs Clearance", "Ready for Delivery"

    # Shipping details
    shipping_order_id: Optional[str] = None
    vessel_name: Optional[str] = None
    voyage_number: Optional[str] = None
    container_number: Optional[str] = None
    bill_of_lading: Optional[str] = None  # B/L number
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    estimated_arrival_date: Optional[str] = None
    actual_arrival_date: Optional[str] = None
    delivery_date: Optional[str] = None
    tracking_url: Optional[str] = None

    # Additional information
    notes: Optional[str] = None
    contact_person: Optional[str] = None
