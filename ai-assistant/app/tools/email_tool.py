import smtplib
from email.message import EmailMessage
from app.config import Config


def send_email(to: str, subject: str, body: str) -> str:
    if not Config.GMAIL_USER or not Config.GMAIL_APP_PASSWORD:
        return "Gmail not configured. Set GMAIL_USER and GMAIL_APP_PASSWORD in .env"
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = Config.GMAIL_USER
        msg["To"] = to

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(Config.GMAIL_USER, Config.GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        return f"Email sent to {to}"
    except Exception as e:
        return f"Failed to send email: {e}"


EMAIL_TOOLS = [
    (send_email, "send_email", "Send an email via Gmail SMTP", {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body text"},
        },
        "required": ["to", "subject", "body"],
    }),
]
