from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class NotificationRequest(BaseModel):
    """
    Request model for accepting general notification events
    """
    notification_type: str = Field(
        ...,
        description="Type of notification (e.g., 'order_update', 'system_alert')",
        min_length=1,
        max_length=100
    )

    source: str = Field(
        ...,
        description="Source service/system that generated the notification",
        min_length=1,
        max_length=100
    )

    payload: Dict[str, Any] = Field(
        ...,
        description="Notification-specific data as flexible JSON object"
    )

    priority: Optional[str] = Field(
        default="normal",
        description="Priority level: 'low', 'normal', 'high', 'critical'",
        pattern="^(normal|high|urgent)$"
    )

    timestamp: Optional[str] = Field(
        default=None,
        description="ISO format timestamp (auto-generated if not provided)"
    )

    reference_id: Optional[str] = Field(
        default=None,
        description="External reference ID (order ID, transaction ID, etc.)",
        max_length=200
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata/tags for the notification"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "notification_type": "order_update",
                "source": "purchasing-service",
                "payload": {
                    "order_id": "ORD-12345",
                    "status": "confirmed",
                    "amount": 15000.00
                },
                "priority": "high",
                "reference_id": "ORD-12345",
                "metadata": {
                    "user_id": "USR-789",
                    "region": "asia-pacific"
                }
            }
        }
