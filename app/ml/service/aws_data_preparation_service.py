from typing import Any, Dict, Optional
import joblib

from app.ml.service.feature_utils import FeatureUtils


class AWSDataPreparationService:
    """
    AWS CloudTrail-specific data preparation service.

    Model:
        awscloud_logs_if_model.pkl

    Responsibility:
        Convert heterogeneous AWS / CloudTrail input into the
        exact feature schema expected by the trained Isolation
        Forest model.

    This service does NOT execute the model.
    """

    MODEL_NAME = "awscloud_if"

    MODEL_PATH = r"C:\Users\meena\FinalYearProject\Final_py\models\awscloud_logs_if_model.pkl"

    def __init__(self):

        self.model = joblib.load(self.MODEL_PATH)

        self.features = list(
            self.model.feature_names_in_
        )

        self.aliases = {
            "userIdentity.accountId": [
                "account_id",
                "accountId",
                "aws_account_id",
                "user_account_id",
            ],

            "hour": [
                "event_hour",
                "timestamp_hour",
            ],

            "day_of_week": [
                "weekday",
                "dayofweek",
                "event_day_of_week",
            ],

            "has_error": [
                "error",
                "hasError",
                "error_present",
            ],

            "has_error_message": [
                "error_message",
                "hasErrorMessage",
                "errorMessage",
            ],

            "has_mfa": [
                "mfa",
                "mfa_enabled",
                "mfa_used",
                "multi_factor_authentication",
            ],

            "is_management_event": [
                "management_event",
                "isManagementEvent",
            ],

            "is_read_only": [
                "read_only",
                "readOnly",
            ],

            "eventSource": [
                "event_source",
                "source",
                "aws_service",
            ],

            "eventName": [
                "event_name",
                "api_call",
                "operation",
            ],

            "awsRegion": [
                "aws_region",
                "region",
            ],

            "eventCategory": [
                "event_category",
                "category",
            ],
        }

    # =========================================================
    # PUBLIC API
    # =========================================================

    def prepare(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        context = context or {}

        prepared_data = {}
        feature_details = {}

        # -----------------------------------------------------
        # 1. Direct / alias matching
        # -----------------------------------------------------

        for feature in self.features:

            match = FeatureUtils.find_input_value(
                data=data,
                feature_name=feature,
                aliases=self.aliases.get(feature, []),
            )

            if match is None:
                continue

            value = match["value"]

            # AWS model contains both numerical and one-hot
            # features, so preserve strings where required.
            numeric_value = FeatureUtils.safe_float(value)

            if numeric_value is not None:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    feature,
                    numeric_value,
                    match["source"],
                    match["confidence"],
                    match["reason"],
                )

            else:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    feature,
                    value,
                    match["source"],
                    match["confidence"],
                    match["reason"],
                )

        # -----------------------------------------------------
        # 2. Timestamp-derived AWS features
        # -----------------------------------------------------

        self._derive_timestamp_features(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 3. AWS semantic / relationship derivation
        # -----------------------------------------------------

        self._derive_event_features(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 4. One-hot categorical features
        # -----------------------------------------------------

        self._derive_one_hot_features(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 5. Feature-specific defaults
        # -----------------------------------------------------

        self._apply_defaults(
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 6. Exact schema completion
        # -----------------------------------------------------

        for feature in self.features:

            if feature not in prepared_data:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    feature,
                    0.0,
                    "default",
                    0.35,
                    (
                        f"No AWS-specific evidence was available "
                        f"for '{feature}'."
                    ),
                )

        # -----------------------------------------------------
        # 7. Exact feature ordering
        # -----------------------------------------------------

        prepared_data = {
            feature: prepared_data[feature]
            for feature in self.features
        }

        classification = FeatureUtils.classify_features(
            feature_details
        )

        coverage = FeatureUtils.calculate_coverage(
            len(self.features),
            feature_details,
        )

        quality_score = FeatureUtils.calculate_quality_score(
            feature_details
        )

        unknown_features = (
            FeatureUtils.get_unknown_input_features(
                data=data,
                known_features=set(self.features),
                aliases=self.aliases,
            )
        )

        return {
            "model": self.MODEL_NAME,
            "features": self.features,
            "prepared_data": prepared_data,
            "feature_details": feature_details,

            "provided_features": classification[
                "provided_features"
            ],

            "derived_features": classification[
                "derived_features"
            ],

            "estimated_features": classification[
                "estimated_features"
            ],

            "imputed_features": classification[
                "imputed_features"
            ],

            "defaulted_features": classification[
                "defaulted_features"
            ],

            "unavailable_features": classification[
                "unavailable_features"
            ],

            "missing_features": [],

            "extra_input_features": unknown_features,

            "coverage": coverage,

            "data_quality": quality_score,

            "can_run_model": True,

            "reason": (
                "AWS/CloudTrail data prepared against the exact "
                "trained AWS Isolation Forest schema."
            ),
        }

    # =========================================================
    # TIMESTAMP FEATURES
    # =========================================================

    def _derive_timestamp_features(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        timestamp = self._find_timestamp(data)

        if timestamp is None:
            return

        if "hour" in self.features and "hour" not in prepared_data:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "hour",
                timestamp.hour,
                "derived",
                0.95,
                "Hour derived from event timestamp.",
            )

        if (
            "day_of_week" in self.features
            and "day_of_week" not in prepared_data
        ):

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "day_of_week",
                timestamp.weekday(),
                "derived",
                0.95,
                "Day of week derived from event timestamp.",
            )

    # =========================================================
    # AWS EVENT SEMANTICS
    # =========================================================

    def _derive_event_features(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        event_name = self._find_value(
            data,
            [
                "eventName",
                "event_name",
                "api_call",
                "operation",
            ],
        )

        event_source = self._find_value(
            data,
            [
                "eventSource",
                "event_source",
                "aws_service",
            ],
        )

        error_code = self._find_value(
            data,
            [
                "errorCode",
                "error_code",
            ],
        )

        error_message = self._find_value(
            data,
            [
                "errorMessage",
                "error_message",
            ],
        )

        # -----------------------------------------------------
        # Error detection
        # -----------------------------------------------------

        if (
            "has_error" in self.features
            and "has_error" not in prepared_data
        ):

            has_error = 1 if (
                error_code
                or error_message
                or data.get("error")
            ) else 0

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "has_error",
                has_error,
                "derived",
                0.90,
                (
                    "Derived from AWS errorCode/errorMessage "
                    "presence."
                ),
            )

        if (
            "has_error_message" in self.features
            and "has_error_message" not in prepared_data
        ):

            has_error_message = 1 if error_message else 0

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "has_error_message",
                has_error_message,
                "derived",
                0.90,
                "Derived from errorMessage presence.",
            )

        # -----------------------------------------------------
        # Management event
        # -----------------------------------------------------

        if (
            "is_management_event" in self.features
            and "is_management_event" not in prepared_data
        ):

            value = self._infer_management_event(
                event_source,
                event_name,
            )

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "is_management_event",
                value,
                "relationship_estimated",
                0.70,
                (
                    "Estimated from AWS service/API operation "
                    "semantics."
                ),
            )

        # -----------------------------------------------------
        # Read-only event
        # -----------------------------------------------------

        if (
            "is_read_only" in self.features
            and "is_read_only" not in prepared_data
        ):

            value = self._infer_read_only(
                event_name
            )

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "is_read_only",
                value,
                "relationship_estimated",
                0.75,
                (
                    "Estimated from common AWS read-only "
                    "API operation naming."
                ),
            )

        # -----------------------------------------------------
        # MFA
        # -----------------------------------------------------

        if (
            "has_mfa" in self.features
            and "has_mfa" not in prepared_data
        ):

            value = self._infer_mfa(data)

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "has_mfa",
                value,
                "relationship_estimated",
                0.75,
                "Derived from available AWS authentication context.",
            )

    # =========================================================
    # ONE-HOT FEATURES
    # =========================================================

    def _derive_one_hot_features(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        event_source = self._find_value(
            data,
            ["eventSource", "event_source", "aws_service"],
        )

        event_name = self._find_value(
            data,
            ["eventName", "event_name", "api_call"],
        )

        region = self._find_value(
            data,
            ["awsRegion", "aws_region", "region"],
        )

        identity_type = self._find_value(
            data,
            [
                "userIdentity.type",
                "identity_type",
                "user_type",
            ],
        )

        event_category = self._find_value(
            data,
            [
                "eventCategory",
                "event_category",
                "category",
            ],
        )

        tls_version = self._find_value(
            data,
            [
                "tlsDetails.tlsVersion",
                "tls_version",
            ],
        )

        auth_method = self._find_value(
            data,
            [
                "additionalEventData.AuthenticationMethod",
                "authentication_method",
            ],
        )

        signature_version = self._find_value(
            data,
            [
                "additionalEventData.SignatureVersion",
                "signature_version",
            ],
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "eventSource",
            event_source,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "eventName",
            event_name,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "awsRegion",
            region,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "userIdentity.type",
            identity_type,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "eventCategory",
            event_category,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "tlsDetails.tlsVersion",
            tls_version,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "additionalEventData.AuthenticationMethod",
            auth_method,
        )

        self._activate_one_hot(
            prepared_data,
            feature_details,
            "additionalEventData.SignatureVersion",
            signature_version,
        )

    def _activate_one_hot(
        self,
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
        prefix: str,
        value: Any,
    ):

        if value is None:
            return

        value_string = str(value)

        candidate = f"{prefix}_{value_string}"

        if candidate not in self.features:
            return

        if candidate in prepared_data:
            return

        FeatureUtils.add_feature(
            feature_details,
            prepared_data,
            candidate,
            1.0,
            "derived",
            0.95,
            (
                f"One-hot feature activated from "
                f"'{prefix}' = '{value_string}'."
            ),
        )

    # =========================================================
    # DEFAULTS
    # =========================================================

    def _apply_defaults(
        self,
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        defaults = {
            "has_error": 0.0,
            "has_error_message": 0.0,
            "has_mfa": 0.0,
            "is_management_event": 0.0,
            "is_read_only": 0.0,
            "hour": 12.0,
            "day_of_week": 0.0,
        }

        for feature, value in defaults.items():

            if (
                feature in self.features
                and feature not in prepared_data
            ):

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    feature,
                    value,
                    "default",
                    0.45,
                    (
                        f"AWS-specific default used for "
                        f"'{feature}'."
                    ),
                )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _find_timestamp(
        data: Dict[str, Any],
    ):

        for key in [
            "timestamp",
            "eventTime",
            "event_time",
            "time",
        ]:

            if key in data:

                parsed = FeatureUtils.parse_timestamp(
                    data[key]
                )

                if parsed is not None:
                    return parsed

        return None

    @staticmethod
    def _find_value(
        data: Dict[str, Any],
        keys: list,
    ):

        for key in keys:

            if key in data:

                value = data[key]

                if value is not None and value != "":
                    return value

        return None

    @staticmethod
    def _infer_management_event(
        event_source: Any,
        event_name: Any,
    ) -> float:

        if event_source is None and event_name is None:
            return 0.0

        source = str(event_source or "").lower()
        name = str(event_name or "").lower()

        management_services = [
            "iam.amazonaws.com",
            "ec2.amazonaws.com",
            "cloudtrail.amazonaws.com",
            "organizations.amazonaws.com",
            "kms.amazonaws.com",
            "sts.amazonaws.com",
        ]

        management_actions = [
            "create",
            "delete",
            "update",
            "put",
            "attach",
            "detach",
            "authorize",
            "revoke",
            "modify",
        ]

        if any(service in source for service in management_services):
            return 1.0

        if any(action in name for action in management_actions):
            return 1.0

        return 0.0

    @staticmethod
    def _infer_read_only(
        event_name: Any,
    ) -> float:

        if event_name is None:
            return 0.0

        name = str(event_name).lower()

        read_prefixes = [
            "get",
            "describe",
            "list",
            "head",
            "lookup",
        ]

        if any(name.startswith(prefix) for prefix in read_prefixes):
            return 1.0

        return 0.0

    @staticmethod
    def _infer_mfa(
        data: Dict[str, Any],
    ) -> float:

        for key in [
            "mfaAuthenticated",
            "mfa_authenticated",
            "mfa",
            "has_mfa",
        ]:

            if key in data:

                value = data[key]

                if isinstance(value, bool):
                    return float(value)

                if str(value).lower() in [
                    "true",
                    "yes",
                    "1",
                    "enabled",
                ]:
                    return 1.0

                if str(value).lower() in [
                    "false",
                    "no",
                    "0",
                    "disabled",
                ]:
                    return 0.0

        return 0.0

    # =========================================================
    # MODEL SCHEMA
    # =========================================================

    def get_schema(self) -> Dict[str, Any]:

        return {
            "model": self.MODEL_NAME,
            "model_file": self.MODEL_PATH,
            "feature_count": len(self.features),
            "features": self.features,
            "description": (
                "AWS CloudTrail feature preparation for the "
                "trained Isolation Forest model."
            ),
        }


aws_data_preparation_service = (
    AWSDataPreparationService()
)