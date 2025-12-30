from pydantic import BaseModel, EmailStr
from typing import Optional


class PurchasingStatusEmail(BaseModel):
    # Customer details
    email: Optional[EmailStr] = None
    customer_name: Optional[str] = None

    # Car details
    make: str
    model: str
    year: Optional[int] = None
    chassis_id: Optional[str] = None

    # Purchasing status details
    old_status: Optional[str] = None
    new_status: str  # e.g., "LC Opened", "LC Received", "Payment Processed", "Documents Verified"

    # Purchase details
    purchase_order_id: Optional[str] = None
    lc_number: Optional[str] = None  # Letter of Credit number
    supplier_name: Optional[str] = None
    port_of_loading: Optional[str] = None
    expected_shipping_date: Optional[str] = None
    purchase_price: Optional[str] = None
    currency: Optional[str] = None

    # Additional information
    notes: Optional[str] = None
    contact_person: Optional[str] = None
