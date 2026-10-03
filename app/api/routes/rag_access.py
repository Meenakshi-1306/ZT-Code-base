from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.database import SessionLocal

from app.controllers.rag_access_controller import (
    RagAccessController,
)

from app.schemas.rag_access import (
    RagAccessCheckRequest,
    RagAccessCheckResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["RAG Access Control"],
)

controller = RagAccessController()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user_id():
    """
    TEMPORARY PLACEHOLDER.

    Replace this with your project's existing
    current-user authentication dependency.

    Do NOT create another authentication system.
    """

    return None


@router.post(
    "/organizations/{organization_id}/rag/access-check",
    response_model=RagAccessCheckResponse,
)
def check_rag_access(
    organization_id: str,
    request: RagAccessCheckRequest,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
):
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    try:
        result = controller.check_access(
            db=db,
            user_id=user_id,
            organization_id=organization_id,
            resource=request.resource,
            action=request.action,
            resource_type=request.resource_type,
            context=request.context,
        )

        return {
            "organization_id": organization_id,
            "user_id": user_id,
            "resource": request.resource,
            "resource_type": request.resource_type,
            "action": request.action,
            **result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Access check failed: {str(exc)}",
        )