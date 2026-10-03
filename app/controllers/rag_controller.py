from typing import Any

from sqlalchemy.orm import Session

class RagController:

    def __init__(self):
        self._service = None

    @property
    def service(self):
        if self._service is None:
            from app.services.rag_service import RagApplicationService
            self._service = RagApplicationService()
        return self._service

    # ============================================================
    # DOCUMENT UPLOAD
    # ============================================================

    def upload_document(
        self,
        db: Session,
        organization_id: str,
        filename: str,
        original_filename: str,
        file_path: str,
        uploaded_by: str | None = None,
    ):

        return (
            self.service.create_document(
                db=db,
                organization_id=organization_id,
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                uploaded_by=uploaded_by,
            )
        )

    # ============================================================
    # DOCUMENT LIST
    # ============================================================

    def list_documents(
        self,
        db: Session,
        organization_id: str,
    ):

        return (
            self.service.list_documents(
                db=db,
                organization_id=organization_id,
            )
        )

    # ============================================================
    # DOCUMENT GET
    # ============================================================

    def get_document(
        self,
        db: Session,
        organization_id: str,
        document_id: str,
    ):

        return (
            self.service.get_document(
                db=db,
                document_id=document_id,
                organization_id=organization_id,
            )
        )

    # ============================================================
    # DOCUMENT DELETE
    # ============================================================

    def delete_document(
        self,
        db: Session,
        organization_id: str,
        document_id: str,
    ):

        return (
            self.service.delete_document(
                db=db,
                document_id=document_id,
                organization_id=organization_id,
            )
        )

    # ============================================================
    # QUESTION + ANSWER
    # ============================================================

    def query(
        self,
        question: str,
        organization_id: str,
        top_k: int = 5,
    ):

        return (
            self.service.query(
                question=question,
                organization_id=organization_id,
                top_k=top_k,
            )
        )

    # ============================================================
    # DATA ACCESS / PRIVILEGE CHECK
    # ============================================================

    def check_access(
        self,
        db: Session,
        user_id: str,
        organization_id: str,
        resource: str,
        resource_type: str,
        action: str,
        context: dict[str, Any] | None = None,
    ):

        return (
            self.service.check_access(
                db=db,
                user_id=user_id,
                organization_id=organization_id,
                resource=resource,
                resource_type=resource_type,
                action=action,
                context=context,
            )
        )