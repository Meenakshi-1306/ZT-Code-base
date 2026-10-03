from typing import Any, Dict


class RiskEngine:
    """
    ZeroTrust AI - Risk Engine

    Combines:
        1. ML model risk
        2. Zero Trust contextual risk

    The ML models are NOT modified.

    The final operational score is calculated dynamically
    from the actual event data.

    Score:
        0   -> lowest operational risk
        100 -> highest operational risk

    Severity:
        0-24   LOW
        25-39  MEDIUM
        40-74  HIGH
        75-100 CRITICAL
    """

    # ============================================================
    # MODEL WEIGHTS
    # ============================================================

    MODEL_WEIGHTS = {
        "network_rf": 0.25,
        "awscloud_if": 0.20,
        "zero_trust_gb": 0.30,
        "zero_trust_if": 0.25,
    }

    # ML contributes 20%.
    # Context contributes 80%.

    ML_WEIGHT = 0.20
    CONTEXT_WEIGHT = 0.80

    # ============================================================
    # SEVERITY THRESHOLDS
    # ============================================================

    SEVERITY_THRESHOLDS = {
        "CRITICAL": 75.0,
        "HIGH": 40.0,
        "MEDIUM": 25.0,
        "LOW": 0.0,
    }

    # ============================================================
    # MAIN RISK CALCULATION
    # ============================================================

    def calculate_risk(
        self,
        model_results: Dict[str, Any],
        event_data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        event_data = event_data or {}

        findings = []
        reasons = []

        weighted_score = 0.0
        total_weight = 0.0

        executed_models = 0
        skipped_models = 0
        attack_models = 0
        anomaly_models = 0

        # ========================================================
        # PROCESS ML MODELS
        # ========================================================

        for model_name, result in model_results.items():

            if not isinstance(result, dict):
                continue

            status = result.get(
                "status",
                "UNKNOWN",
            )

            # ----------------------------------------------------
            # SKIPPED
            # ----------------------------------------------------

            if status == "SKIPPED":

                skipped_models += 1

                findings.append({
                    "model": model_name,
                    "status": "SKIPPED",
                    "prediction": None,
                    "risk_contribution": 0.0,
                    "reason": result.get(
                        "reason",
                        "Model was skipped.",
                    ),
                })

                continue

            # ----------------------------------------------------
            # ERROR
            # ----------------------------------------------------

            if status == "ERROR":

                findings.append({
                    "model": model_name,
                    "status": "ERROR",
                    "prediction": None,
                    "risk_contribution": 0.0,
                    "reason": result.get(
                        "reason",
                        "Model execution failed.",
                    ),
                })

                continue

            # ----------------------------------------------------
            # NOT PREDICTED
            # ----------------------------------------------------

            if status != "PREDICTED":
                continue

            executed_models += 1

            prediction = result.get(
                "prediction"
            )

            # ----------------------------------------------------
            # MODEL RISK
            # ----------------------------------------------------

            model_risk = self._model_risk_score(
                model_name=model_name,
                result=result,
            )

            weight = self.MODEL_WEIGHTS.get(
                model_name,
                0.0,
            )

            weighted_score += (
                model_risk * weight
            )

            total_weight += weight

            interpretation = result.get(
                "interpretation",
                str(prediction),
            )

            findings.append({
                "model": model_name,
                "status": "PREDICTED",
                "prediction": self._safe_value(
                    prediction
                ),
                "interpretation": interpretation,
                "model_risk_score": round(
                    model_risk,
                    2,
                ),
                "weight": weight,
            })

            # ----------------------------------------------------
            # COUNTERS
            # ----------------------------------------------------

            if interpretation == "ATTACK_DETECTED":

                attack_models += 1

                reasons.append(
                    f"{model_name} detected "
                    f"a potential attack."
                )

            elif interpretation == "ANOMALOUS":

                anomaly_models += 1

                reasons.append(
                    f"{model_name} detected "
                    f"anomalous behavior."
                )

            elif interpretation == "NORMAL":

                reasons.append(
                    f"{model_name} classified "
                    f"the activity as normal."
                )

        # ========================================================
        # NO MODEL RESULTS
        # ========================================================

        if total_weight == 0:

            return {
                "success": True,
                "risk_score": None,
                "risk_level": "UNAVAILABLE",
                "risk_status": "NO_MODEL_RESULT",
                "executed_models": 0,
                "skipped_models": skipped_models,
                "attack_models": attack_models,
                "anomaly_models": anomaly_models,
                "findings": findings,
                "reasons": [
                    "No model produced a usable prediction."
                ],
                "recommended_action":
                    "Collect additional data "
                    "before making a risk assessment.",
            }

        # ========================================================
        # RAW ML COMBINED SCORE
        # ========================================================

        ml_combined_score = (
            weighted_score / total_weight
        )

        ml_combined_score = self._clamp_score(
            ml_combined_score
        )

        # ========================================================
        # CONTEXTUAL ZERO TRUST SCORE
        # ========================================================

        contextual_score, context_reasons = (
            self._calculate_contextual_risk(
                event_data
            )
        )

        # Add contextual explanations.

        reasons.extend(
            context_reasons
        )

        # ========================================================
        # FINAL OPERATIONAL SCORE
        # ========================================================

        operational_score = (
            (
                ml_combined_score
                * self.ML_WEIGHT
            )
            +
            (
                contextual_score
                * self.CONTEXT_WEIGHT
            )
        )

        operational_score = self._clamp_score(
            operational_score
        )

        # ========================================================
        # SEVERITY
        # ========================================================

        risk_level = self._risk_level(
            operational_score
        )

        risk_status = self._risk_status(
            risk_level
        )

        recommended_action = (
            self._recommended_action(
                risk_level=risk_level,
                attack_models=attack_models,
                anomaly_models=anomaly_models,
            )
        )

        # ========================================================
        # FINAL RESPONSE
        # ========================================================

        return {

            "success": True,

            # ----------------------------------------------------
            # FINAL STAFF-FACING SCORE
            # ----------------------------------------------------

            "risk_score": round(
                operational_score,
                2,
            ),

            "risk_level":
                risk_level,

            "risk_status":
                risk_status,

            # ----------------------------------------------------
            # INTERNAL / TECHNICAL SCORES
            # ----------------------------------------------------

            "ml_combined_score":
                round(
                    ml_combined_score,
                    2,
                ),

            "contextual_risk_score":
                round(
                    contextual_score,
                    2,
                ),

            "score_weights": {
                "ml_weight": self.ML_WEIGHT,
                "context_weight": self.CONTEXT_WEIGHT,
            },

            # ----------------------------------------------------
            # MODEL INFORMATION
            # ----------------------------------------------------

            "executed_models":
                executed_models,

            "skipped_models":
                skipped_models,

            "attack_models":
                attack_models,

            "anomaly_models":
                anomaly_models,

            "findings":
                findings,

            "reasons":
                reasons,

            "recommended_action":
                recommended_action,
        }

    # ============================================================
    # CONTEXTUAL RISK
    # ============================================================

    def _calculate_contextual_risk(
        self,
        event_data: Dict[str, Any],
    ):

        score = 0.0
        reasons = []

        # --------------------------------------------------------
        # Normalize input
        # --------------------------------------------------------

        data = self._flatten_data(
            event_data
        )

        # ========================================================
        # FAILED LOGINS
        # ========================================================

        failed_logins = self._number(
            data.get("failed_logins", 0)
        )

        if failed_logins > 0:

            contribution = min(
                30.0,
                failed_logins * 2.0
            )

            score += contribution

            reasons.append(
                f"{int(failed_logins)} failed "
                f"login attempt(s) increased risk."
            )

        # ========================================================
        # LOGIN ATTEMPTS
        # ========================================================

        login_attempts = self._number(
            data.get("login_attempts", 0)
        )

        if login_attempts > 1:

            contribution = min(
                20.0,
                (login_attempts - 1) * 1.5
            )

            score += contribution

            reasons.append(
                f"Elevated login activity "
                f"({int(login_attempts)} attempts) "
                f"increased risk."
            )

        # ========================================================
        # IP REPUTATION
        # ========================================================

        reputation = self._number(
            data.get(
                "ip_reputation_score",
                1.0,
            )
        )

        # Supports both:
        #
        # 0.0 - 1.0
        #
        # and
        #
        # 0 - 100

        if reputation > 1:

            reputation = reputation / 100.0

        reputation = max(
            0.0,
            min(
                1.0,
                reputation,
            ),
        )

        reputation_risk = (
            1.0 - reputation
        ) * 20.0

        score += reputation_risk

        if reputation < 0.7:

            reasons.append(
                "Low IP reputation increased risk."
            )

        # ========================================================
        # UNUSUAL TIME
        # ========================================================

        unusual_time = self._boolean(
            data.get(
                "unusual_time_access",
                0,
            )
        )

        if unusual_time:

            score += 15.0

            reasons.append(
                "Access occurred during "
                "an unusual time."
            )

        # ========================================================
        # UNKNOWN DEVICE
        # ========================================================

        device = self._string(
            data.get(
                "device_type",
                ""
            )
        )

        if self._contains(
            device,
            [
                "unknown",
                "untrusted",
                "unrecognized",
                "new device",
            ],
        ):

            score += 10.0

            reasons.append(
                "Unknown or unrecognized "
                "device increased risk."
            )

        # ========================================================
        # SENSITIVE ACTION
        # ========================================================

        action = self._string(
            data.get(
                "action",
                ""
            )
        )

        resource = self._string(
            data.get(
                "resource_type",
                ""
            )
        )

        action_risk = self._action_risk(
            action,
            resource,
        )

        score += action_risk

        if action_risk > 0:

            reasons.append(
                "Sensitive resource/action "
                "combination increased risk."
            )

        # ========================================================
        # USER ROLE
        # ========================================================

        role = self._string(
            data.get(
                "user_role",
                ""
            )
        )

        if self._contains(
            role,
            [
                "admin",
                "administrator",
                "root",
            ],
        ):

            score += 5.0

            reasons.append(
                "Privileged account activity "
                "increased risk."
            )

        # ========================================================
        # NETWORK PACKET SIZE
        # ========================================================

        packet_size = self._number(
            data.get(
                "network_packet_size",
                0,
            )
        )

        if packet_size > 5000:

            score += 10.0

            reasons.append(
                "Very large network transfer "
                "increased risk."
            )

        elif packet_size > 2000:

            score += 5.0

            reasons.append(
                "Large network transfer "
                "increased risk."
            )

        # ========================================================
        # ENCRYPTION
        # ========================================================

        encryption = self._string(
            data.get(
                "encryption_used",
                ""
            )
        )

        if self._contains(
            encryption,
            [
                "none",
                "null",
                "unknown",
                "unencrypted",
            ],
        ):

            score += 10.0

            reasons.append(
                "Missing or weak encryption "
                "increased risk."
            )

        # ========================================================
        # SESSION DURATION
        # ========================================================

        session_duration = self._number(
            data.get(
                "session_duration",
                0,
            )
        )

        if session_duration > 3600:

            score += 5.0

            reasons.append(
                "Long-lived session "
                "increased risk."
            )

        # ========================================================
        # FINAL CONTEXT SCORE
        # ========================================================

        score = self._clamp_score(
            score
        )

        return score, reasons

    # ============================================================
    # ACTION RISK
    # ============================================================

    @staticmethod
    def _action_risk(
        action: str,
        resource: str,
    ) -> float:

        action = action.lower()
        resource = resource.lower()

        score = 0.0

        # High-impact operations.

        if any(
            value in action
            for value in [
                "delete",
                "destroy",
                "disable",
            ]
        ):

            score += 15.0

        elif any(
            value in action
            for value in [
                "export",
                "exfil",
            ]
        ):

            score += 20.0

        elif any(
            value in action
            for value in [
                "download",
                "transfer",
            ]
        ):

            score += 12.0

        elif any(
            value in action
            for value in [
                "login",
                "authenticate",
            ]
        ):

            score += 8.0

        # Sensitive resource types.

        if any(
            value in resource
            for value in [
                "credential",
                "password",
                "secret",
                "financial",
                "employee",
                "customer",
                "database",
            ]
        ):

            score += 8.0

        return min(
            25.0,
            score,
        )

    # ============================================================
    # MODEL RISK SCORE
    # ============================================================

    def _model_risk_score(
        self,
        model_name: str,
        result: Dict[str, Any],
    ) -> float:

        prediction = result.get(
            "prediction"
        )

        interpretation = result.get(
            "interpretation"
        )

        # ========================================================
        # GRADIENT BOOSTING
        # ========================================================

        if model_name == "zero_trust_gb":

            probabilities = result.get(
                "class_probabilities"
            )

            if isinstance(
                probabilities,
                dict,
            ):

                attack_probability = (
                    probabilities.get(
                        "1",
                        0.0,
                    )
                )

                return self._clamp_score(
                    float(
                        attack_probability
                    ) * 100.0
                )

            if interpretation == "ATTACK_DETECTED":
                return 100.0

            if interpretation == "NORMAL":
                return 0.0

        # ========================================================
        # ISOLATION FOREST
        # ========================================================

        if model_name in [
            "awscloud_if",
            "zero_trust_if",
        ]:

            decision_score = result.get(
                "decision_score"
            )

            if decision_score is not None:

                decision_score = float(
                    decision_score
                )

                if decision_score < 0:

                    # Negative = anomalous.
                    #
                    # Smooth transformation rather
                    # than a fixed prediction score.

                    score = (
                        abs(decision_score)
                        / 0.20
                    ) * 100.0

                    return self._clamp_score(
                        score
                    )

                # Positive = normal.

                score = max(
                    0.0,
                    25.0
                    - (
                        decision_score
                        * 100.0
                    ),
                )

                return self._clamp_score(
                    score
                )

            if prediction == -1:
                return 100.0

            return 0.0

        # ========================================================
        # NETWORK RANDOM FOREST
        # ========================================================

        if model_name == "network_rf":

            probabilities = result.get(
                "class_probabilities"
            )

            if isinstance(
                probabilities,
                dict,
            ):

                return self._clamp_score(
                    float(
                        probabilities.get(
                            "1",
                            0.0,
                        )
                    ) * 100.0
                )

            if interpretation == "ATTACK_DETECTED":
                return 100.0

            return 0.0

        # ========================================================
        # FALLBACK
        # ========================================================

        if interpretation in [
            "ATTACK_DETECTED",
            "ANOMALOUS",
        ]:

            return 100.0

        return 0.0

    # ============================================================
    # SEVERITY
    # ============================================================

    @classmethod
    def _risk_level(
        cls,
        risk_score: float,
    ) -> str:

        if risk_score >= 75:
            return "CRITICAL"

        if risk_score >= 40:
            return "HIGH"

        if risk_score >= 25:
            return "MEDIUM"

        return "LOW"

    # ============================================================
    # STATUS
    # ============================================================

    @staticmethod
    def _risk_status(
        risk_level: str,
    ) -> str:

        if risk_level == "CRITICAL":
            return "IMMEDIATE_ATTENTION"

        if risk_level == "HIGH":
            return "INVESTIGATION_REQUIRED"

        if risk_level == "MEDIUM":
            return "MONITOR"

        return "NORMAL"

    # ============================================================
    # RECOMMENDED ACTION
    # ============================================================

    @staticmethod
    def _recommended_action(
        risk_level: str,
        attack_models: int,
        anomaly_models: int,
    ) -> str:

        if risk_level == "CRITICAL":

            return (
                "Immediately investigate the event, "
                "review authentication and access activity, "
                "and apply the organization's incident "
                "response procedure."
            )

        if risk_level == "HIGH":

            return (
                "Investigate the event and review "
                "related user, device, session and "
                "resource activity."
            )

        if risk_level == "MEDIUM":

            return (
                "Continue monitoring the activity "
                "and review related events for "
                "additional anomalies."
            )

        return (
            "No immediate security action indicated "
            "by the available model and contextual "
            "risk signals."
        )

    # ============================================================
    # FLATTEN INPUT
    # ============================================================

    @classmethod
    def _flatten_data(
        cls,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        flattened = {}

        def walk(
            value: Any,
            prefix: str = "",
        ):

            if isinstance(
                value,
                dict,
            ):

                for key, child in value.items():

                    key_name = (
                        f"{prefix}.{key}"
                        if prefix
                        else key
                    )

                    walk(
                        child,
                        key_name,
                    )

            else:

                key = (
                    prefix.split(".")[-1]
                    if prefix
                    else prefix
                )

                flattened[key] = value

        walk(data)

        return flattened

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _number(
        value: Any,
    ) -> float:

        try:

            if value is None:
                return 0.0

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

    @staticmethod
    def _boolean(
        value: Any,
    ) -> bool:

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            (int, float),
        ):
            return value != 0

        return str(
            value
        ).lower() in [
            "true",
            "1",
            "yes",
            "y",
        ]

    @staticmethod
    def _string(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _contains(
        value: str,
        candidates,
    ) -> bool:

        value = value.lower()

        return any(
            candidate.lower() in value
            for candidate in candidates
        )

    @staticmethod
    def _clamp_score(
        score: float,
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                float(score),
            ),
        )

    @staticmethod
    def _safe_value(
        value: Any,
    ) -> Any:

        try:

            import numpy as np

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

        except ImportError:
            pass

        return value


# ================================================================
# SERVICE INSTANCE
# ================================================================

risk_engine = RiskEngine()