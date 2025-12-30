from fastapi import FastAPI, HTTPException, Depends

from auth.AuthService import AuthService
from config import get_settings
from dto.request import PurchasingStatusEmail, ShippingStatusEmail, NotificationRequest
from mail_server.MailServer import MailServer
from services.MailService import MailService
from services.TemplateRenderer import TemplateRenderer
from services.NotificationService import NotificationService
from db.DataBase import Database

app = FastAPI(title="Email Service API")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=configs.host, port=configs.port)
