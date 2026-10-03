from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# ================================================================
# SCHEMAS
# ================================================================

class MLPredictRequest(BaseModel):
    source: str = "organization_logs"
    data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


class MLPredictResponse(BaseModel):
    success: bool
    models: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)


# ================================================================
# ROUTER
# ================================================================

router = APIRouter(
    prefix="/api/ml-models",
    tags=["ML Models"],
)


# ================================================================
# PREDICT
# ================================================================

@router.post(
    "/predict",
)
def predict(request: MLPredictRequest):
    """
    Execute predictions on all applicable
    trained ML models.
    """

    try:

        from app.ml.model_service import model_service

        result = model_service.predict(
            source=request.source,
            data=request.data,
            context=request.context,
        )

        return {
            "success": True,
            **result,
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "ML model prediction failed: "
                f"{str(e)}"
            ),
        )


# ================================================================
# MODEL STATUS
# ================================================================

@router.get(
    "/status",
)
def get_model_status():
    """
    Return loading status of all trained ML models.
    """

    try:

        from app.ml.model_service import model_service

        return {
            "success": True,
            "models": model_service.get_model_status(),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve model status: "
                f"{str(e)}"
            ),
        )
