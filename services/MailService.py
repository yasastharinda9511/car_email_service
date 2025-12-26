from fastapi import HTTPException

from dto.request import PurchasingStatusEmail, ShippingStatusEmail
from mail_server import MailServer
from services import TemplateRenderer


class MailService:
    def __init__(self, mail_server: MailServer, template_renderer: TemplateRenderer):
        self.mail_server = mail_server
        self.template_renderer = template_renderer

    def send_purchase_status_update(self, purchase: PurchasingStatusEmail):
        try:
            # Load template
            template_content = self.template_renderer.load_template("purchasing_status_template.html")

            # Build car info
            car_info = f"{purchase.car_make} {purchase.car_model}"
            if purchase.car_year:
                car_info += f" ({purchase.car_year})"

            # Build status message
            if purchase.old_status:
                status_message = f"Great news! Your vehicle purchase status has been updated from <strong>{purchase.old_status}</strong> to <strong>{purchase.new_status}</strong>."
            else:
                status_message = f"Your vehicle purchase status is now: <strong>{purchase.new_status}</strong>"

            # Build conditional sections
            chassis_section = self.template_renderer.build_section(
                purchase.chassis_number,
                f'<div class="info-item"><strong>Chassis Number:</strong> {purchase.chassis_number}</div>'
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
                to_email=purchase.to_email,
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

    def send_shipping_status_update(self, shipping: ShippingStatusEmail):
        try:
            # Load template
            template_content = self.template_renderer.load_template("shipping_status_template.html")

            # Build car info
            car_info = f"{shipping.car_make} {shipping.car_model}"
            if shipping.car_year:
                car_info += f" ({shipping.car_year})"

            # Build status message
            if shipping.old_status:
                status_message = f"Your vehicle shipping status has been updated from <strong>{shipping.old_status}</strong> to <strong>{shipping.new_status}</strong>."
            else:
                status_message = f"Your vehicle shipping status is now: <strong>{shipping.new_status}</strong>"

            # Build conditional sections
            chassis_section = self.template_renderer.build_section(
                shipping.chassis_number,
                f'<div class="info-item"><strong>Chassis Number:</strong> {shipping.chassis_number}</div>'
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
                to_email=shipping.to_email,
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
