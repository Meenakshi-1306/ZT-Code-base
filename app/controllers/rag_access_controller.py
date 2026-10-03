from typing import Any

from sqlalchemy.orm import Session

from app.services.rag_access_service import RagAccessService


class RagAccessController:

    def __init__(self):
        self.service = RagAccessService()

    def check_access(
        self,
        db: Session,
        user_id: str,
        organization_id: str,
        resource: str,
        action: str,
        resource_type: str = "resource",
        context: dict[str, Any] | None = None,
    ):
        return self.service.check_access(
            db=db,
            user_id=user_id,
            organization_id=organization_id,
            resource=resource,
            action=action,
            resource_type=resource_type,
            context=context,
        )