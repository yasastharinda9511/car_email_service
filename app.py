from fastapi import FastAPI, HTTPException

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


@app.get("/email-service")
async def root():
    return {"message": "Email Service API is running"}


@app.post("/email-service/send-purchasing-status")
async def send_purchasing_status(purchase: PurchasingStatusEmail):
    """
    Send purchasing status update email (LC opened, LC received, payment processed, etc.)
    """
    try:
        response = mail_service.send_purchase_status_update(purchase)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/email-service/send-shipping-status")
async def send_shipping_status(shipping: ShippingStatusEmail):
    """
    Send shipping status update email (In Transit, Arrived at Port, Customs Clearance, etc.)
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
