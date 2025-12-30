from fastapi import HTTPException

from dto.request import PurchasingStatusEmail
from services.TemplateRenderer import TemplateRenderer
from mail_server.MailServer import MailServer


class EmailPurchaseHandler:

    def __init__(self, template_renderer: TemplateRenderer, mail_server: MailServer):
        self.template_renderer = template_renderer
        self.mail_server = mail_server

    def send_purchase_status_update(self, purchase: PurchasingStatusEmail):
        try:
            # Load template
            template_content = self.template_renderer.load_template("purchasing_status_template.html")

            # Build car info
            car_info = f"{purchase.make} {purchase.model}"
            if purchase.year:
                car_info += f" ({purchase.year})"

            # Build status message
            if purchase.old_status:
                status_message = f"Great news! Your vehicle purchase status has been updated from <strong>{purchase.old_status}</strong> to <strong>{purchase.new_status}</strong>."
            else:
                status_message = f"Your vehicle purchase status is now: <strong>{purchase.new_status}</strong>"

            # Build conditional sections
            chassis_section = self.template_renderer.build_section(
                purchase.chassis_id,
                f'<div class="info-item"><strong>Chassis Number:</strong> {purchase.chassis_id}</div>'
            )

            po_section = self.template_renderer.build_section(
                purchase.purchase_order_id,
                f'<div class="info-item"><strong>Purchase Order:</strong> {purchase.purchase_order_id}</div>'
            )

            lc_section = self.template_renderer.build_section(
                purchase.lc_number,
                f'<div class="info-item"><strong>LC Number:</strong> {purchase.lc_number}</div>'
            )

            supplier_section = self.template_renderer.build_section(
                purchase.supplier_name,
                f'<div class="info-item"><strong>Supplier:</strong> {purchase.supplier_name}</div>'
            )

            price_section = self.template_renderer.build_section(
                purchase.purchase_price,
                f'<div class="info-item"><strong>Purchase Price:</strong> {purchase.currency or ""} {purchase.purchase_price}</div>'
            )

            port_section = self.template_renderer.build_section(
                purchase.port_of_loading,
                f'<div class="info-item"><strong>Port of Loading:</strong> {purchase.port_of_loading}</div>'
            )

            shipping_date_section = self.template_renderer.build_section(
                purchase.expected_shipping_date,
                f'<div class="info-item"><strong>Expected Shipping Date:</strong> {purchase.expected_shipping_date}</div>'
            )

            notes_section = self.template_renderer.build_section(
                purchase.notes,
                f'<div class="highlight"><p class="info-label">📌 Important Notes</p><p>{purchase.notes}</p></div>'
            )

            contact_section = self.template_renderer.build_section(
                purchase.contact_person,
                f'<div class="info-item"><strong>Contact Person:</strong> {purchase.contact_person}</div>'
            )

            # Render template
            html_body = self.template_renderer.render_template(
                template_content,
                customer_name=purchase.customer_name,
                status_message=status_message,
                new_status=purchase.new_status,
                car_info=car_info,
                chassis_number_section=chassis_section,
                purchase_order_section=po_section,
                lc_number_section=lc_section,
                supplier_section=supplier_section,
                price_section=price_section,
                port_loading_section=port_section,
                shipping_date_section=shipping_date_section,
                notes_section=notes_section,
                contact_section=contact_section
            )

            # Send email
            success = self.mail_server.send_email(
                to_email=purchase.email,
                subject=f"Purchase Update: {purchase.new_status} - {car_info}",
                body=html_body
            )

            if success:
                return {
                    "status": "success",
                    "message": f"Purchase status email sent to {purchase.to_email}",
                    "details": {
                        "car": car_info,
                        "new_status": purchase.new_status,
                        "purchase_order_id": purchase.purchase_order_id
                    }
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to send email")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
