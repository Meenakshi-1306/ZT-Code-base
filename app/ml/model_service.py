from typing import Any, Dict
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

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


class ModelService:
    """
    ZeroTrust AI - Model Execution Service

    Responsibilities:
        1. Load existing trained models.
        2. Determine which models are applicable.
        3. Prepare incoming organization data.
        4. Build model-compatible input.
        5. Execute prediction.
        6. Return model outputs.

    IMPORTANT:
        No model is trained or modified here.
    """

    BASE_DIR = Path(__file__).resolve().parent
    MODEL_DIR = BASE_DIR / "models"

    MODEL_FILES = {
        "network_rf": "network_logs_rf_model.pkl",
        "awscloud_if": "awscloud_logs_if_model.pkl",
        "zero_trust_gb": "zero_trust_gradient_boosting.pkl",
        "zero_trust_if": "zero_trust_isolation_forest.pkl",
    }

    def __init__(self):

        self.models = {}

        self.preparation_services = {
            "network_rf": network_data_preparation_service,
            "awscloud_if": aws_data_preparation_service,
            "zero_trust_gb": zero_trust_gb_data_preparation_service,
            "zero_trust_if": zero_trust_if_data_preparation_service,
        }

        self._load_models()

    # ============================================================
    # LOAD MODELS
    # ============================================================

    def _load_models(self):

        for model_name, filename in self.MODEL_FILES.items():

            model_path = self.MODEL_DIR / filename

            if not model_path.exists():

                self.models[model_name] = None
                continue

            try:

                self.models[model_name] = joblib.load(
                    model_path
                )

            except Exception as exc:

                raise RuntimeError(
                    f"Unable to load model "
                    f"'{model_name}': {exc}"
                )

    # ============================================================
    # MODEL STATUS
    # ============================================================

    def get_model_status(self):

        result = {}

        for model_name, model in self.models.items():

            info = {
                "loaded": model is not None,
                "model_file": self.MODEL_FILES[model_name],
            }

            if model is not None:

                if hasattr(model, "n_features_in_"):

                    info["feature_count"] = int(
                        model.n_features_in_
                    )

                if hasattr(model, "feature_names_in_"):

                    info["features"] = list(
                        model.feature_names_in_
                    )

            result[model_name] = info

        return result

    # ============================================================
    # PUBLIC PREDICTION
    # ============================================================

    def predict(
        self,
        source: str,
        data: Dict[str, Any],
        context: Dict[str, Any] = None,
    ):

        context = context or {}

        source = (
            str(source)
            .strip()
            .lower()
        )

        # --------------------------------------------------------
        # Determine applicable models
        # --------------------------------------------------------

        model_names = self._models_for_source(
            source=source,
            data=data,
            context=context,
        )

        results = {}

        for model_name in model_names:

            results[model_name] = (
                self._predict_single(
                    model_name=model_name,
                    data=data,
                    context=context,
                )
            )

        combined_severity = self._calculate_combined_severity(
            model_results=results,
        )

        return {
            "success": True,
            "source": source,
            "models": results,
            "combined_severity": combined_severity,
        }

    # ============================================================
    # MODEL APPLICABILITY
    # ============================================================

    @classmethod
    def _models_for_source(
        cls,
        source: str,
        data: Dict[str, Any],
        context: Dict[str, Any],
    ):
        """
        Decide which trained models are applicable.

        IMPORTANT:

        A generic organization event must NOT automatically
        be sent to every ML model.

        The working reference separates:

            Network traffic -> Network RF
            AWS CloudTrail  -> AWS IF
            Zero Trust      -> GB + Zero Trust IF

        Therefore organization_logs is inferred from the
        actual fields present in the event.
        """

        # --------------------------------------------------------
        # Explicit network source
        # --------------------------------------------------------

        if source == "network":

            return [
                "network_rf"
            ]

        # --------------------------------------------------------
        # Explicit AWS source
        # --------------------------------------------------------

        if source == "aws":

            return [
                "awscloud_if"
            ]

        # --------------------------------------------------------
        # Explicit Zero Trust source
        # --------------------------------------------------------

        if source == "zero_trust":

            return [
                "zero_trust_gb",
                "zero_trust_if",
            ]

        # --------------------------------------------------------
        # Organization logs
        # --------------------------------------------------------

        if source == "organization_logs":

            models = []

            # ----------------------------------------------------
            # Explicit context overrides
            # ----------------------------------------------------

            declared_type = (
                context.get("data_type")
                or context.get("source_type")
                or context.get("log_type")
                or context.get("event_type")
            )

            if declared_type:

                declared_type = (
                    str(declared_type)
                    .strip()
                    .lower()
                )

                if declared_type in [
                    "aws",
                    "cloudtrail",
                    "aws_cloudtrail",
                ]:

                    return [
                        "awscloud_if"
                    ]

                if declared_type in [
                    "network",
                    "network_flow",
                    "traffic",
                ]:

                    return [
                        "network_rf"
                    ]

                if declared_type in [
                    "zero_trust",
                    "security_event",
                    "access_event",
                ]:

                    return [
                        "zero_trust_gb",
                        "zero_trust_if",
                    ]

            # ----------------------------------------------------
            # AWS detection
            # ----------------------------------------------------

            aws_keys = {
                "eventSource",
                "eventName",
                "awsRegion",
                "userIdentity",
                "eventCategory",
                "tlsDetails",
                "additionalEventData",
                "resources",
            }

            if any(
                key in data
                for key in aws_keys
            ):

                models.append(
                    "awscloud_if"
                )

            # ----------------------------------------------------
            # Network-flow detection
            # ----------------------------------------------------

            network_keys = {
                "Destination Port",
                "Flow Duration",
                "Total Fwd Packets",
                "Total Length of Fwd Packets",
                "Fwd Packet Length Max",
                "Bwd Packet Length Max",
                "Flow Bytes/s",
                "Flow Packets/s",
                "Fwd IAT Total",
                "Bwd IAT Total",
                "Packet Length Mean",
                "FIN Flag Count",
                "ACK Flag Count",
            }

            network_match_count = len(
                network_keys.intersection(
                    set(data.keys())
                )
            )

            if network_match_count >= 3:

                models.append(
                    "network_rf"
                )

            # ----------------------------------------------------
            # Zero Trust behavioral detection
            # ----------------------------------------------------

            zero_trust_keys = {
                "device_type",
                "operating_system",
                "browser",
                "user_role",
                "action",
                "resource_type",
                "http_method",
                "endpoint",
                "location",
                "network_packet_size",
                "protocol_type",
                "login_attempts",
                "session_duration",
                "encryption_used",
                "ip_reputation_score",
                "failed_logins",
                "browser_type",
                "unusual_time_access",
            }

            zero_trust_match_count = len(
                zero_trust_keys.intersection(
                    set(data.keys())
                )
            )

            if zero_trust_match_count >= 2:

                models.extend([
                    "zero_trust_gb",
                    "zero_trust_if",
                ])

            # ----------------------------------------------------
            # Remove duplicates
            # ----------------------------------------------------

            models = list(
                dict.fromkeys(models)
            )

            # ----------------------------------------------------
            # No recognizable model domain
            # ----------------------------------------------------

            if not models:

                return []

            return models

        raise ValueError(
            f"Unsupported prediction source: "
            f"'{source}'"
        )

    # ============================================================
    # SINGLE MODEL PREDICTION
    # ============================================================

    def _predict_single(
        self,
        model_name: str,
        data: Dict[str, Any],
        context: Dict[str, Any],
    ):

        model = self.models.get(
            model_name
        )

        # --------------------------------------------------------
        # Model unavailable
        # --------------------------------------------------------

        if model is None:

            return {
                "model": model_name,
                "status": "SKIPPED",
                "prediction": None,
                "reason": (
                    "Model file could not be loaded."
                ),
            }

        preparation_service = (
            self.preparation_services[
                model_name
            ]
        )

        # --------------------------------------------------------
        # Prepare data
        # --------------------------------------------------------

        try:

            prepared = (
                preparation_service.prepare(
                    data=data,
                    context=context,
                )
            )

        except Exception as exc:

            return {
                "model": model_name,
                "status": "ERROR",
                "prediction": None,
                "reason": (
                    f"Data preparation failed: "
                    f"{exc}"
                ),
            }

        # --------------------------------------------------------
        # Model readiness
        # --------------------------------------------------------

        can_run = prepared.get(
            "can_run_model",
            False,
        )

        if not can_run:

            return {
                "model": model_name,
                "status": "SKIPPED",
                "prediction": None,
                "reason": prepared.get(
                    "reason",
                    "Prepared data is not sufficient "
                    "for model execution.",
                ),
                "coverage": prepared.get(
                    "coverage",
                    0.0,
                ),
                "prepared_features": len(
                    prepared.get(
                        "prepared_data",
                        {},
                    )
                ),
            }

        # --------------------------------------------------------
        # Build model input
        # --------------------------------------------------------

        try:

            X = self._build_input(
                model_name=model_name,
                model=model,
                prepared=prepared,
            )

        except Exception as exc:

            return {
                "model": model_name,
                "status": "ERROR",
                "prediction": None,
                "reason": (
                    f"Unable to construct model "
                    f"input: {exc}"
                ),
            }

        # --------------------------------------------------------
        # Execute model
        # --------------------------------------------------------

        try:

            prediction = model.predict(X)

            prediction_value = prediction[0]

            result = {
                "model": model_name,
                "status": "PREDICTED",
                "prediction": self._safe_value(
                    prediction_value
                ),
                "input_shape": list(
                    X.shape
                ),
                "coverage": prepared.get(
                    "coverage",
                    0.0,
                ),
            }

            # ----------------------------------------------------
            # Classification probabilities
            # ----------------------------------------------------

            if hasattr(
                model,
                "predict_proba",
            ):

                probabilities = (
                    model.predict_proba(X)[0]
                )

                result["probabilities"] = [
                    float(value)
                    for value in probabilities
                ]

                if hasattr(
                    model,
                    "classes_",
                ):

                    class_probabilities = {

                        str(cls):
                            float(prob)

                        for cls, prob in zip(
                            model.classes_,
                            probabilities,
                        )
                    }

                    result[
                        "class_probabilities"
                    ] = class_probabilities

                    if model_name == "zero_trust_gb":

                        attack_probability = (
                            self._get_attack_probability(
                                model=model,
                                probabilities=probabilities,
                            )
                        )

                        normal_probability = (
                            self._get_normal_probability(
                                model=model,
                                probabilities=probabilities,
                            )
                        )

                        result[
                            "attack_probability"
                        ] = attack_probability

                        result[
                            "normal_probability"
                        ] = normal_probability

                        result[
                            "attack_probability_percent"
                        ] = round(
                            attack_probability * 100,
                            2,
                        )

                        result[
                            "normal_probability_percent"
                        ] = round(
                            normal_probability * 100,
                            2,
                        )

            # ----------------------------------------------------
            # Isolation Forest decision score
            # ----------------------------------------------------

            if hasattr(
                model,
                "decision_function",
            ):

                score = model.decision_function(X)

                decision_score = float(
                    score[0]
                )

                result[
                    "decision_score"
                ] = decision_score

                if model_name in [
                    "awscloud_if",
                    "zero_trust_if",
                ]:

                    result[
                        "score_type"
                    ] = (
                        "isolation_forest_decision_score"
                    )

                    result[
                        "is_probability"
                    ] = False

                    result[
                        "anomaly_direction"
                    ] = (
                        "negative_is_more_anomalous"
                    )

                    result[
                        "anomaly_index"
                    ] = self._calculate_anomaly_index(
                        decision_score
                    )

                    result[
                        "anomaly_severity"
                    ] = self._get_anomaly_severity(
                        decision_score
                    )

            # ----------------------------------------------------
            # Interpretation
            # ----------------------------------------------------

            result[
                "interpretation"
            ] = self._interpret_prediction(
                model_name=model_name,
                prediction=prediction_value,
            )

            return result

        except Exception as exc:

            return {
                "model": model_name,
                "status": "ERROR",
                "prediction": None,
                "reason": (
                    f"Model prediction failed: "
                    f"{exc}"
                ),
            }

    # ============================================================
    # BUILD MODEL INPUT
    # ============================================================

    def _build_input(
        self,
        model_name: str,
        model,
        prepared: Dict[str, Any],
    ):

        prepared_data = dict(
            prepared.get(
                "prepared_data",
                {},
            )
        )

        # --------------------------------------------------------
        # Zero Trust GB
        #
        # IMPORTANT:
        # The working reference uses IP reputation values such
        # as 90, 85, 75, 35, 15.
        #
        # If API input provides 0.9 / 0.5 / 0.15, convert it to
        # the 0-100 representation expected by the trained model.
        # --------------------------------------------------------

        if model_name == "zero_trust_gb":

            if "ip_reputation_score" in prepared_data:

                value = prepared_data[
                    "ip_reputation_score"
                ]

                try:

                    numeric_value = float(
                        value
                    )

                    if (
                        0.0
                        <= numeric_value
                        <= 1.0
                    ):

                        prepared_data[
                            "ip_reputation_score"
                        ] = (
                            numeric_value * 100.0
                        )

                except (
                    TypeError,
                    ValueError,
                ):

                    pass

        # --------------------------------------------------------
        # Zero Trust Isolation Forest
        # --------------------------------------------------------

        if model_name == "zero_trust_if":

            values = list(
                prepared_data.values()
            )

            X = np.asarray(
                values,
                dtype=float,
            ).reshape(
                1,
                -1,
            )

            expected = getattr(
                model,
                "n_features_in_",
                None,
            )

            if (
                expected is not None
                and X.shape[1] != expected
            ):

                raise ValueError(
                    f"Model expects "
                    f"{expected} features "
                    f"but prepared input contains "
                    f"{X.shape[1]}."
                )

            return X

        # --------------------------------------------------------
        # Feature names
        # --------------------------------------------------------

        if hasattr(
            model,
            "feature_names_in_",
        ):

            features = list(
                model.feature_names_in_
            )

        else:

            features = list(
                prepared.get(
                    "features",
                    [],
                )
            )

        if not features:

            raise ValueError(
                "Model feature schema is unavailable."
            )

        # --------------------------------------------------------
        # Check missing features
        # --------------------------------------------------------

        missing = [
            feature
            for feature in features
            if feature not in prepared_data
        ]

        if missing:

            raise ValueError(
                f"Missing model features: "
                f"{missing[:10]}"
            )

        # --------------------------------------------------------
        # Exact feature order
        # --------------------------------------------------------

        values = [
            prepared_data[feature]
            for feature in features
        ]

        return pd.DataFrame(
            [values],
            columns=features,
        )

    # ============================================================
    # COMBINED SECURITY SEVERITY
    # ============================================================

    MODEL_WEIGHTS = {
        "network_rf": 0.25,
        "awscloud_if": 0.20,
        "zero_trust_gb": 0.30,
        "zero_trust_if": 0.25,
    }

    @classmethod
    def _model_severity_score(cls, model_name: str, result: Dict[str, Any]) -> float:
        if result.get("status") != "PREDICTED":
            return 0.0

        if model_name in {"network_rf", "zero_trust_gb"}:
            probabilities = result.get("class_probabilities")
            if isinstance(probabilities, dict):
                try:
                    return max(0.0, min(100.0, float(probabilities.get("1", 0.0)) * 100.0))
                except (TypeError, ValueError):
                    pass

            attack_probability = result.get("attack_probability")
            if attack_probability is not None:
                try:
                    return max(0.0, min(100.0, float(attack_probability) * 100.0))
                except (TypeError, ValueError):
                    pass

            return 100.0 if result.get("interpretation") == "ATTACK_DETECTED" else 0.0

        if model_name in {"awscloud_if", "zero_trust_if"}:
            decision_score = result.get("decision_score")
            if decision_score is None:
                return 100.0 if result.get("prediction") == -1 else 0.0

            try:
                score = float(decision_score)
            except (TypeError, ValueError):
                return 0.0

            if score >= 0:
                return 0.0

            return max(0.0, min(100.0, (abs(score) / 0.10) * 100.0))

        return 0.0

    @classmethod
    def _calculate_combined_severity(cls, model_results: Dict[str, Any]) -> Dict[str, Any]:
        weighted_sum = 0.0
        active_weight = 0.0
        contributions = []

        for model_name, result in model_results.items():
            if not isinstance(result, dict) or result.get("status") != "PREDICTED":
                continue

            weight = cls.MODEL_WEIGHTS.get(model_name, 0.0)
            if weight <= 0:
                continue

            severity_score = cls._model_severity_score(model_name, result)
            weighted_sum += severity_score * weight
            active_weight += weight

            contributions.append({
                "model": model_name,
                "raw_severity_score": round(severity_score, 2),
                "configured_weight": weight,
                "weighted_contribution": round(severity_score * weight, 2),
            })

        if active_weight == 0:
            return {
                "available": False,
                "combined_severity_score": None,
                "severity": "UNAVAILABLE",
                "models_included": [],
                "weights_normalized": False,
            }

        combined_score = max(0.0, min(100.0, weighted_sum / active_weight))

        if combined_score >= 75:
            severity = "CRITICAL"
        elif combined_score >= 50:
            severity = "HIGH"
        elif combined_score >= 25:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        return {
            "available": True,
            "combined_severity_score": round(combined_score, 2),
            "severity": severity,
            "models_included": [x["model"] for x in contributions],
            "weights_normalized": True,
            "active_weight": round(active_weight, 2),
            "contributions": contributions,
            "score_type": "combined_model_severity",
            "is_probability": False,
        }

    # ============================================================
    # ATTACK PROBABILITY
    # ============================================================

    @staticmethod
    def _get_attack_probability(
        model,
        probabilities,
    ):

        if not hasattr(
            model,
            "classes_",
        ):

            return 0.0

        for cls, probability in zip(
            model.classes_,
            probabilities,
        ):

            if int(cls) == 1:

                return float(
                    probability
                )

        return 0.0

    # ============================================================
    # NORMAL PROBABILITY
    # ============================================================

    @staticmethod
    def _get_normal_probability(
        model,
        probabilities,
    ):

        if not hasattr(
            model,
            "classes_",
        ):

            return 0.0

        for cls, probability in zip(
            model.classes_,
            probabilities,
        ):

            if int(cls) == 0:

                return float(
                    probability
                )

        return 0.0

    # ============================================================
    # ANOMALY INDEX
    # ============================================================

    @staticmethod
    def _calculate_anomaly_index(
        decision_score: float,
    ) -> float:

        if decision_score >= 0:

            return 0.0

        index = (
            abs(decision_score)
            / 0.20
        ) * 100.0

        index = max(
            0.0,
            min(
                index,
                100.0,
            ),
        )

        return round(
            index,
            2,
        )

    # ============================================================
    # ANOMALY SEVERITY
    # ============================================================

    @staticmethod
    def _get_anomaly_severity(
        decision_score: float,
    ) -> str:

        if decision_score >= 0:

            return "NORMAL"

        if decision_score >= -0.05:

            return "LOW_ANOMALY"

        if decision_score >= -0.10:

            return "MEDIUM_ANOMALY"

        if decision_score >= -0.20:

            return "HIGH_ANOMALY"

        return "CRITICAL_ANOMALY"

    # ============================================================
    # INTERPRETATION
    # ============================================================

    @staticmethod
    def _interpret_prediction(
        model_name,
        prediction,
    ):

        if model_name in [
            "awscloud_if",
            "zero_trust_if",
        ]:

            if prediction == -1:

                return "ANOMALOUS"

            if prediction == 1:

                return "NORMAL"

        if model_name == "zero_trust_gb":

            if prediction == 1:

                return "ATTACK_DETECTED"

            if prediction == 0:

                return "NORMAL"

        if model_name == "network_rf":

            if prediction == 1:

                return "ATTACK_DETECTED"

            return "NORMAL"

        return str(prediction)

    # ============================================================
    # SAFE VALUE
    # ============================================================

    @staticmethod
    def _safe_value(value):

        if isinstance(
            value,
            np.integer,
        ):

            return int(value)

        if isinstance(
            value,
            np.floating,
        ):

            return float(value)

        return value


# ================================================================
# SERVICE INSTANCE
# ================================================================

model_service = ModelService()


# ================================================================
# LOCAL TEST
# ================================================================

if __name__ == "__main__":

    import json

    test_data = {

        "timestamp":
            "2026-09-22T10:30:00",

        "user_id":
            "user_001",

        "session_id":
            "session_001",

        "resource":
            "customer_database",

        "resource_type":
            "database",

        "action":
            "read",

        "device_type":
            "Laptop",

        "operating_system":
            "Windows",

        "browser":
            "Chrome",

        "user_role":
            "employee",

        "http_method":
            "GET",

        "endpoint":
            "/api/customers",

        "location":
            "Chennai",

        "protocol_type":
            "TCP",

        "network_packet_size":
            600,

        "login_attempts":
            1,

        "session_duration":
            300,

        "encryption_used":
            "AES",

        "ip_reputation_score":
            0.9,

        "failed_logins":
            0,

        "browser_type":
            "Chrome",

        "unusual_time_access":
            0,
    }

    print()
    print("=" * 70)
    print("ZERO TRUST AI - MODEL SERVICE TEST")
    print("=" * 70)

    print()
    print("MODEL STATUS")
    print("-" * 70)

    print(
        json.dumps(
            model_service.get_model_status(),
            indent=2,
            default=str,
        )
    )

    print()
# ================================================================
# SERVICE INSTANCE
# ================================================================

model_service = ModelService()