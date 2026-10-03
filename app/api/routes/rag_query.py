from fastapi import (
    APIRouter,
    HTTPException,
)

from app.controllers.rag_query_controller import (
    RagQueryController,
)

from app.schemas.rag_query import (
    RagQueryRequest,
)

from app.schemas.rag_response import (
    RagQueryResponse,
)

from app.services.rag_risk_service import (
    RagRiskService,
)


router = APIRouter(
    prefix="/api",
    tags=["RAG"],
)

controller = RagQueryController()

risk_service = RagRiskService()


@router.post(
    "/organizations/{organization_id}/rag/query",
    response_model=RagQueryResponse,
)
def query_rag(
    organization_id: str,
    request: RagQueryRequest,
):
    try:

        result = risk_service.query(
            question=request.question,
            top_k=request.top_k,
        )

        return {
            "organization_id": organization_id,
            **result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"RAG query failed: {str(exc)}",
        )