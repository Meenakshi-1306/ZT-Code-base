from datetime import datetime

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.organization_verification import OrganizationVerification
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.otp_repository import OTPRepository
from app.services.otp_service import OTPService
from app.services.email_service import EmailService
from app.models.role import Role
from app.repositories.organization_repository import OrganizationRepository


class OrganizationService:

    # ============================================================
    # Existing Organization Access Helpers
    # ============================================================

    @staticmethod
    def _get_current_organization_id(current_user: User):
        """
        Get the organization associated with the current user.
        """

        # If current_user already has an active organization
        if getattr(current_user, "current_organization_id", None):
            return current_user.current_organization_id

        # Otherwise use the user's first active organization membership
        memberships = getattr(current_user, "organization_members", [])

        for membership in memberships:
            if getattr(membership, "status", None) == "active":
                return membership.organization_id

        # Fallback if status is not present on the membership
        if memberships:
            return memberships[0].organization_id

        return None

    @staticmethod
    def _ensure_organization_access(
        db: Session,
        organization: Organization,
        current_user: User,
    ):
        """
        Ensure the current user belongs to the requested organization.
        """

        if not organization:
            raise ValueError("Organization not found")

        membership = OrganizationRepository.get_membership(
            db=db,
            user_id=current_user.id,
            organization_id=organization.id,
        )

        if not membership:
            raise PermissionError(
                "You do not have access to this organization"
            )

        return membership

    # ============================================================
    # Existing Organization APIs
    # ============================================================
    @staticmethod
    def assign_role(
    db: Session,
    organization_id: str,
    user_id: str,
    role_id: str,
    current_user
):
    # --------------------------------------------------------
    # Validate target user membership
    # --------------------------------------------------------

        membership = OrganizationRepository.get_membership(
        db=db,
        user_id=user_id,
        organization_id=organization_id
    )

        if not membership:
            raise ValueError(
            "User does not belong to this organization"
        )

    # --------------------------------------------------------
    # Validate role belongs to same organization
    # --------------------------------------------------------

        role = (
        db.query(Role)
        .filter(
            Role.id == role_id,
            Role.organization_id == organization_id
        )
        .first()
    )

        if not role:
            raise ValueError(
            "Role not found in this organization"
        )

    # --------------------------------------------------------
    # Assign role
    # --------------------------------------------------------

        membership.role_id = role.id

        db.commit()
        db.refresh(membership)

        return {
        "user_id": user_id,
        "organization_id": organization_id,
        "role_id": role.id,
        "role_name": role.name
    }
    
    @staticmethod
    def get_organization(
        db: Session,
        organization_id: str,
        current_user: User,
    ):
        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        OrganizationService._ensure_organization_access(
            db,
            organization,
            current_user,
        )

        members = OrganizationRepository.get_members(
            db,
            organization_id,
        )

        return {
            "organization_id": organization.id,
            "name": organization.name,
            "registration_number": organization.registration_number,
            "industry": organization.industry,
            "website": organization.website,
            "contact_email": organization.contact_email,
            "contact_phone": organization.contact_phone,
            "address": organization.address,
            "organization_type": organization.organization_type,
            "email_domain": organization.email_domain,
            "country": organization.country,
            "state": organization.state,
            "gstin": organization.gstin,
            "verification_status": organization.verification_status,
            "email_verified": organization.email_verified,
            "verified_at": organization.verified_at,
            "created_at": organization.created_at,
            "updated_at": organization.updated_at,
            "members": [
                member.user_id
                for member in members
            ],
        }

    @staticmethod
    def update_organization(
        db: Session,
        organization_id: str,
        update_data: dict,
        current_user: User,
    ):
        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        OrganizationService._ensure_organization_access(
            db,
            organization,
            current_user,
        )

        allowed_fields = {
            "name",
            "registration_number",
            "industry",
            "website",
            "contact_email",
            "contact_phone",
            "address",
            "organization_type",
            "email_domain",
            "country",
            "state",
            "gstin",
        }

        filtered_data = {
            key: value
            for key, value in update_data.items()
            if key in allowed_fields
        }

        if not filtered_data:
            return organization

        return OrganizationRepository.update_organization(
            db,
            organization,
            filtered_data,
        )

    @staticmethod
    def get_settings(
        db: Session,
        organization_id: str,
        current_user: User,
    ):
        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        OrganizationService._ensure_organization_access(
            db,
            organization,
            current_user,
        )

        return {
            "organization_id": organization.id,
            "organization_name": organization.name,
            "organization_type": organization.organization_type,
            "industry": organization.industry,
            "website": organization.website,
            "contact_email": organization.contact_email,
            "contact_phone": organization.contact_phone,
            "country": organization.country,
            "state": organization.state,
            "address": organization.address,
            "gstin": organization.gstin,
            "email_domain": organization.email_domain,
            "email_verified": organization.email_verified,
            "verification_status": organization.verification_status,
        }

    @staticmethod
    def get_verification(
        db: Session,
        organization_id: str,
        current_user: User,
    ):
        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        OrganizationService._ensure_organization_access(
            db,
            organization,
            current_user,
        )

        verification = (
            db.query(OrganizationVerification)
            .filter(
                OrganizationVerification.organization_id
                == organization_id
            )
            .first()
        )

        return {
            "organization_id": organization.id,
            "verification_status": organization.verification_status,
            "email_verified": organization.email_verified,
            "verified_at": organization.verified_at,
            "verification": verification,
        }

    # ============================================================
    # Module 1 - Professional Email
    # ============================================================

    FREE_EMAIL_PROVIDERS = {
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "live.com",
        "icloud.com",
        "protonmail.com",
        "proton.me",
        "rediffmail.com",
    }

    @staticmethod
    def get_email_domain(email: str) -> str:

        return EmailService.get_domain(
            email
        )

        return email.split("@", 1)[1]

    @staticmethod
    def validate_professional_email(email: str):

            return EmailService.validate_professional_email(
            email
        )

    # ============================================================
    # Module 1 - Organization Registration
    # ============================================================

    @staticmethod
    def _generate_organization_id(db: Session) -> str:
        """
        Generate IDs such as ORG_001, ORG_002, etc.
        """

        organizations = (
            db.query(Organization)
            .filter(Organization.id.like("ORG_%"))
            .all()
        )

        max_number = 0

        for organization in organizations:
            try:
                number = int(organization.id.split("_")[1])
                max_number = max(max_number, number)
            except (IndexError, ValueError):
                continue

        return f"ORG_{max_number + 1:03d}"

    @staticmethod
    def create_organization(
        db: Session,
        organization_data: dict,
    ):
        """
        Create organization and generate initial email OTP.
        """

        contact_email = (
            organization_data.get("contact_email")
            or organization_data.get("email")
        )

        if not contact_email:
            raise ValueError("Organization email is required")

        contact_email = str(contact_email).strip().lower()

        # Validate professional email
        email_validation = (
            OrganizationService.validate_professional_email(
                contact_email
            )
        )

        email_domain = email_validation["domain"]

        # Check duplicate email
        existing_email_org = OrganizationRepository.get_by_email(
            db,
            contact_email,
        )

        if existing_email_org:
            raise ValueError(
                "An organization with this email already exists"
            )

        # Check duplicate registration number
        registration_number = organization_data.get(
            "registration_number"
        )

        if registration_number:
            existing_registration = (
                OrganizationRepository.get_by_registration_number(
                    db,
                    registration_number,
                )
            )

            if existing_registration:
                raise ValueError(
                    "An organization with this registration number "
                    "already exists"
                )

        # Generate organization ID
        organization_id = OrganizationService._generate_organization_id(
            db
        )

        # Create organization
        organization = Organization(
            id=organization_id,
            name=organization_data["name"],
            organization_type=organization_data.get(
                "organization_type"
            ),
            registration_number=registration_number,
            industry=organization_data.get("industry"),
            website=organization_data.get("website"),
            contact_email=contact_email,
            contact_phone=organization_data.get("contact_phone"),
            address=organization_data.get("address"),
            country=organization_data.get("country"),
            state=organization_data.get("state"),
            gstin=organization_data.get("gstin"),
            email_domain=email_domain,
            email_verified=False,
            verification_status="PENDING",
        )

        organization = OrganizationRepository.create(
            db,
            organization,
        )

        # Generate OTP
        otp = OTPService.generate_otp()

        otp_hash = OTPService.hash_otp(otp)

        expires_at = OTPService.get_expiry_time()

        resend_available_at = (
            OTPService.get_resend_available_time()
        )

        # Save OTP
        OTPRepository.create(
            db=db,
            organization_id=organization.id,
            email=contact_email,
            otp_hash=otp_hash,
            expires_at=expires_at,
            resend_available_at=resend_available_at,
            max_attempts=OTPService.MAX_OTP_ATTEMPTS,
        )

        # Temporary development response.
        # Later this will be replaced by email sending.
        return {
            "organization": organization,
            "otp": otp,
        }

    # ============================================================
    # Module 1 - OTP Verification
    # ============================================================

    @staticmethod
    def verify_organization_email(
        db: Session,
        organization_id: str,
        otp: str,
    ):
        """
        Verify the OTP generated for an organization.
        """

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        otp_record = OTPRepository.get_latest_for_organization(
            db,
            organization_id,
        )

        if not otp_record:
            raise ValueError(
                "No OTP found. Please request a new OTP"
            )

        if otp_record.verified:
            raise ValueError(
                "OTP has already been verified"
            )

        if OTPService.is_expired(otp_record.expires_at):
            raise ValueError(
                "OTP has expired. Please request a new OTP"
            )

        if not OTPService.can_attempt(otp_record.attempts):
            raise ValueError(
                "Maximum OTP attempts exceeded"
            )

        # Count this verification attempt
        OTPRepository.increment_attempts(
            db,
            otp_record,
        )

        # Compare OTP hash
        if not OTPService.verify_otp(
            otp,
            otp_record.otp_hash,
        ):
            raise ValueError("Invalid OTP")

        # Mark OTP as verified
        OTPRepository.mark_verified(
            db,
            otp_record,
        )

        # Mark organization email as verified
        OrganizationRepository.mark_email_verified(
            db,
            organization,
        )

        return {
            "organization_id": organization.id,
            "email_verified": True,
            "verification_status": organization.verification_status,
            "message": "Email verified successfully",
        }

    # ============================================================
    # Module 1 - OTP Resend
    # ============================================================

    @staticmethod
    def resend_organization_otp(
        db: Session,
        organization_id: str,
    ):
        """
        Generate and save a new OTP after checking the resend
        cooldown.
        """

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        if organization.email_verified:
            raise ValueError(
                "Organization email is already verified"
            )

        latest_otp = OTPRepository.get_latest_for_organization(
            db,
            organization_id,
        )

        # Check resend cooldown
        if latest_otp and not OTPService.can_resend(
            latest_otp.resend_available_at
        ):
            seconds_remaining = (
                OTPService.seconds_until_resend(
                    latest_otp.resend_available_at
                )
            )

            raise ValueError(
                f"Please wait {seconds_remaining} seconds "
                "before requesting another OTP"
            )

        # Invalidate old OTP
        if latest_otp:
            OTPRepository.invalidate_previous_otps(
                db,
                organization_id,
            )

        # Generate new OTP
        otp = OTPService.generate_otp()

        otp_hash = OTPService.hash_otp(otp)

        expires_at = OTPService.get_expiry_time()

        resend_available_at = (
            OTPService.get_resend_available_time()
        )

        # Save new OTP
        OTPRepository.create(
            db=db,
            organization_id=organization_id,
            email=organization.contact_email,
            otp_hash=otp_hash,
            expires_at=expires_at,
            resend_available_at=resend_available_at,
            max_attempts=OTPService.MAX_OTP_ATTEMPTS,
        )

        return {
            "organization_id": organization_id,
            "message": "A new OTP has been generated",
            "development_otp": otp,
        }
        # ============================================================
    # Organization Verification Submission
    # ============================================================

    @staticmethod
    def submit_verification(
        db: Session,
        organization_id: str,
        verification_data: dict,
    ):

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        if not organization.email_verified:
            raise ValueError(
                "Email must be verified before submitting organization verification"
            )

        verification = (
            db.query(OrganizationVerification)
            .filter(
                OrganizationVerification.organization_id
                == organization_id
            )
            .first()
        )

        if verification:
            verification.registration_number = (
                verification_data.get(
                    "registration_number"
                )
                or organization.registration_number
            )

            verification.verification_type = (
                verification_data.get(
                    "verification_type"
                )
                or "ORGANIZATION"
            )

            verification.status = "UNDER_REVIEW"

        else:
            verification = OrganizationVerification(
                organization_id=organization_id,
                verification_type=verification_data.get(
                    "verification_type",
                    "ORGANIZATION",
                ),
                registration_number=verification_data.get(
                    "registration_number"
                ),
                status="UNDER_REVIEW",
            )

            db.add(verification)

        organization.verification_status = "UNDER_REVIEW"

        db.commit()

        db.refresh(verification)

        return {
            "organization_id": organization_id,
            "verification_id": verification.id,
            "status": verification.status,
        }

    @staticmethod
    def get_verification_status(
            db: Session,
        organization_id: str,
        ):

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        verification = (
            db.query(OrganizationVerification)
            .filter(
                OrganizationVerification.organization_id
                == organization_id
            )
            .first()
        )

        if not verification:
            return {
                "organization_id": organization_id,
                "verification_id": None,
                "status": organization.verification_status,
                "submitted_at": None,
                "updated_at": None,
            }

        return {
            "organization_id": organization_id,
            "verification_id": verification.id,
            "status": verification.status,
            "submitted_at": getattr(
                verification,
                "created_at",
                None,
            ),
            "updated_at": getattr(
                verification,
                "updated_at",
                None,
            ),
        }


@staticmethod
def verify_company(
    db,
    organization_id: str,
):
    organization = OrganizationRepository.get_organization(
        db,
        organization_id,
    )

    if not organization:
        raise ValueError("Organization not found.")

    if not organization.email_verified:
        raise ValueError(
            "Organization email must be verified first."
        )

    result = lookup_company(
        company_name=organization.name,
        cin=organization.registration_number,
    )

    if not result["found"]:
        return {
            "organization_id": organization.id,
            "verified": False,
            "status": "REJECTED",
            "message": result["error"],
            "company": None,
        }

    organization.verification_status = "VERIFIED"
    organization.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(organization)

    return {
        "organization_id": organization.id,
        "verified": True,
        "status": "VERIFIED",
        "message": "Organization successfully verified.",
        "company": result["company"],
    }