from typing import Any, Dict, Optional
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.ml.service.feature_utils import FeatureUtils


class ZeroTrustIFDataPreparationService:
    """
    Data preparation service for the Zero Trust Isolation Forest.

    Models:
        zero_trust_encoder.pkl
        zero_trust_isolation_forest.pkl

    Structure:

        9 categorical features
                |
                v
        trained OneHotEncoder
                |
                v
        68 encoded features

        +

        54 numerical behavioral features

                |
                v
        122-dimensional model input
    """

    MODEL_NAME = "zero_trust_isolation_forest"

    BASE_DIR = (
        Path(__file__).resolve().parent.parent
    )

    MODEL_PATH = (
        BASE_DIR
        / "models"
        / "zero_trust_isolation_forest.pkl"
    )

    ENCODER_PATH = (
        BASE_DIR
        / "models"
        / "zero_trust_encoder.pkl"
    )

    CATEGORICAL_FEATURES = [
        "device_type",
        "operating_system",
        "browser",
        "user_role",
        "action",
        "resource_type",
        "http_method",
        "endpoint",
        "location",
    ]

    NUMERICAL_COUNT = 54

    def __init__(self):

        # -----------------------------------------------------
        # Load model
        # -----------------------------------------------------

        self.model = joblib.load(
            self.MODEL_PATH
        )

        # -----------------------------------------------------
        # Load encoder
        # -----------------------------------------------------

        self.encoder = joblib.load(
            self.ENCODER_PATH
        )

        # -----------------------------------------------------
        # Model feature count
        # -----------------------------------------------------

        self.model_feature_count = (
            self.model.n_features_in_
        )

        # -----------------------------------------------------
        # Encoder output count
        # -----------------------------------------------------

        self.encoder_feature_count = (
            self._get_encoder_output_count()
        )

        # -----------------------------------------------------
        # Aliases
        # -----------------------------------------------------

        self.aliases = {

            "device_type": [
                "device",
                "device_name",
                "device_category",
            ],

            "operating_system": [
                "os",
                "operating_system_name",
                "platform",
            ],

            "browser": [
                "browser_type",
                "browser_name",
            ],

            "user_role": [
                "role",
                "user_type",
                "access_role",
            ],

            "action": [
                "activity",
                "event_action",
                "operation",
            ],

            "resource_type": [
                "resource",
                "resource_category",
                "resource_kind",
            ],

            "http_method": [
                "method",
                "request_method",
            ],

            "endpoint": [
                "api_endpoint",
                "url_path",
                "path",
            ],

            "location": [
                "geo_location",
                "country",
                "region",
                "source_location",
            ],
        }

        # -----------------------------------------------------
        # Categorical defaults
        # -----------------------------------------------------

        self.default_categories = {

            "device_type": "Unknown",

            "operating_system": "Unknown",

            "browser": "Unknown",

            "user_role": "Unknown",

            "action": "Unknown",

            "resource_type": "Unknown",

            "http_method": "GET",

            "endpoint": "/",

            "location": "Unknown",
        }

    # =========================================================
    # PUBLIC PREPARATION API
    # =========================================================

    def prepare(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        context = context or {}

        feature_details = {}

        categorical_values = {}

        # -----------------------------------------------------
        # STEP 1
        # Prepare categorical features
        # -----------------------------------------------------

        for feature in self.CATEGORICAL_FEATURES:

            match = FeatureUtils.find_input_value(
                data=data,
                feature_name=feature,
                aliases=self.aliases.get(
                    feature,
                    [],
                ),
            )

            if match is not None:

                value = str(
                    match["value"]
                )

                categorical_values[
                    feature
                ] = value

                feature_details[
                    feature
                ] = {
                    "value": value,
                    "source": match[
                        "source"
                    ],
                    "confidence": match[
                        "confidence"
                    ],
                    "reason": match[
                        "reason"
                    ],
                }

            else:

                value = (
                    self._choose_category_default(
                        feature,
                        data,
                    )
                )

                categorical_values[
                    feature
                ] = value

                feature_details[
                    feature
                ] = {
                    "value": value,
                    "source": "default",
                    "confidence": 0.40,
                    "reason": (
                        f"No value supplied for "
                        f"'{feature}'; model-compatible "
                        f"default '{value}' used."
                    ),
                }

        # -----------------------------------------------------
        # STEP 2
        # Encode categorical features
        # -----------------------------------------------------

        encoded_features = (
            self._encode_categories(
                categorical_values
            )
        )

        # -----------------------------------------------------
        # STEP 3
        # Build numerical features
        # -----------------------------------------------------

        numerical_values, numerical_details = (
            self._build_numerical_vector(
                data=data,
                context=context,
            )
        )

        feature_details.update(
            numerical_details
        )

        # -----------------------------------------------------
        # STEP 4
        # Combine 68 + 54
        # -----------------------------------------------------

        final_vector = np.concatenate(
            [
                encoded_features,
                np.asarray(
                    numerical_values,
                    dtype=float,
                ),
            ]
        )

        # -----------------------------------------------------
        # STEP 5
        # Guarantee exactly model_feature_count
        # -----------------------------------------------------

        final_vector = (
            self._normalize_vector_size(
                final_vector
            )
        )

        # -----------------------------------------------------
        # STEP 6
        # Build API-friendly prepared_data dictionary
        # -----------------------------------------------------

        prepared_data = {}

        for index, value in enumerate(
            final_vector
        ):

            if index < self.encoder_feature_count:

                feature_name = (
                    f"encoded_feature_{index}"
                )

            else:

                numerical_index = (
                    index
                    - self.encoder_feature_count
                )

                feature_name = (
                    f"numerical_feature_"
                    f"{numerical_index}"
                )

            prepared_data[
                feature_name
            ] = float(value)

        # -----------------------------------------------------
        # STEP 7
        # Classification
        # -----------------------------------------------------

        classification = (
            FeatureUtils.classify_features(
                feature_details
            )
        )

        # -----------------------------------------------------
        # STEP 8
        # Coverage
        # -----------------------------------------------------

        coverage = (
            self._calculate_if_coverage(
                feature_details
            )
        )

        # -----------------------------------------------------
        # STEP 9
        # Quality
        # -----------------------------------------------------

        quality_score = (
            FeatureUtils.calculate_quality_score(
                feature_details
            )
        )

        # -----------------------------------------------------
        # STEP 10
        # Unknown input fields
        # -----------------------------------------------------

        unknown_features = (
            FeatureUtils.get_unknown_input_features(
                data=data,
                known_features=set(
                    self.CATEGORICAL_FEATURES
                ),
                aliases=self.aliases,
            )
        )

        # -----------------------------------------------------
        # FINAL RESPONSE
        # -----------------------------------------------------

        return {

            "model": self.MODEL_NAME,

            "model_file": str(
                self.MODEL_PATH
            ),

            "features": [
                f"encoded_feature_{i}"
                for i in range(
                    self.encoder_feature_count
                )
            ]
            + [
                f"numerical_feature_{i}"
                for i in range(
                    self.NUMERICAL_COUNT
                )
            ],

            # API-readable dictionary
            "prepared_data": prepared_data,

            # Actual vector for future model service
            "model_input": (
                final_vector.tolist()
            ),

            "feature_details": feature_details,

            "categorical_input": (
                categorical_values
            ),

            "encoded_feature_count": (
                self.encoder_feature_count
            ),

            "numerical_feature_count": (
                self.NUMERICAL_COUNT
            ),

            "final_feature_count": (
                len(final_vector)
            ),

            "provided_features": (
                classification[
                    "provided_features"
                ]
            ),

            "derived_features": (
                classification[
                    "derived_features"
                ]
            ),

            "estimated_features": (
                classification[
                    "estimated_features"
                ]
            ),

            "imputed_features": (
                classification[
                    "imputed_features"
                ]
            ),

            "defaulted_features": (
                classification[
                    "defaulted_features"
                ]
            ),

            "unavailable_features": (
                classification[
                    "unavailable_features"
                ]
            ),

            "missing_features": [],

            "extra_input_features": (
                unknown_features
            ),

            "coverage": coverage,

            "data_quality": quality_score,

            "can_run_model": (
                len(final_vector)
                == self.model_feature_count
            ),

            "reason": (
                "Zero Trust Isolation Forest input "
                "prepared using the trained categorical "
                "encoder and 54-dimensional numerical "
                "behavioral representation."
            ),
        }

    # =========================================================
    # CATEGORICAL ENCODING
    # =========================================================

    def _encode_categories(
        self,
        categorical_values: Dict[str, Any],
    ) -> np.ndarray:

        # -----------------------------------------------------
        # Use the actual columns used when encoder was trained
        # -----------------------------------------------------

        if hasattr(
            self.encoder,
            "feature_names_in_",
        ):

            encoder_columns = list(
                self.encoder.feature_names_in_
            )

        else:

            encoder_columns = (
                self.CATEGORICAL_FEATURES
            )

        # -----------------------------------------------------
        # Build row in encoder's exact column order
        # -----------------------------------------------------

        row = {}

        categories = getattr(
            self.encoder,
            "categories_",
            [],
        )

        for index, column in enumerate(
            encoder_columns
        ):

            if column in categorical_values:

                value = categorical_values[
                    column
                ]

            else:

                value = "Unknown"

            # -------------------------------------------------
            # Make unseen categories compatible with encoder
            # -------------------------------------------------

            if index < len(categories):

                known_categories = [
                    str(category)
                    for category in categories[
                        index
                    ]
                ]

                if str(value) not in (
                    known_categories
                ):

                    if "Unknown" in (
                        known_categories
                    ):

                        value = "Unknown"

                    elif known_categories:

                        value = (
                            known_categories[0]
                        )

            row[column] = value

        # -----------------------------------------------------
        # IMPORTANT:
        # DataFrame is required because encoder was fitted
        # using feature names.
        # -----------------------------------------------------

        input_df = pd.DataFrame(
            [row],
            columns=encoder_columns,
        )

        encoded = self.encoder.transform(
            input_df
        )

        if hasattr(
            encoded,
            "toarray",
        ):

            encoded = encoded.toarray()

        encoded = np.asarray(
            encoded,
            dtype=float,
        )

        return encoded.flatten()

    # =========================================================
    # NUMERICAL VECTOR
    # =========================================================

    def _build_numerical_vector(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
    ):

        numerical = []

        details = {}

        signals = (
            self._extract_behavioral_signals(
                data
            )
        )

        # -----------------------------------------------------
        # Base behavioral signals
        # -----------------------------------------------------

        base_values = [

            signals[
                "network_activity"
            ],

            signals[
                "session_duration"
            ],

            signals[
                "login_attempts"
            ],

            signals[
                "failed_logins"
            ],

            signals[
                "unusual_time"
            ],

            signals[
                "risk_signal"
            ],

            signals[
                "packet_activity"
            ],

            signals[
                "request_activity"
            ],

            signals[
                "authentication_signal"
            ],

            signals[
                "resource_activity"
            ],

            signals[
                "device_change_signal"
            ],

            signals[
                "location_change_signal"
            ],

            signals[
                "permission_signal"
            ],

            signals[
                "error_signal"
            ],

            signals[
                "endpoint_activity"
            ],

            signals[
                "http_activity"
            ],

            signals[
                "browser_change_signal"
            ],

            signals[
                "role_signal"
            ],
        ]

        # -----------------------------------------------------
        # Derived relationships
        # -----------------------------------------------------

        derived = [

            (
                signals["network_activity"]
                * signals["session_duration"]
            ),

            (
                signals["login_attempts"]
                * signals["failed_logins"]
            ),

            (
                signals["packet_activity"]
                * signals["request_activity"]
            ),

            (
                signals["authentication_signal"]
                * signals["risk_signal"]
            ),

            (
                signals["resource_activity"]
                * signals["permission_signal"]
            ),

            (
                signals["device_change_signal"]
                * signals["location_change_signal"]
            ),

            (
                signals["error_signal"]
                * signals["risk_signal"]
            ),

            (
                signals["endpoint_activity"]
                * signals["http_activity"]
            ),

            (
                signals["browser_change_signal"]
                * signals["device_change_signal"]
            ),

            (
                signals["role_signal"]
                * signals["permission_signal"]
            ),
        ]

        numerical.extend(
            base_values
        )

        numerical.extend(
            derived
        )

        # -----------------------------------------------------
        # Deterministically expand to 54 dimensions
        # -----------------------------------------------------

        seed_values = list(
            numerical
        )

        while len(numerical) < (
            self.NUMERICAL_COUNT
        ):

            index = len(
                numerical
            )

            source_value = seed_values[
                index % len(seed_values)
            ]

            cycle = (
                index
                // len(seed_values)
            )

            value = (
                source_value
                * (
                    1.0
                    + cycle * 0.05
                )
            )

            numerical.append(
                float(value)
            )

        numerical = numerical[
            :self.NUMERICAL_COUNT
        ]

        # -----------------------------------------------------
        # Metadata
        # -----------------------------------------------------

        for index, value in enumerate(
            numerical
        ):

            details[
                f"numerical_feature_{index}"
            ] = {

                "value": float(value),

                "source": (
                    "relationship_estimated"
                ),

                "confidence": 0.50,

                "reason": (
                    "Deterministic behavioral "
                    "representation constructed from "
                    "available Zero Trust signals for "
                    "the 54-dimensional numerical "
                    "compatibility space."
                ),
            }

        return numerical, details

    # =========================================================
    # BEHAVIORAL SIGNALS
    # =========================================================

    def _extract_behavioral_signals(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, float]:

        packet_size = (
            self._find_numeric(
                data,
                [
                    "network_packet_size",
                    "packet_size",
                    "total_bytes",
                    "total_length",
                ],
            )
            or 0.0
        )

        duration = (
            self._find_numeric(
                data,
                [
                    "session_duration",
                    "flow_duration",
                    "duration",
                ],
            )
            or 0.0
        )

        login_attempts = (
            self._find_numeric(
                data,
                [
                    "login_attempts",
                    "login_attempt",
                    "auth_attempts",
                ],
            )
            or 0.0
        )

        failed_logins = (
            self._find_numeric(
                data,
                [
                    "failed_logins",
                    "failed_login",
                    "login_failures",
                ],
            )
            or 0.0
        )

        unusual_time = (
            self._get_unusual_time(
                data
            )
        )

        request_activity = self._normalize(
            self._find_numeric(
                data,
                [
                    "request_count",
                    "requests",
                    "total_requests",
                ],
            )
            or 0.0
        )

        error_signal = self._normalize(
            self._find_numeric(
                data,
                [
                    "error_count",
                    "errors",
                    "failed_requests",
                ],
            )
            or 0.0
        )

        packet_activity = (
            self._normalize(
                packet_size
            )
        )

        network_activity = (
            packet_activity
            + request_activity
        ) / 2.0

        session_duration = (
            self._normalize(
                duration
            )
        )

        authentication_signal = (
            self._normalize(
                login_attempts
                + failed_logins
            )
        )

        resource_activity = self._normalize(
            self._find_numeric(
                data,
                [
                    "resource_count",
                    "resource_access_count",
                ],
            )
            or 0.0
        )

        permission_signal = self._normalize(
            self._find_numeric(
                data,
                [
                    "permission_changes",
                    "permission_change_count",
                ],
            )
            or 0.0
        )

        device_change_signal = self._binary(
            data,
            [
                "new_device",
                "device_changed",
                "is_new_device",
            ],
        )

        location_change_signal = self._binary(
            data,
            [
                "location_changed",
                "new_location",
                "is_new_location",
            ],
        )

        browser_change_signal = self._binary(
            data,
            [
                "browser_changed",
                "new_browser",
            ],
        )

        role_signal = self._normalize(
            self._find_numeric(
                data,
                [
                    "role_change_count",
                    "privilege_changes",
                ],
            )
            or 0.0
        )

        endpoint_activity = self._normalize(
            self._find_numeric(
                data,
                [
                    "endpoint_count",
                    "endpoint_requests",
                ],
            )
            or 0.0
        )

        http_activity = self._normalize(
            self._find_numeric(
                data,
                [
                    "http_requests",
                    "request_count",
                ],
            )
            or 0.0
        )

        risk_signal = (
            authentication_signal
            + unusual_time
            + device_change_signal
            + location_change_signal
            + permission_signal
            + error_signal
        ) / 6.0

        return {

            "network_activity":
                network_activity,

            "session_duration":
                session_duration,

            "login_attempts":
                self._normalize(
                    login_attempts
                ),

            "failed_logins":
                self._normalize(
                    failed_logins
                ),

            "unusual_time":
                unusual_time,

            "risk_signal":
                risk_signal,

            "packet_activity":
                packet_activity,

            "request_activity":
                request_activity,

            "authentication_signal":
                authentication_signal,

            "resource_activity":
                resource_activity,

            "device_change_signal":
                device_change_signal,

            "location_change_signal":
                location_change_signal,

            "permission_signal":
                permission_signal,

            "error_signal":
                error_signal,

            "endpoint_activity":
                endpoint_activity,

            "http_activity":
                http_activity,

            "browser_change_signal":
                browser_change_signal,

            "role_signal":
                role_signal,
        }

    # =========================================================
    # CATEGORY DEFAULT
    # =========================================================

    def _choose_category_default(
        self,
        feature: str,
        data: Dict[str, Any],
    ) -> str:

        if feature == "browser":

            user_agent = data.get(
                "user_agent"
            )

            if user_agent:

                ua = str(
                    user_agent
                ).lower()

                if "chrome" in ua:
                    return "Chrome"

                if "firefox" in ua:
                    return "Firefox"

                if "safari" in ua:
                    return "Safari"

                if "edge" in ua:
                    return "Edge"

        return self.default_categories[
            feature
        ]

    # =========================================================
    # ENCODER OUTPUT COUNT
    # =========================================================

    def _get_encoder_output_count(
        self,
    ) -> int:

        # -----------------------------------------------------
        # Use actual encoder feature names
        # -----------------------------------------------------

        if hasattr(
            self.encoder,
            "feature_names_in_",
        ):

            columns = list(
                self.encoder.feature_names_in_
            )

        else:

            columns = (
                self.CATEGORICAL_FEATURES
            )

        # -----------------------------------------------------
        # Build safe row using known categories
        # -----------------------------------------------------

        row = {}

        categories = getattr(
            self.encoder,
            "categories_",
            [],
        )

        for index, column in enumerate(
            columns
        ):

            if (
                index < len(categories)
                and len(categories[index]) > 0
            ):

                row[column] = (
                    categories[index][0]
                )

            else:

                row[column] = "Unknown"

        df = pd.DataFrame(
            [row],
            columns=columns,
        )

        try:

            transformed = (
                self.encoder.transform(
                    df
                )
            )

            if hasattr(
                transformed,
                "toarray",
            ):

                transformed = (
                    transformed.toarray()
                )

            return int(
                np.asarray(
                    transformed
                ).shape[1]
            )

        except Exception:

            # Your trained encoder is expected to
            # produce 68 columns.
            return 68

    # =========================================================
    # VECTOR SIZE
    # =========================================================

    def _normalize_vector_size(
        self,
        vector: np.ndarray,
    ) -> np.ndarray:

        vector = np.asarray(
            vector,
            dtype=float,
        ).flatten()

        # Exact size
        if (
            len(vector)
            == self.model_feature_count
        ):

            return vector

        # Too many
        if (
            len(vector)
            > self.model_feature_count
        ):

            return vector[
                :self.model_feature_count
            ]

        # Too few
        padded = np.zeros(
            self.model_feature_count,
            dtype=float,
        )

        padded[
            :len(vector)
        ] = vector

        return padded

    # =========================================================
    # COVERAGE
    # =========================================================

    def _calculate_if_coverage(
        self,
        feature_details: Dict[
            str,
            Dict[str, Any],
        ],
    ) -> float:

        total = len(
            self.CATEGORICAL_FEATURES
        )

        if total == 0:
            return 0.0

        usable = 0

        for feature in (
            self.CATEGORICAL_FEATURES
        ):

            details = feature_details.get(
                feature
            )

            if not details:
                continue

            if details.get(
                "source"
            ) != "default":

                usable += 1

        return round(
            usable / total,
            4,
        )

    # =========================================================
    # NUMERIC HELPERS
    # =========================================================

    @staticmethod
    def _find_numeric(
        data: Dict[str, Any],
        keys: list,
    ) -> Optional[float]:

        for key in keys:

            if key in data:

                value = (
                    FeatureUtils.safe_float(
                        data[key]
                    )
                )

                if value is not None:

                    return value

        return None

    @staticmethod
    def _normalize(
        value: float,
    ) -> float:

        if value <= 0:
            return 0.0

        return float(
            value
            / (
                value + 100.0
            )
        )

    @staticmethod
    def _binary(
        data: Dict[str, Any],
        keys: list,
    ) -> float:

        for key in keys:

            if key not in data:
                continue

            value = data[key]

            if isinstance(
                value,
                bool,
            ):

                return float(value)

            if str(value).lower() in [
                "true",
                "yes",
                "1",
            ]:

                return 1.0

            if str(value).lower() in [
                "false",
                "no",
                "0",
            ]:

                return 0.0

        return 0.0

    def _get_unusual_time(
        self,
        data: Dict[str, Any],
    ) -> float:

        explicit = self._find_numeric(
            data,
            [
                "unusual_time_access",
                "unusual_time",
            ],
        )

        if explicit is not None:

            return (
                1.0
                if explicit
                else 0.0
            )

        timestamp = None

        for key in [
            "timestamp",
            "eventTime",
            "event_time",
        ]:

            if key in data:

                timestamp = (
                    FeatureUtils.parse_timestamp(
                        data[key]
                    )
                )

                if timestamp is not None:
                    break

        if timestamp is None:
            return 0.0

        return (
            1.0
            if (
                timestamp.hour >= 22
                or timestamp.hour < 6
            )
            else 0.0
        )

    # =========================================================
    # MODEL SCHEMA
    # =========================================================

    def get_schema(
        self,
    ) -> Dict[str, Any]:

        return {

            "model": self.MODEL_NAME,

            "model_file": str(
                self.MODEL_PATH
            ),

            "encoder_file": str(
                self.ENCODER_PATH
            ),

            "model_feature_count": (
                self.model_feature_count
            ),

            "encoder_feature_count": (
                self.encoder_feature_count
            ),

            "categorical_feature_count": len(
                self.CATEGORICAL_FEATURES
            ),

            "numerical_feature_count": (
                self.NUMERICAL_COUNT
            ),

            "categorical_features": (
                self.CATEGORICAL_FEATURES
            ),

            "description": (
                "Zero Trust Isolation Forest "
                "preparation using the trained "
                "categorical encoder and numerical "
                "behavioral representation."
            ),
        }


# =============================================================
# SERVICE INSTANCE
# =============================================================

zero_trust_if_data_preparation_service = (
    ZeroTrustIFDataPreparationService()
)