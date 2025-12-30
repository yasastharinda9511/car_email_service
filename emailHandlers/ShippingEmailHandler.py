from typing import Dict, Any

from fastapi import HTTPException

from dto.request import ShippingStatusEmail
from services.TemplateRenderer import TemplateRenderer
from mail_server.MailServer import MailServer


class ShippingEmailHandler:
    def __init__(self, template_renderer: TemplateRenderer, mail_server: MailServer):
        self.template_renderer = template_renderer
        self.mail_server = mail_server

    def send_shipping_status_update(self, shipping: ShippingStatusEmail):
        try:
            # Load template
            template_content = self.template_renderer.load_template("shipping_status_template.html")

            # Build car info
            car_info = f"{shipping.make} {shipping.model}"
            if shipping.year:
                car_info += f" ({shipping.year})"

            # Build status message
            if shipping.old_status:
                status_message = f"Your vehicle shipping status has been updated from <strong>{shipping.old_status}</strong> to <strong>{shipping.new_status}</strong>."
            else:
                status_message = f"Your vehicle shipping status is now: <strong>{shipping.new_status}</strong>"

            # Build conditional sections
            chassis_section = self.template_renderer.build_section(
                shipping.chassis_id,
                f'<div class="info-item"><strong>Chassis Number:</strong> {shipping.chassis_id}</div>'
            )

            shipping_order_section = self.template_renderer.build_section(
                shipping.shipping_order_id,
                f'<div class="info-item"><strong>Shipping Order ID:</strong> {shipping.shipping_order_id}</div>'
            )

            vessel_section = self.template_renderer.build_section(
                shipping.vessel_name,
                f'<div class="info-item"><strong>Vessel Name:</strong> {shipping.vessel_name}</div>'
            )

            voyage_section = self.template_renderer.build_section(
                shipping.voyage_number,
                f'<div class="info-item"><strong>Voyage Number:</strong> {shipping.voyage_number}</div>'
            )

            container_section = self.template_renderer.build_section(
                shipping.container_number,
                f'<div class="info-item"><strong>Container Number:</strong> {shipping.container_number}</div>'
            )

            bl_section = self.template_renderer.build_section(
                shipping.bill_of_lading,
                f'<div class="info-item"><strong>Bill of Lading:</strong> {shipping.bill_of_lading}</div>'
            )

            port_loading_section = self.template_renderer.build_section(
                shipping.port_of_loading,
                f'<div class="info-item"><strong>Port of Loading:</strong> {shipping.port_of_loading}</div>'
            )

            port_discharge_section = self.template_renderer.build_section(
                shipping.port_of_discharge,
                f'<div class="info-item"><strong>Port of Discharge:</strong> {shipping.port_of_discharge}</div>'
            )

            eta_section = self.template_renderer.build_section(
                shipping.estimated_arrival_date,
                f'<div class="info-item"><strong>Estimated Arrival:</strong> {shipping.estimated_arrival_date}</div>'
            )

            ata_section = self.template_renderer.build_section(
                shipping.actual_arrival_date,
                f'<div class="info-item"><strong>Actual Arrival:</strong> {shipping.actual_arrival_date}</div>'
            )

            delivery_section = self.template_renderer.build_section(
                shipping.delivery_date,
                f'<div class="info-item"><strong>Delivery Date:</strong> {shipping.delivery_date}</div>'
            )

            tracking_section = self.template_renderer.build_section(
                shipping.tracking_url,
                f'<div style="text-align: center;"><a href="{shipping.tracking_url}" class="tracking-button">📍 Track Your Shipment</a></div>'
            )

            notes_section = self.template_renderer.build_section(
                shipping.notes,
                f'<div class="highlight"><p class="info-label">📌 Important Notes</p><p>{shipping.notes}</p></div>'
            )

            contact_section = self.template_renderer.build_section(
                shipping.contact_person,
                f'<div class="info-item"><strong>Contact Person:</strong> {shipping.contact_person}</div>'
            )

            # Render template
            html_body = self.template_renderer.render_template(
                template_content,
                customer_name=shipping.customer_name,
                status_message=status_message,
                new_status=shipping.new_status,
                car_info=car_info,
                chassis_number_section=chassis_section,
                shipping_order_section=shipping_order_section,
                vessel_section=vessel_section,
                voyage_section=voyage_section,
                container_section=container_section,
                bl_section=bl_section,
                port_loading_section=port_loading_section,
                port_discharge_section=port_discharge_section,
                eta_section=eta_section,
                ata_section=ata_section,
                delivery_date_section=delivery_section,
                tracking_section=tracking_section,
                notes_section=notes_section,
                contact_section=contact_section
            )

            # Send email
            success = self.mail_server.send_email(
                to_email=shipping.email,
                subject=f"Shipping Update: {shipping.new_status} - {car_info}",
                body=html_body
            )

            if success:
                return {
                    "status": "success",
                    "message": f"Shipping status email sent to {shipping.to_email}",
                    "details": {
                        "car": car_info,
                        "new_status": shipping.new_status,
                        "shipping_order_id": shipping.shipping_order_id,
                        "tracking_url": shipping.tracking_url
                    }
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to send email")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


