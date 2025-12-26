import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailServer:
    def __init__(self, host,  port, e_mail, password):
        self.host = host
        self.port = port
        self.e_mail = e_mail
        self.password = password

    def send_email(self, to_email, subject, body):
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.e_mail
        message["To"] = to_email

        # Add HTML content
        html_part = MIMEText(body, "html")
        message.attach(html_part)

        try:
            # Connect to Gmail SMTP server
            with smtplib.SMTP_SSL(self.host, self.port) as server:
                server.login(self.e_mail, self.password)
                server.sendmail(self.e_mail, to_email, message.as_string())
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
