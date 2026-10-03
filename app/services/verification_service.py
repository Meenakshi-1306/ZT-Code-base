from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.organization_verification import OrganizationVerification
from app.models.verification_document import VerificationDocument

from app.repositories.organization_repository import (
    OrganizationRepository,
)

from app.repositories.verification_repository import (
    VerificationRepository,
)


class VerificationService:

    # ============================================================
    # SUBMIT ORGANIZATION VERIFICATION
    # ============================================================

    @staticmethod
    def submit_verification(
        db: Session,
        organization_id: str,
        verification_type: str,
        registration_number: str | None = None,
    ):

        # --------------------------------------------------------
        # Check organization
        # --------------------------------------------------------

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        # --------------------------------------------------------
        # Email must be verified first
        # --------------------------------------------------------

        if not organization.email_verified:
            raise ValueError(
                "Email must be verified before submitting organization verification"
            )

        # --------------------------------------------------------
        # Check existing verification
        # --------------------------------------------------------

        existing_verification = (
            VerificationRepository.get_verification_by_organization(
                db,
                organization_id,
            )
        )

        # --------------------------------------------------------
        # Already verified
        # --------------------------------------------------------

        if (
            existing_verification
            and existing_verification.status.lower() == "verified"
        ):
            raise ValueError(
                "Organization is already verified"
            )

        # --------------------------------------------------------
        # Update existing verification
        # --------------------------------------------------------

        if existing_verification:

            verification = (
                VerificationRepository.update_verification(
                    db,
                    existing_verification,
                    {
                        "verification_type": verification_type,
                        "registration_number": registration_number,
                        "status": "under_review",
                        "updated_at": datetime.utcnow(),
                    },
                )
            )

        # --------------------------------------------------------
        # Create new verification
        # --------------------------------------------------------

        else:

            verification = OrganizationVerification(
                id=f"VER_{uuid4().hex[:10].upper()}",
                organization_id=organization_id,
                verification_type=verification_type,
                registration_number=registration_number,
                status="under_review",
            )

            verification = (
                VerificationRepository.create_verification(
                    db,
                    verification,
                )
            )

        # --------------------------------------------------------
        # Update organization verification status
        # --------------------------------------------------------

        OrganizationRepository.update_verification_status(
            db,
            organization,
            "UNDER_REVIEW",
        )

        # --------------------------------------------------------
        # Return API-friendly response
        # --------------------------------------------------------

        return {
            "organization_id": organization_id,
            "verification_id": verification.id,
            "status": verification.status,
            "verification_type": verification.verification_type,
            "registration_number": verification.registration_number,
            "submitted_at": verification.created_at,
            "updated_at": verification.updated_at,
            "message": "Organization verification submitted successfully",
        }

    # ============================================================
    # GET VERIFICATION STATUS
    # ============================================================

    @staticmethod
    def get_verification_status(
        db: Session,
        organization_id: str,
    ):

        # --------------------------------------------------------
        # Check organization
        # --------------------------------------------------------

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        # --------------------------------------------------------
        # Get verification
        # --------------------------------------------------------

        verification = (
            VerificationRepository.get_verification_by_organization(
                db,
                organization_id,
            )
        )

        # --------------------------------------------------------
        # Get documents
        # --------------------------------------------------------

        documents = (
            VerificationRepository.get_documents_by_organization(
                db,
                organization_id,
            )
        )

        return {
            "organization_id": organization_id,
            "organization_status": organization.verification_status,
            "verification": verification,
            "documents": documents,
        }

    # ============================================================
    # UPLOAD VERIFICATION DOCUMENT
    # ============================================================

    @staticmethod
    async def upload_document(
        db: Session,
        organization_id: str,
        document_type: str,
        document: UploadFile,
    ):

        # --------------------------------------------------------
        # Check organization
        # --------------------------------------------------------

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError("Organization not found")

        # --------------------------------------------------------
        # Email verification required
        # --------------------------------------------------------

        if not organization.email_verified:
            raise ValueError(
                "Email must be verified before uploading verification documents"
            )

        # --------------------------------------------------------
        # Check verification record
        # --------------------------------------------------------

        verification = (
            VerificationRepository.get_verification_by_organization(
                db,
                organization_id,
            )
        )

        if not verification:
            raise ValueError(
                "Submit organization verification before uploading documents"
            )

        # --------------------------------------------------------
        # Validate filename
        # --------------------------------------------------------

        if not document.filename:
            raise ValueError(
                "Document filename is required"
            )

        # --------------------------------------------------------
        # Validate extension
        # --------------------------------------------------------

        allowed_extensions = {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
        }

        extension = Path(
            document.filename
        ).suffix.lower()

        if extension not in allowed_extensions:
            raise ValueError(
                "Only PDF, PNG, JPG and JPEG files are allowed"
            )

        # --------------------------------------------------------
        # Create upload directory
        # --------------------------------------------------------

        upload_directory = (
            Path("uploads") / "verification"
        )

        upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # Generate unique filename
        # --------------------------------------------------------

        unique_filename = (
            f"{organization_id}_"
            f"{uuid4().hex}"
            f"{extension}"
        )

        file_path = (
            upload_directory /
            unique_filename
        )

        # --------------------------------------------------------
        # Read uploaded file
        # --------------------------------------------------------

        try:

            contents = await document.read()

        except Exception as exc:

            raise ValueError(
                f"Failed to read uploaded document: {str(exc)}"
            )

        # --------------------------------------------------------
        # Save file
        # --------------------------------------------------------

        try:

            with open(
                file_path,
                "wb",
            ) as file:

                file.write(contents)

        except Exception as exc:

            raise ValueError(
                f"Failed to save document: {str(exc)}"
            )

        # --------------------------------------------------------
        # Create database record
        # --------------------------------------------------------

        verification_document = VerificationDocument(
            id=f"DOC_{uuid4().hex[:10].upper()}",
            organization_id=organization_id,
            document_type=document_type,
            document_name=document.filename,
            document_path=str(file_path),
            status="pending",
        )

        verification_document = (
            VerificationRepository.create_document(
                db,
                verification_document,
            )
        )

        # --------------------------------------------------------
        # If verification was pending, move it to under_review
        # --------------------------------------------------------

        if verification.status.lower() == "pending":

            VerificationRepository.update_verification(
                db,
                verification,
                {
                    "status": "under_review",
                    "updated_at": datetime.utcnow(),
                },
            )

            OrganizationRepository.update_verification_status(
                db,
                organization,
                "UNDER_REVIEW",
            )

        # --------------------------------------------------------
        # Return API response
        # --------------------------------------------------------

        return {
            "document_id": verification_document.id,
            "organization_id": verification_document.organization_id,
            "document_type": verification_document.document_type,
            "document_name": verification_document.document_name,
            "document_path": verification_document.document_path,
            "status": verification_document.status,
            "uploaded_at": verification_document.uploaded_at,
        }

    # ============================================================
    # UPDATE VERIFICATION STATUS
    # ============================================================

    @staticmethod
    def update_verification_status(
        db: Session,
        organization_id: str,
        status: str,
    ):

        # --------------------------------------------------------
        # Allowed statuses
        # --------------------------------------------------------

        allowed_statuses = {
            "pending",
            "under_review",
            "verified",
            "rejected",
        }

        normalized_status = status.lower()

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid verification status. "
                "Allowed values: pending, under_review, "
                "verified, rejected"
            )

        # --------------------------------------------------------
        # Check organization
        # --------------------------------------------------------

        organization = OrganizationRepository.get_organization(
            db,
            organization_id,
        )

        if not organization:
            raise ValueError(
                "Organization not found"
            )

        # --------------------------------------------------------
        # Get verification
        # --------------------------------------------------------

        verification = (
            VerificationRepository.get_verification_by_organization(
                db,
                organization_id,
            )
        )

        if not verification:
            raise ValueError(
                "Verification record not found"
            )

        # --------------------------------------------------------
        # Update verification
        # --------------------------------------------------------

        verification = (
            VerificationRepository.update_verification(
                db,
                verification,
                {
                    "status": normalized_status,
                    "updated_at": datetime.utcnow(),
                },
            )
        )

        # --------------------------------------------------------
        # Map status to organization status
        # --------------------------------------------------------

        organization_status_map = {
            "pending": "PENDING",
            "under_review": "UNDER_REVIEW",
            "verified": "VERIFIED",
            "rejected": "REJECTED",
        }

        OrganizationRepository.update_verification_status(
            db,
            organization,
            organization_status_map[
                normalized_status
            ],
        )

        # --------------------------------------------------------
        # Store verification timestamp
        # --------------------------------------------------------

        if normalized_status == "verified":

            organization.verified_at = datetime.utcnow()

            db.commit()
            db.refresh(organization)

        return verification