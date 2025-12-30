from typing import Dict, Any
from fastapi import HTTPException

from dto.request import PurchasingStatusEmail, ShippingStatusEmail
from emailHandlers.PurchaseEmailHandler import EmailPurchaseHandler
from emailHandlers.ShippingEmailHandler import ShippingEmailHandler
from mail_server import MailServer
from services.TemplateRenderer import TemplateRenderer


class MailService:
    def __init__(self, mail_server: MailServer, template_renderer: TemplateRenderer):
        self.mail_server = mail_server
        self.template_renderer = template_renderer

        # Initialize handlers
        self.purchase_handler = EmailPurchaseHandler(
            template_renderer=template_renderer,
            mail_server=mail_server
        )
        self.shipping_handler = ShippingEmailHandler(
            template_renderer=template_renderer,
            mail_server=mail_server
        )

        # Map notification types to (handler, DTO class, handler method name)
        self.mail_processing_map = {
            "purchase_status": (self.purchase_handler, PurchasingStatusEmail, "send_purchase_status_update"),
            "shipping_status": (self.shipping_handler, ShippingStatusEmail, "send_shipping_status_update"),
        }

    def send_mail(self, notification_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process notification and send appropriate email based on notification type

        Args:
            notification_type: Type of notification (e.g., 'purchase_status', 'shipping_status')
            payload: Dictionary containing the notification data

        Returns:
            Dictionary with send result details

        Raises:
            HTTPException: If notification type is not supported or sending fails
        """
        # Check if notification type is supported
        if notification_type not in self.mail_processing_map:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported notification type: {notification_type}. "
                       f"Supported types: {', '.join(self.mail_processing_map.keys())}"
            )

        try:
            # Get handler, DTO class, and method name for this notification type
            handler, dto_class, method_name = self.mail_processing_map[notification_type]

            # Transform payload from backend format to DTO format

            # Convert transformed payload to appropriate DTO
            email_dto = dto_class(**payload)

            # Get the handler method and call it
            handler_method = getattr(handler, method_name)
            result = handler_method(email_dto)

            return result

        except ValueError as e:
            # Pydantic validation error when converting payload to DTO
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payload for notification type '{notification_type}': {str(e)}"
            )
        except AttributeError as e:
            # Handler method not found
            raise HTTPException(
                status_code=500,
                detail=f"Handler configuration error: {str(e)}"
            )
        except Exception as e:
            # Other unexpected errors
            raise HTTPException(
                status_code=500,
                detail=f"Error sending email: {str(e)}"
            )

    def send_purchase_status_update(self, purchase: PurchasingStatusEmail) -> Dict[str, Any]:
        """
        Send purchase status update email (backward compatible method)

        Args:
            purchase: PurchasingStatusEmail DTO

        Returns:
            Dictionary with send result details
        """
        return self.purchase_handler.send_purchase_status_update(purchase)

    def send_shipping_status_update(self, shipping: ShippingStatusEmail) -> Dict[str, Any]:
        """
        Send shipping status update email (backward compatible method)

        Args:
            shipping: ShippingStatusEmail DTO

        Returns:
            Dictionary with send result details
        """
        return self.shipping_handler.send_shipping_status_update(shipping)
