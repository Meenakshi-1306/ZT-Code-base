import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.rag_document import RagDocument

from app.repositories.rag_document_repository import (
    RagDocumentRepository,
)

from app.rag.rag_service import (
    RagService as VectorRagService,
)

from app.rag.risk_engine import (
    assess_risk,
)

from app.services.rbac_service import (
    RBACService,
)


class RagApplicationService:

    def __init__(self):

        self.repository = (
            RagDocumentRepository()
        )

        self.rag_engine = (
            VectorRagService()
        )

        self.rbac_service = (
            RBACService()
        )

    # ============================================================
    # DOCUMENT MANAGEMENT
    # ============================================================

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

        document = (
            self.repository.create(
                db,
                document,
            )
        )

        try:

            result = (
                self.rag_engine.index_document(
                    file_path=file_path,
                    organization_id=organization_id,
                    document_id=document_id,
                )
            )

            document.standard = (
                result["standard"]
            )

            document.version = (
                result["version"]
            )

            document.pages = (
                result["pages"]
            )

            document.chunks = (
                result["chunks"]
            )

            document.status = "indexed"

            db.commit()
            db.refresh(document)

            return document

        except Exception:

            document.status = "failed"

            db.commit()
            db.refresh(document)

            raise

    # ============================================================
    # GET DOCUMENT
    # ============================================================

    def get_document(
        self,
        db: Session,
        document_id: str,
        organization_id: str,
    ):

        return (
            self.repository
            .get_by_id_and_organization(
                db=db,
                document_id=document_id,
                organization_id=organization_id,
            )
        )

    # ============================================================
    # LIST DOCUMENTS
    # ============================================================

    def list_documents(
        self,
        db: Session,
        organization_id: str,
    ):

        return (
            self.repository
            .get_by_organization(
                db=db,
                organization_id=organization_id,
            )
        )

    # ============================================================
    # DELETE DOCUMENT
    # ============================================================

    def delete_document(
        self,
        db: Session,
        document_id: str,
        organization_id: str,
    ):

        document = self.get_document(
            db=db,
            document_id=document_id,
            organization_id=organization_id,
        )

        if document is None:
            return None

        self.repository.delete(
            db=db,
            document=document,
        )

        return document

    # ============================================================
    # RAG QUESTION + ANSWER
    # ============================================================

    def query(
        self,
        question: str,
        organization_id: str,
        top_k: int = 5,
    ):

        retrieved_documents = (
            self.rag_engine.query(
                question=question,
                organization_id=organization_id,
                top_k=top_k,
            )
        )

        if not retrieved_documents:

            raise ValueError(
                "No relevant compliance documents "
                "were found for this organization."
            )

        risk_result = assess_risk(
            question=question,
            retrieved_documents=retrieved_documents,
        )

        return {
            "question": question,

            "answer": risk_result[
                "answer"
            ],

            "compliance": risk_result[
                "compliance"
            ],

            "risk_assessment": risk_result[
                "risk_assessment"
            ],

            "recommendation": risk_result[
                "recommendation"
            ],

            "risk_explanation": risk_result[
                "risk_explanation"
            ],

            "results": retrieved_documents,
        }

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

        context = context or {}

        permission_name = (
            f"{resource}:{action}"
        )

        # --------------------------------------------------------
        # EXISTING RBAC SYSTEM
        # --------------------------------------------------------

        try:

            has_permission = (
                self.rbac_service
                .user_has_permission(
                    db=db,
                    user_id=user_id,
                    organization_id=organization_id,
                    permission_name=permission_name,
                )
            )

        except TypeError:

            # Compatibility with an existing
            # RBACService using positional arguments.

            has_permission = (
                self.rbac_service
                .user_has_permission(
                    db,
                    user_id,
                    organization_id,
                    permission_name,
                )
            )

        # --------------------------------------------------------
        # RISK SCORE
        # --------------------------------------------------------

        if has_permission:

            risk_score = (
                self._calculate_access_risk(
                    context=context,
                    access_granted=True,
                )
            )

        else:

            risk_score = 90.0

        risk_level = (
            self._get_risk_level(
                risk_score
            )
        )

        # --------------------------------------------------------
        # ACCESS GRANTED
        # --------------------------------------------------------

        if has_permission:

            return {
                "access_granted": True,

                "permission":
                    permission_name,

                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "reason": (
                    "The user has the required "
                    f"permission '{permission_name}'."
                ),

                "recommendation": (
                    "Access may proceed subject to "
                    "contextual Zero Trust controls."
                ),

                "context":
                    context,
            }

        # --------------------------------------------------------
        # ACCESS DENIED
        # --------------------------------------------------------

        return {
            "access_granted": False,

            "permission":
                permission_name,

            "risk_level":
                risk_level,

            "risk_score":
                risk_score,

            "reason": (
                "The user does not have the required "
                f"permission '{permission_name}'."
            ),

            "recommendation": (
                "Deny access and review the user's "
                "organization role and permissions."
            ),

            "context":
                context,
        }

    # ============================================================
    # ACCESS RISK
    # ============================================================

    def _calculate_access_risk(
        self,
        context: dict[str, Any],
        access_granted: bool,
    ) -> float:

        if not access_granted:
            return 90.0

        score = 20.0

        if context.get(
            "unusual_time"
        ):
            score += 15

        if context.get(
            "untrusted_device"
        ):
            score += 20

        if context.get(
            "unusual_location"
        ):
            score += 15

        if context.get(
            "multiple_failed_logins"
        ):
            score += 20

        if context.get(
            "sensitive_resource"
        ):
            score += 10

        return min(
            score,
            100.0,
        )

    # ============================================================
    # RISK LEVEL
    # ============================================================

    def _get_risk_level(
        self,
        score: float,
    ) -> str:

        if score >= 70:
            return "HIGH"

        if score >= 40:
            return "MEDIUM"

        return "LOW"