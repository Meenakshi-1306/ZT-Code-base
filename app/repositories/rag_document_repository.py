from sqlalchemy.orm import Session

from app.models.rag_document import RagDocument


class RagDocumentRepository:

    def create(
        self,
        db: Session,
        document: RagDocument,
    ) -> RagDocument:

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def get_by_id(
        self,
        db: Session,
        document_id: str,
    ) -> RagDocument | None:

        return (
            db.query(RagDocument)
            .filter(RagDocument.id == document_id)
            .first()
        )

    def get_by_organization(
        self,
        db: Session,
        organization_id: str,
    ) -> list[RagDocument]:

        return (
            db.query(RagDocument)
            .filter(
                RagDocument.organization_id == organization_id
            )
            .order_by(RagDocument.created_at.desc())
            .all()
        )

    def delete(
        self,
        db: Session,
        document: RagDocument,
    ) -> None:

        db.delete(document)
        db.commit()