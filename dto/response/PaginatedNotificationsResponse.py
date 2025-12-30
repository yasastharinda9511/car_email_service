from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class NotificationItem(BaseModel):
    """Individual notification item in the response"""
    notification_id: str
    notification_type: str
    source: str
    payload: Dict[str, Any]
    priority: str
    timestamp: str
    reference_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    stored_at: str


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int = Field(..., description="Total number of notifications")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PaginatedNotificationsResponse(BaseModel):
    """Response model for paginated notifications"""
    notifications: List[NotificationItem]
    pagination: PaginationMeta

    class Config:
        json_schema_extra = {
            "example": {
                "notifications": [
                    {
                        "notification_id": "123e4567-e89b-12d3-a456-426614174000",
                        "notification_type": "order_update",
                        "source": "purchasing-service",
                        "payload": {
                            "order_id": "ORD-12345",
                            "status": "confirmed"
                        },
                        "priority": "high",
                        "timestamp": "2025-12-30T10:30:00Z",
                        "reference_id": "ORD-12345",
                        "metadata": {"user_id": "USR-789"},
                        "stored_at": "2025-12-30T10:30:01Z"
                    }
                ],
                "pagination": {
                    "total": 150,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 8
                }
            }
        }
