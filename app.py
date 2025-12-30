from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import math

from auth.AuthService import AuthService
from config import get_settings
from dto.request import PurchasingStatusEmail, ShippingStatusEmail, NotificationRequest
from dto.response import PaginatedNotificationsResponse, NotificationItem, PaginationMeta
from mail_server.MailServer import MailServer
from services.MailService import MailService
from services.TemplateRenderer import TemplateRenderer
from services.NotificationService import NotificationService
from db.DataBase import Database

app = FastAPI(title="Email Service API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configs = get_settings()

# Initialize services
mail_server = MailServer(
    host=configs.mail_server_host,
    port=configs.mail_server_port,
    e_mail=configs.email,
    password=configs.email_app_password
)
dataBase = Database(
    host=configs.db_host,
    port=configs.db_port,
    database=configs.db_name,
    user=configs.db_user,
    password=configs.db_password,
    min_conn=1,
    max_conn=3
)

template_renderer = TemplateRenderer()
mail_service = MailService(mail_server = mail_server , template_renderer=template_renderer)
notification_store = NotificationService(data_base=dataBase)
auth_service = AuthService(introspect_url=configs.introspect_url)


# Auth dependency
async def verify_token(token_data: dict = Depends(auth_service.verify_token)):
    """Dependency to verify authentication token"""
    return token_data


@app.get("/notification-service")
async def root():
    return {"message": "Email Service API is running"}


@app.post("/notification-service/notifications")
async def accept_notification(
    notification: NotificationRequest,
    token_data: dict = Depends(verify_token)
):
    """
    Accept notification events and store them. If an email handler exists for the
    notification type, an email will be sent as well.
    Requires valid Bearer token in Authorization header.

    The notification will always be stored in the database. Email sending is optional
    and won't fail the request if no handler exists or sending fails.
    """
    try:
        # Convert Pydantic model to dict
        notification_dict = notification.model_dump()

        # Store the notification (primary purpose - must succeed)
        storage_result = notification_store.store_notification(notification_dict)

        # Try to send email if handler exists (secondary purpose - optional)
        email_result = None
        email_error = None
        try:
            email_result = mail_service.send_mail(
                notification_type=notification.notification_type,
                payload=notification.payload
            )
        except HTTPException as e:
            # Email handler doesn't exist or validation failed - this is OK
            email_error = e.detail
        except Exception as e:
            # Email sending failed - this is OK, just log it
            email_error = str(e)

        # Build response
        response = {
            "status": "success",
            "message": "Notification accepted and stored",
            "details": {
                "storage": storage_result
            }
        }

        if email_result:
            response["message"] = "Notification accepted, stored, and email sent"
            response["details"]["email"] = email_result
        elif email_error:
            response["details"]["email_warning"] = f"Email not sent: {email_error}"

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/notification-service/notifications", response_model=PaginatedNotificationsResponse)
async def get_notifications(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    source: Optional[str] = Query(None, description="Filter by source service"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    token_data: dict = Depends(verify_token)
):
    """
    Retrieve notifications with pagination and optional filters.
    Requires valid Bearer token in Authorization header.

    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - notification_type: Filter by notification type (optional)
    - source: Filter by source service (optional)
    - priority: Filter by priority level (optional)

    Returns paginated notifications with metadata including total count and page information.
    """
    try:
        # Calculate offset from page number
        offset = (page - 1) * page_size

        # Get total count with filters
        total_count = notification_store.get_notification_count(
            notification_type=notification_type,
            source=source,
            priority=priority
        )

        # Get notifications with pagination
        notifications = notification_store.get_notifications(
            notification_type=notification_type,
            source=source,
            priority=priority,
            limit=page_size,
            offset=offset
        )

        # Calculate total pages
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

        # Convert datetime objects to ISO format strings
        processed_notifications = []
        for notification in notifications:
            # Create a copy to avoid modifying the original
            notif_dict = dict(notification)

            # Convert timestamp if it's a datetime object
            if notif_dict.get('timestamp') and hasattr(notif_dict['timestamp'], 'isoformat'):
                notif_dict['timestamp'] = notif_dict['timestamp'].isoformat()

            # Convert stored_at if it's a datetime object
            if notif_dict.get('stored_at') and hasattr(notif_dict['stored_at'], 'isoformat'):
                notif_dict['stored_at'] = notif_dict['stored_at'].isoformat()

            processed_notifications.append(notif_dict)

        # Build response
        return PaginatedNotificationsResponse(
            notifications=[NotificationItem(**notification) for notification in processed_notifications],
            pagination=PaginationMeta(
                total=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving notifications: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=configs.host, port=configs.port)
