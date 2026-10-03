from sqlalchemy.orm import Session

from app.models.organization_verification import OrganizationVerification
from app.models.verification_document import VerificationDocument


class VerificationRepository:

    # ---------------------------------------------------------
    # ORGANIZATION VERIFICATION
    # ---------------------------------------------------------

    @staticmethod
    def get_verification_by_organization(
        db: Session,
        organization_id: str
    ):
        return (
            db.query(OrganizationVerification)
            .filter(
                OrganizationVerification.organization_id == organization_id
            )
            .order_by(OrganizationVerification.created_at.desc())
            .first()
        )

    @staticmethod
    def create_verification(
        db: Session,
        verification: OrganizationVerification
    ):
        db.add(verification)
        db.commit()
        db.refresh(verification)

        return verification

    @staticmethod
    def update_verification(
        db: Session,
        verification: OrganizationVerification,
        update_data: dict
    ):
        for field, value in update_data.items():
            if hasattr(verification, field):
                setattr(verification, field, value)

        db.commit()
        db.refresh(verification)

        return verification

    # ---------------------------------------------------------
    # VERIFICATION DOCUMENTS
    # ---------------------------------------------------------

    @staticmethod
    def create_document(
        db: Session,
        document: VerificationDocument
    ):
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def get_documents_by_organization(
        db: Session,
        organization_id: str
    ):
        return (
            db.query(VerificationDocument)
            .filter(
                VerificationDocument.organization_id == organization_id
            )
            .order_by(VerificationDocument.uploaded_at.desc())
            .all()
        )

    @staticmethod
    def get_document(
        db: Session,
        document_id: str
    ):
        return (
            db.query(VerificationDocument)
            .filter(
                VerificationDocument.id == document_id
            )
            .first()
        )

    @staticmethod
    def update_document_status(
        db: Session,
        document: VerificationDocument,
        status: str
    ):
        document.status = status

        db.commit()
        db.refresh(document)

        return document