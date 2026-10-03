import hashlib
import secrets
from datetime import datetime, timedelta


class OTPService:

    OTP_EXPIRY_MINUTES = 10
    RESEND_COOLDOWN_SECONDS = 60
    MAX_OTP_ATTEMPTS = 5
    OTP_LENGTH = 6

    @staticmethod
    def generate_otp() -> str:
        """
        Generate a secure 6-digit OTP.
        """
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def hash_otp(otp: str) -> str:
        """
        Hash OTP using SHA-256 before storing it.
        """
        return hashlib.sha256(
            otp.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def verify_otp(otp: str, stored_hash: str) -> bool:
        """
        Compare the supplied OTP against the stored hash.
        """
        calculated_hash = OTPService.hash_otp(otp)

        return secrets.compare_digest(
            calculated_hash,
            stored_hash
        )

    @staticmethod
    def get_expiry_time() -> datetime:
        """
        Return the time at which the OTP expires.
        """
        return datetime.utcnow() + timedelta(
            minutes=OTPService.OTP_EXPIRY_MINUTES
        )

    @staticmethod
    def get_resend_available_time() -> datetime:
        """
        Return the time at which another OTP can be requested.
        """
        return datetime.utcnow() + timedelta(
            seconds=OTPService.RESEND_COOLDOWN_SECONDS
        )

    @staticmethod
    def is_expired(expires_at: datetime) -> bool:
        """
        Check whether the OTP has expired.
        """
        return datetime.utcnow() >= expires_at

    @staticmethod
    def can_attempt(attempts: int) -> bool:
        """
        Check whether the user still has OTP verification attempts.
        """
        return attempts < OTPService.MAX_OTP_ATTEMPTS

    @staticmethod
    def can_resend(resend_available_at: datetime) -> bool:
        """
        Check whether the resend cooldown has elapsed.
        """
        return datetime.utcnow() >= resend_available_at

    @staticmethod
    def seconds_until_resend(
        resend_available_at: datetime
    ) -> int:
        """
        Return remaining resend cooldown in seconds.
        """
        remaining = (
            resend_available_at - datetime.utcnow()
        ).total_seconds()

        return max(0, int(remaining))