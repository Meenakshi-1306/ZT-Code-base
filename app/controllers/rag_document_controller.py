from sqlalchemy.orm import Session

from app.services.rag_document_service import RagDocumentService


class RagDocumentController:

    def __init__(self):
        self.service = RagDocumentService()

    def create_document(
        self,
        db: Session,
        organization_id: str,
        filename: str,
        original_filename: str,
        file_path: str,
        uploaded_by: str | None = None,
        standard: str | None = None,
        version: str | None = None,
    ):
        return self.service.create_document(
            db=db,
            organization_id=organization_id,
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            uploaded_by=uploaded_by,
            standard=standard,
            version=version,
        )

    def get_document(
        self,
        db: Session,
        document_id: str,
    ):
        return self.service.get_document(
            db=db,
            document_id=document_id,
        )

    def list_documents(
        self,
        db: Session,
        organization_id: str,
    ):
        return self.service.list_documents(
            db=db,
            organization_id=organization_id,
        )

    def delete_document(
        self,
        db: Session,
        document_id: str,
    ):
        document = self.service.get_document(
            db=db,
            document_id=document_id,
        )

        if not document:
            return None

        self.service.delete_document(
            db=db,
            document=document,
        )

        return document