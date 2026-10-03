from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.organization import OrganizationUpdateRequest
from app.services.organization_service import OrganizationService
from app.services.verification_service import VerificationService


class OrganizationController:

    # ============================================================
    # Existing Organization APIs
    # ============================================================

    @staticmethod
    def get_organization(
        db: Session,
        organization_id: str,
        current_user: User,
    ):
        return OrganizationService.get_organization(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
        )

    @staticmethod
    def update_organization(
        db: Session,
        organization_id: str,
        request: OrganizationUpdateRequest,
        current_user: User,
    ):
        return OrganizationService.update_organization(
            db=db,
            organization_id=organization_id,
            update_data=request.model_dump(
                exclude_unset=True
            ),
            current_user=current_user,
        )

    @staticmethod
    def get_settings(
        db: Session,
        organization_id: str,
        current_user: User,
    ):
        return OrganizationService.get_settings(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
        )

    @staticmethod
    def get_verification(
        db: Session,
        organization_id: str,
        current_user: User,
    ):
        return OrganizationService.get_verification(
            db=db,
            organization_id=organization_id,
            current_user=current_user,
        )

    # ============================================================
    # Module 1 - Organization Registration
    # ============================================================

    @staticmethod
    def create_organization(
        db: Session,
        organization_data: dict,
    ):
        return OrganizationService.create_organization(
            db=db,
            organization_data=organization_data,
        )

    # ============================================================
    # Module 1 - Professional Email
    # ============================================================

    @staticmethod
    def validate_professional_email(
        email: str,
    ):
        return OrganizationService.validate_professional_email(
            email=email,
        )

    @staticmethod
    def get_email_domain(
        email: str,
    ):
        return OrganizationService.get_email_domain(
            email=email,
        )

    # ============================================================
    # Module 1 - OTP Verification
    # ============================================================

    @staticmethod
    def verify_organization_email(
        db: Session,
        organization_id: str,
        otp: str,
    ):
        return OrganizationService.verify_organization_email(
            db=db,
            organization_id=organization_id,
            otp=otp,
        )

    # ============================================================
    # Module 1 - OTP Resend
    # ============================================================

    @staticmethod
    def resend_organization_otp(
        db: Session,
        organization_id: str,
    ):
        return OrganizationService.resend_organization_otp(
            db=db,
            organization_id=organization_id,
        )

    # ============================================================
    # Organization Verification
    # ============================================================

    @staticmethod
    def submit_verification(
        db: Session,
        organization_id: str,
        verification_data: dict,
    ):
        """
        Submit organization verification request.

        The route sends the complete request data as a dictionary.
        The controller extracts the required fields and delegates
        the actual business logic to VerificationService.
        """

        return VerificationService.submit_verification(
            db=db,
            organization_id=organization_id,
            verification_type=verification_data.get(
                "verification_type",
                "ORGANIZATION",
            ),
            registration_number=verification_data.get(
                "registration_number"
            ),
        )

    # ============================================================
    # Get Verification Status
    # ============================================================

    @staticmethod
    def get_verification_status(
        db: Session,
        organization_id: str,
    ):
        return VerificationService.get_verification_status(
            db=db,
            organization_id=organization_id,
        )

    # ============================================================
    # Verification Document Upload
    # ============================================================

    @staticmethod
    async def upload_verification_document(
        db: Session,
        organization_id: str,
        document_type: str,
        document: UploadFile,
    ):
        return await VerificationService.upload_document(
            db=db,
            organization_id=organization_id,
            document_type=document_type,
            document=document,
        )
def get_dashboard(
    self,
    organization_id: str,
    current_user,
):
    organization = self.repository.get_by_id(
        organization_id
    )

    if not organization:
        raise ValueError("Organization not found")

    return {
        "organization": {
            "id": organization.id,
            "name": organization.name,
            "status": getattr(
                organization,
                "status",
                None,
            ),
        },
        "statistics": {
            "total_users": self.repository.count_users(
                organization_id
            ),
            "total_teams": self.repository.count_teams(
                organization_id
            ),
        },
        "security": {
            "anomalies": 0,
            "alerts": 0,
            "high_risk_events": 0,
        },
        "activity": [],
    }