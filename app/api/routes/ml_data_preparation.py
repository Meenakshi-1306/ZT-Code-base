from fastapi import APIRouter, HTTPException

from app.ml.schema.ml_data_preparation_schema import (
    MLDataPreparationRequest,
    MLDataPreparationResponse,
)


# ================================================================
# ROUTER
# ================================================================

router = APIRouter(
    prefix="/api/ml-data-preparation",
    tags=["ML Data Preparation"],
)


# ================================================================
# PREPARE ORGANIZATION DATA
# ================================================================

@router.post(
    "/prepare",
    response_model=MLDataPreparationResponse,
)
def prepare_ml_data(
    request: MLDataPreparationRequest,
):
    """
    Prepare heterogeneous organization data
    for the appropriate ML models.

    The organization does NOT need to provide
    the exact trained-model feature names.

    The service handles:

        1. Exact match
        2. Alias match
        3. Semantic match
        4. Feature derivation
        5. Historical / local statistics
        6. Feature-specific defaults
        7. Unavailable features
    """

    try:

        from app.ml.controller.ml_data_preparation_controller import (
            ml_data_preparation_controller,
        )

        result = ml_data_preparation_controller.prepare_data(
            organization_id=request.organization_id,
            source=request.source,
            data=request.data,
            context=request.context,
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "ML data preparation failed: "
                f"{str(e)}"
            ),
        )


# ================================================================
# MODEL SCHEMA
# ================================================================

@router.get(
    "/model-schema",
)
def get_model_schema():
    """
    Return the actual feature schemas discovered
    from the trained ML models.
    """

    try:

        from app.ml.controller.ml_data_preparation_controller import (
            ml_data_preparation_controller,
        )

        return ml_data_preparation_controller.get_model_schema()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve model schema: "
                f"{str(e)}"
            ),
        )
