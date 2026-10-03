import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    SMTP_USERNAME,
)


class EmailService:

    @staticmethod
    def _validate_config():

        missing = []

        if not SMTP_HOST:
            missing.append("SMTP_HOST")

        if not SMTP_USERNAME:
            missing.append("SMTP_USERNAME")

        if not SMTP_PASSWORD:
            missing.append("SMTP_PASSWORD")

        if missing:
            raise RuntimeError(
                "Missing SMTP configuration: "
                + ", ".join(missing)
            )

    @staticmethod
    def send_email(
        recipient: str,
        subject: str,
        body: str,
    ):

        EmailService._validate_config()

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = recipient

        message.set_content(body)

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=20,
        ) as server:

            server.starttls()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )

            server.send_message(message)

    @staticmethod
    def send_organization_otp(
        email: str,
        otp: str,
    ):

        subject = "Zero Trust Organization Email Verification"

        body = f"""
Hello,

Your Zero Trust organization verification OTP is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this verification,
please ignore this email.

Regards,
Zero Trust Security Platform
"""

        EmailService.send_email(
            recipient=email,
            subject=subject,
            body=body,
        )

    @staticmethod
    def send_user_invitation(
        email: str,
        name: str,
        invitation_link: str,
    ):

        subject = "You've been invited to Zero Trust"

        body = f"""
Hello {name},

You have been invited to join your organization's
Zero Trust Security Platform.

Complete your account setup using this link:

{invitation_link}

If you were not expecting this invitation,
please ignore this email.

Regards,
Zero Trust Security Platform
"""

        EmailService.send_email(
            recipient=email,
            subject=subject,
            body=body,
        )