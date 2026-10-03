import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.rag_document import RagDocument

from app.repositories.rag_document_repository import (
    RagDocumentRepository,
)

from app.rag.rag_service import RagService


class RagDocumentService:

    def __init__(self):

        self.repository = RagDocumentRepository()

        self.rag_service = RagService()

    def create_document(
        self,
        db: Session,
        organization_id: str,
        filename: str,
        original_filename: str,
        file_path: str,
        uploaded_by: str | None = None,
    ):

        document_id = str(
            uuid.uuid4()
        )

        document = RagDocument(
            id=document_id,
            organization_id=organization_id,
            filename=filename,
            original_filename=original_filename,
            standard=None,
            version=None,
            pages=0,
            chunks=0,
            file_path=file_path,
            status="processing",
            uploaded_by=uploaded_by,
        )

        document = self.repository.create(
            db,
            document,
        )

        try:

            result = self.rag_service.index_document(
                file_path=file_path,
            )

            document.standard = result[
                "standard"
            ]

            document.version = result[
                "version"
            ]

            document.pages = result[
                "pages"
            ]

            document.chunks = result[
                "chunks"
            ]

            document.status = "indexed"

            db.commit()

            db.refresh(document)

            return document

        except Exception:

            document.status = "failed"

            db.commit()

            db.refresh(document)

            raise

    def get_document(
        self,
        db: Session,
        document_id: str,
    ):

        return self.repository.get_by_id(
            db,
            document_id,
        )

    def list_documents(
        self,
        db: Session,
        organization_id: str,
    ):

        return self.repository.get_by_organization(
            db,
            organization_id,
        )

    def delete_document(
        self,
        db: Session,
        document: RagDocument,
    ):

        self.repository.delete(
            db,
            document,
        )