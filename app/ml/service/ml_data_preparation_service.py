from typing import Any, Dict

from app.ml.service.network_data_preparation_service import (
    network_data_preparation_service,
)

from app.ml.service.aws_data_preparation_service import (
    aws_data_preparation_service,
)

from app.ml.service.zero_trust_gb_data_preparation_service import (
    zero_trust_gb_data_preparation_service,
)

from app.ml.service.zero_trust_if_data_preparation_service import (
    zero_trust_if_data_preparation_service,
)


class MLDataPreparationService:

    SOURCE_MODELS = {
        "network": [
            "network_rf",
            "zero_trust_gb",
            "zero_trust_if",
        ],

        "aws": [
            "awscloud_if",
        ],

        "zero_trust": [
            "zero_trust_gb",
            "zero_trust_if",
        ],

        # Generic heterogeneous organization logs
        "organization_logs": [
            "network_rf",
            "awscloud_if",
            "zero_trust_gb",
            "zero_trust_if",
        ],
    }

    def __init__(self):

        self.services = {
            "network_rf": (
                network_data_preparation_service
            ),

            "awscloud_if": (
                aws_data_preparation_service
            ),

            "zero_trust_gb": (
                zero_trust_gb_data_preparation_service
            ),

            "zero_trust_if": (
                zero_trust_if_data_preparation_service
            ),
        }

    # ---------------------------------------------------------
    # PREPARE
    # ---------------------------------------------------------

    def prepare(
        self,
        source: str,
        data: Dict[str, Any],
        context: Dict[str, Any],
    ):

        source = (
            source.strip()
            .lower()
        )

        if source not in self.SOURCE_MODELS:

            raise ValueError(
                f"Unsupported ML preparation source: "
                f"'{source}'"
            )

        model_names = self.SOURCE_MODELS[
            source
        ]

        prepared_models = {}

        models_ready = []
        models_skipped = []

        for model_name in model_names:

            service = self.services[
                model_name
            ]

            try:

                result = service.prepare(
                    data=data,
                    context=context,
                )

                prepared_models[
                    model_name
                ] = result

                # -------------------------------------------------
                # IMPORTANT:
                # The individual preparation services expose
                # `can_run_model` as the final execution gate.
                #
                # Do NOT use `ml_ready` here because some models
                # can be executed even when their stricter
                # preparation-quality flag is false.
                # -------------------------------------------------

                if result.get(
                    "can_run_model",
                    False,
                ):

                    models_ready.append(
                        model_name
                    )

                else:

                    models_skipped.append(
                        model_name
                    )

            except Exception as exc:

                prepared_models[
                    model_name
                ] = {
                    "model": model_name,
                    "features": [],
                    "prepared_data": {},
                    "feature_details": {},
                    "provided_features": [],
                    "derived_features": [],
                    "estimated_features": [],
                    "imputed_features": [],
                    "defaulted_features": [],
                    "unavailable_features": [],
                    "missing_features": [],
                    "extra_input_features": [],
                    "coverage": 0.0,
                    "model_compatible": False,
                    "ml_ready": False,
                    "can_run_model": False,
                    "reason": (
                        f"Preparation failed: {exc}"
                    ),
                }

                models_skipped.append(
                    model_name
                )

        # -----------------------------------------------------
        # DATA QUALITY
        # -----------------------------------------------------

        total_input_fields = len(
            data
        )

        mapped_fields = 0
        derived_fields = 0
        estimated_fields = 0
        imputed_fields = 0
        defaulted_fields = 0
        unavailable_fields = 0

        for result in prepared_models.values():

            mapped_fields += len(
                result.get(
                    "provided_features",
                    [],
                )
            )

            derived_fields += len(
                result.get(
                    "derived_features",
                    [],
                )
            )

            estimated_fields += len(
                result.get(
                    "estimated_features",
                    [],
                )
            )

            imputed_fields += len(
                result.get(
                    "imputed_features",
                    [],
                )
            )

            defaulted_fields += len(
                result.get(
                    "defaulted_features",
                    [],
                )
            )

            unavailable_fields += len(
                result.get(
                    "unavailable_features",
                    [],
                )
            )

        # -----------------------------------------------------
        # Remove duplicate counting across models.
        # Quality is based on input fields rather than the
        # number of model features.
        # -----------------------------------------------------

        known_input_keys = set()

        for result in prepared_models.values():

            for feature in result.get(
                "provided_features",
                [],
            ):

                known_input_keys.add(
                    feature
                )

        effective_mapped = min(
            mapped_fields,
            total_input_fields,
        )

        overall_coverage = round(
            (
                effective_mapped
                + min(
                    derived_fields,
                    total_input_fields,
                )
            )
            / max(
                total_input_fields,
                1,
            ),
            4,
        )

        quality_components = []

        for result in prepared_models.values():

            quality_components.append(
                self._result_quality(
                    result
                )
            )

        overall_quality = round(
            sum(quality_components)
            / max(
                len(quality_components),
                1,
            ),
            4,
        )

        unknown_fields = max(
            0,
            total_input_fields
            - effective_mapped,
        )

        return {
            "success": True,

            "source": source,

            "models_considered": model_names,

            "models_ready": models_ready,

            "models_skipped": models_skipped,

            "prepared_models": prepared_models,

            "data_quality": {
                "total_input_fields": total_input_fields,

                "mapped_fields": effective_mapped,

                "derived_fields": min(
                    derived_fields,
                    total_input_fields,
                ),

                "estimated_fields": estimated_fields,

                "imputed_fields": imputed_fields,

                "defaulted_fields": defaulted_fields,

                "unavailable_fields": unavailable_fields,

                "unknown_fields": unknown_fields,

                "overall_coverage": overall_coverage,

                "overall_quality_score": overall_quality,
            },

            "message": (
                "Data preparation completed."
                if models_ready
                else
                "Data preparation completed, but "
                "no model currently has sufficient "
                "ML-ready data."
            ),
        }

    # ---------------------------------------------------------
    # QUALITY
    # ---------------------------------------------------------

    def _result_quality(
        self,
        result: Dict[str, Any],
    ) -> float:

        details = result.get(
            "feature_details",
            {},
        )

        if not details:
            return 0.0

        weights = {
            "provided": 1.0,
            "alias": 0.95,
            "derived": 0.90,
            "historical": 0.85,
            "imputed": 0.70,
            "relationship_estimated": 0.50,
            "default": 0.30,
            "unavailable": 0.0,
        }

        total = 0

        for detail in details.values():

            total += weights.get(
                detail.get(
                    "source",
                    "unavailable",
                ),
                0.0,
            )

        return total / len(details)

    # ---------------------------------------------------------
    # MODEL SCHEMA
    # ---------------------------------------------------------

    def get_model_schema(self):

        return {
            "network_rf": {
                "model": "network_logs_rf_model",

                "feature_count": len(
                    network_data_preparation_service.features
                ),

                "features": (
                    network_data_preparation_service.features
                ),
            },

            "awscloud_if": {
                "model": "awscloud_logs_if_model",

                "feature_count": len(
                    aws_data_preparation_service.features
                ),

                "features": (
                    aws_data_preparation_service.features
                ),
            },

            "zero_trust_gb": {
                "model": (
                    "zero_trust_gradient_boosting"
                ),

                "feature_count": len(
                    zero_trust_gb_data_preparation_service.features
                ),

                "features": (
                    zero_trust_gb_data_preparation_service.features
                ),
            },

            "zero_trust_if": {
                "model": (
                    "zero_trust_isolation_forest"
                ),

                "expected_total_features": (
                    zero_trust_if_data_preparation_service.expected_total
                ),

                "encoder_features": (
                    zero_trust_if_data_preparation_service.categorical_features
                ),

                "encoded_feature_count": (
                    zero_trust_if_data_preparation_service.encoded_count
                ),

                "unknown_numerical_feature_count": (
                    zero_trust_if_data_preparation_service.required_numerical_count
                ),

                "ml_ready": False,

                "reason": (
                    "The trained artifact does not expose "
                    "the names/order of the numerical "
                    "training features."
                ),
            },
        }


ml_data_preparation_service = (
    MLDataPreparationService()
)