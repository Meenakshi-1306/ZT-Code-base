from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# ================================================================
# SCHEMAS
# ================================================================

class RiskCalculateRequest(BaseModel):
    model_results: Dict[str, Any] = Field(default_factory=dict)
    event_data: Dict[str, Any] = Field(default_factory=dict)


class RiskEvaluateRequest(BaseModel):
    source: str = "organization_logs"
    data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


# ================================================================
# ROUTER
# ================================================================

router = APIRouter(
    prefix="/api/risk-engine",
    tags=["Risk Engine"],
)


# ================================================================
# CALCULATE RISK
# ================================================================

@router.post(
    "/calculate",
)
def calculate_risk(request: RiskCalculateRequest):
    """
    Calculate risk from model results and event data.

    Expects pre-computed model outputs.
    """

    try:

        from app.ml.risk_engine import risk_engine

        result = risk_engine.calculate_risk(
            model_results=request.model_results,
            event_data=request.event_data,
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
                "Risk calculation failed: "
                f"{str(e)}"
            ),
        )


# ================================================================
# END-TO-END EVALUATE
# ================================================================

@router.post(
    "/evaluate",
)
def evaluate_risk(request: RiskEvaluateRequest):
    """
    End-to-end pipeline:
        1. Execute ML model predictions
        2. Calculate contextual risk
        3. Return final operational risk score and severity
    """

    try:

        from app.ml.model_service import model_service
        from app.ml.risk_engine import risk_engine

        # Step 1: Model prediction
        model_response = model_service.predict(
            source=request.source,
            data=request.data,
            context=request.context,
        )

        model_results = model_response.get(
            "models",
            {},
        )

        # Step 2: Risk calculation
        risk_response = risk_engine.calculate_risk(
            model_results=model_results,
            event_data=request.data,
        )

        return {
            "success": True,
            "model_response": model_response,
            "risk_response": risk_response,
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
                "Risk evaluation failed: "
                f"{str(e)}"
            ),
        )
