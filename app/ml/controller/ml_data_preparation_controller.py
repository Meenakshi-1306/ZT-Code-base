from typing import Any, Dict

from app.ml.service.ml_data_preparation_service import (
    ml_data_preparation_service,
)


# ================================================================
# ML DATA PREPARATION CONTROLLER
# ================================================================

class MLDataPreparationController:
    """
    Controller layer for the ML Data Preparation Service.

    Responsibilities:
        - Receive validated request data from the route
        - Call the preparation service
        - Attach organization_id to the response
        - Return the prepared result
    """

    def __init__(self):
        self.service = ml_data_preparation_service

    # ============================================================
    # PREPARE DATA
    # ============================================================

    def prepare_data(
        self,
        organization_id: str,
        source: str,
        data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prepare organization data for the appropriate
        ML model(s).
        """

        result = self.service.prepare(
            source=source,
            data=data,
            context=context,
        )

        # The service does not need to know about
        # organization identity. The controller adds it.
        result["organization_id"] = organization_id

        return result

    # ============================================================
    # MODEL SCHEMA
    # ============================================================

    def get_model_schema(self):
        """
        Return the feature schema discovered
        from the loaded ML models.
        """

        return self.service.get_model_schema()


# ================================================================
# SINGLETON
# ================================================================

ml_data_preparation_controller = (
    MLDataPreparationController()
)