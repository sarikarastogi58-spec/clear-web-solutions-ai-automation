import os
import smtplib
from email.mime.text import MIMEText

import requests


def send_email(to_email: str, subject: str, body: str) -> dict:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL", smtp_user)
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")

    if sendgrid_api_key:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": from_email},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            },
        )
        return {"success": response.ok, "status_code": response.status_code, "body": response.text}

    if not smtp_host or not smtp_user or not smtp_pass:
        return {"success": False, "error": "SMTP or SendGrid credentials not configured"}

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(message)
        server.quit()
        return {"success": True}
    except Exception as err:
        return {"success": False, "error": str(err)}


def send_twilio_message(body: str, to_number: str, channel: str = "sms") -> dict:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")

    if not account_sid or not auth_token or not from_number:
        return {"success": False, "error": "Twilio credentials not configured"}

    if channel == "whatsapp":
        from_value = f"whatsapp:{whatsapp_from or from_number}"
        to_value = f"whatsapp:{to_number}"
    else:
        from_value = from_number
        to_value = to_number

    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        auth=(account_sid, auth_token),
        data={"From": from_value, "To": to_value, "Body": body},
    )
    return {"success": response.ok, "status_code": response.status_code, "body": response.text}
