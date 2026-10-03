from datetime import datetime

from sqlalchemy.orm import Session

from app.models.email_otp import EmailOTP


class OTPRepository:

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        email: str,
        otp_hash: str,
        expires_at: datetime,
        resend_available_at: datetime,
        max_attempts: int = 5
    ) -> EmailOTP:
        otp_record = EmailOTP(
            organization_id=organization_id,
            email=email,
            otp_hash=otp_hash,
            expires_at=expires_at,
            resend_available_at=resend_available_at,
            attempts=0,
            max_attempts=max_attempts,
            verified=False
        )

        db.add(otp_record)
        db.commit()
        db.refresh(otp_record)

        return otp_record

    @staticmethod
    def get_latest_for_organization(
        db: Session,
        organization_id: str
    ) -> EmailOTP | None:
        return (
            db.query(EmailOTP)
            .filter(
                EmailOTP.organization_id == organization_id
            )
            .order_by(
                EmailOTP.created_at.desc()
            )
            .first()
        )

    @staticmethod
    def get_latest_for_email(
        db: Session,
        organization_id: str,
        email: str
    ) -> EmailOTP | None:
        return (
            db.query(EmailOTP)
            .filter(
                EmailOTP.organization_id == organization_id,
                EmailOTP.email == email
            )
            .order_by(
                EmailOTP.created_at.desc()
            )
            .first()
        )

    @staticmethod
    def increment_attempts(
        db: Session,
        otp_record: EmailOTP
    ) -> EmailOTP:
        otp_record.attempts += 1

        db.commit()
        db.refresh(otp_record)

        return otp_record

    @staticmethod
    def mark_verified(
        db: Session,
        otp_record: EmailOTP
    ) -> EmailOTP:
        otp_record.verified = True

        db.commit()
        db.refresh(otp_record)

        return otp_record

    @staticmethod
    def invalidate_previous_otps(
        db: Session,
        organization_id: str
    ) -> None:
        records = (
            db.query(EmailOTP)
            .filter(
                EmailOTP.organization_id == organization_id,
                EmailOTP.verified == False
            )
            .all()
        )

        for record in records:
            record.verified = True

        db.commit()