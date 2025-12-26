from fastapi import FastAPI, HTTPException, Depends

from auth.AuthService import AuthService
from config import get_settings
from dto.request import PurchasingStatusEmail, ShippingStatusEmail
from mail_server.MailServer import MailServer
from services.MailService import MailService
from services.TemplateRenderer import TemplateRenderer

app = FastAPI(title="Email Service API")

configs = get_settings()

# Initialize services
mail_server = MailServer(
    host=configs.mail_server_host,
    port=configs.mail_server_port,
    e_mail=configs.email,
    password=configs.email_app_password
)
template_renderer = TemplateRenderer()
mail_service = MailService(mail_server = mail_server , template_renderer=template_renderer)
auth_service = AuthService(introspect_url=configs.introspect_url)


# Auth dependency
async def verify_token(token_data: dict = Depends(auth_service.verify_token)):
    """Dependency to verify authentication token"""
    return token_data


@app.get("/email-service")
async def root():
    return {"message": "Email Service API is running"}


@app.post("/email-service/send-purchasing-status")
async def send_purchasing_status(
    purchase: PurchasingStatusEmail,
    token_data: dict = Depends(verify_token)
):
    """
    Send purchasing status update email (LC opened, LC received, payment processed, etc.)
    Requires valid Bearer token in Authorization header.
    """
    try:
        response = mail_service.send_purchase_status_update(purchase)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/email-service/send-shipping-status")
async def send_shipping_status(
    shipping: ShippingStatusEmail,
    token_data: dict = Depends(verify_token)
):
    """
    Send shipping status update email (In Transit, Arrived at Port, Customs Clearance, etc.)
    Requires valid Bearer token in Authorization header.
    """
    try:
        response = mail_service.send_shipping_status_update(shipping)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=configs.host, port=configs.port)
