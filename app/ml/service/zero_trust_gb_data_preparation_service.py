from typing import Any, Dict, Optional
import joblib

from app.ml.service.feature_utils import FeatureUtils


class ZeroTrustGBDataPreparationService:
    """
    Data preparation service for the Zero Trust Gradient Boosting model.

    Model:
        zero_trust_gradient_boosting.pkl

    Expected model features:

        network_packet_size
        protocol_type
        login_attempts
        session_duration
        encryption_used
        ip_reputation_score
        failed_logins
        browser_type
        unusual_time_access
    """

    MODEL_NAME = "zero_trust_gradient_boosting"

    MODEL_PATH = "C:\\Users\\meena\\FinalYearProject\\Final_py\\models\\zero_trust_gradient_boosting.pkl"

    def __init__(self):

        self.model = joblib.load(self.MODEL_PATH)

        self.features = list(
            self.model.feature_names_in_
        )

        self.aliases = {

            "network_packet_size": [
                "packet_size",
                "network_size",
                "total_packet_size",
                "total_bytes",
                "total_length",
                "flow_bytes",
            ],

            "protocol_type": [
                "protocol",
                "protocol_name",
                "network_protocol",
            ],

            "login_attempts": [
                "login_attempt",
                "login_count",
                "authentication_attempts",
                "auth_attempts",
                "failed_login_attempts",
            ],

            "session_duration": [
                "flow_duration",
                "duration",
                "session_time",
                "connection_duration",
            ],

            "encryption_used": [
                "encryption",
                "encryption_type",
                "cipher",
                "tls_version",
            ],

            "ip_reputation_score": [
                "ip_reputation",
                "ip_score",
                "reputation_score",
            ],

            "failed_logins": [
                "failed_login",
                "failed_login_count",
                "login_failures",
            ],

            "browser_type": [
                "browser",
                "browser_name",
                "user_agent_browser",
            ],

            "unusual_time_access": [
                "unusual_time",
                "off_hours_access",
                "after_hours",
                "abnormal_time_access",
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
        # 1. Direct / alias mappings
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

            # Categorical features must remain categorical
            # because the original model test accepts:
            # TCP / AES / Chrome etc.
            if feature in [
                "protocol_type",
                "encryption_used",
                "browser_type",
            ]:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    feature,
                    value,
                    match["source"],
                    match["confidence"],
                    match["reason"],
                )

            else:

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

        # -----------------------------------------------------
        # 2. Derive network_packet_size
        # -----------------------------------------------------

        self._derive_network_packet_size(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 3. Derive session duration
        # -----------------------------------------------------

        self._derive_session_duration(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 4. Derive protocol
        # -----------------------------------------------------

        self._derive_protocol(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 5. Derive encryption
        # -----------------------------------------------------

        self._derive_encryption(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 6. Derive login behavior
        # -----------------------------------------------------

        self._derive_login_features(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 7. Derive unusual access time
        # -----------------------------------------------------

        self._derive_unusual_time(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 8. Browser
        # -----------------------------------------------------

        self._derive_browser(
            data=data,
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 9. Feature-specific defaults
        # -----------------------------------------------------

        self._apply_defaults(
            prepared_data=prepared_data,
            feature_details=feature_details,
        )

        # -----------------------------------------------------
        # 10. Exact model schema
        # -----------------------------------------------------

        for feature in self.features:

            if feature not in prepared_data:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    feature,
                    self._default_for(feature),
                    "default",
                    0.35,
                    (
                        f"No reliable evidence was available "
                        f"for '{feature}'."
                    ),
                )

        # -----------------------------------------------------
        # 11. Exact feature order
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
                "Zero Trust Gradient Boosting input prepared "
                "using model-specific network, authentication, "
                "session, and access-time relationships."
            ),
        }

    # =========================================================
    # NETWORK PACKET SIZE
    # =========================================================

    def _derive_network_packet_size(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        if "network_packet_size" in prepared_data:
            return

        # -----------------------------------------------------
        # Direct total bytes
        # -----------------------------------------------------

        total_bytes = self._find_numeric(
            data,
            [
                "total_bytes",
                "total_length",
                "flow_bytes",
                "network_bytes",
            ],
        )

        if total_bytes is not None:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "network_packet_size",
                total_bytes,
                "derived",
                0.90,
                (
                    "Mapped total network bytes to the "
                    "Zero Trust network packet size feature."
                ),
            )

            return

        # -----------------------------------------------------
        # Forward packets × packet size
        # -----------------------------------------------------

        packet_count = self._find_numeric(
            data,
            [
                "total_fwd_packets",
                "fwd_packets",
                "packet_count",
            ],
        )

        packet_size = self._find_numeric(
            data,
            [
                "packet_size",
                "fwd_packet_length_mean",
                "average_packet_size",
            ],
        )

        if packet_count is not None and packet_size is not None:

            estimated = packet_count * packet_size

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "network_packet_size",
                estimated,
                "relationship_estimated",
                0.75,
                (
                    "Estimated from packet count multiplied "
                    "by average packet size."
                ),
            )

            return

        # -----------------------------------------------------
        # Packet count alone
        # -----------------------------------------------------

        if packet_count is not None:

            estimated = packet_count * 500.0

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "network_packet_size",
                estimated,
                "relationship_estimated",
                0.55,
                (
                    "Estimated from packet count using a "
                    "typical network packet-size baseline."
                ),
            )

    # =========================================================
    # SESSION DURATION
    # =========================================================

    def _derive_session_duration(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        if "session_duration" in prepared_data:
            return

        duration = self._find_numeric(
            data,
            [
                "flow_duration",
                "session_time",
                "connection_duration",
                "duration",
            ],
        )

        if duration is None:
            return

        FeatureUtils.add_feature(
            feature_details,
            prepared_data,
            "session_duration",
            duration,
            "derived",
            0.90,
            (
                "Mapped network flow duration to "
                "Zero Trust session duration."
            ),
        )

    # =========================================================
    # PROTOCOL
    # =========================================================

    def _derive_protocol(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        if "protocol_type" in prepared_data:
            return

        protocol = self._find_value(
            data,
            [
                "protocol",
                "protocol_type",
                "network_protocol",
            ],
        )

        if protocol is not None:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "protocol_type",
                protocol,
                "derived",
                0.95,
                "Protocol directly identified from network data.",
            )

            return

        # -----------------------------------------------------
        # Port-based inference
        # -----------------------------------------------------

        port = self._find_numeric(
            data,
            [
                "dst_port",
                "destination_port",
                "dest_port",
            ],
        )

        if port is None:
            return

        port = int(port)

        protocol = None

        if port in [80, 8080, 8000]:
            protocol = "TCP"

        elif port == 443:
            protocol = "TCP"

        elif port == 22:
            protocol = "TCP"

        elif port == 53:
            protocol = "UDP"

        if protocol is not None:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "protocol_type",
                protocol,
                "relationship_estimated",
                0.65,
                (
                    f"Protocol estimated from destination "
                    f"port {port}."
                ),
            )

    # =========================================================
    # ENCRYPTION
    # =========================================================

    def _derive_encryption(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        if "encryption_used" in prepared_data:
            return

        encryption = self._find_value(
            data,
            [
                "encryption",
                "encryption_type",
                "cipher",
                "tls_version",
            ],
        )

        if encryption is not None:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "encryption_used",
                encryption,
                "derived",
                0.90,
                "Encryption information identified from input.",
            )

            return

        # -----------------------------------------------------
        # HTTPS inference
        # -----------------------------------------------------

        port = self._find_numeric(
            data,
            [
                "dst_port",
                "destination_port",
                "dest_port",
            ],
        )

        if port == 443:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "encryption_used",
                "AES",
                "relationship_estimated",
                0.55,
                (
                    "HTTPS destination port indicates encrypted "
                    "traffic; AES used as a model-compatible "
                    "encryption category."
                ),
            )

    # =========================================================
    # LOGIN FEATURES
    # =========================================================

    def _derive_login_features(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        # -----------------------------------------------------
        # Login attempts
        # -----------------------------------------------------

        if "login_attempts" not in prepared_data:

            attempts = self._find_numeric(
                data,
                [
                    "login_attempts",
                    "login_attempt",
                    "authentication_attempts",
                    "auth_attempts",
                ],
            )

            if attempts is not None:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    "login_attempts",
                    attempts,
                    "derived",
                    0.95,
                    "Authentication attempt count mapped directly.",
                )

        # -----------------------------------------------------
        # Failed logins
        # -----------------------------------------------------

        if "failed_logins" not in prepared_data:

            failed = self._find_numeric(
                data,
                [
                    "failed_logins",
                    "failed_login",
                    "login_failures",
                    "failed_login_count",
                ],
            )

            if failed is not None:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    "failed_logins",
                    failed,
                    "derived",
                    0.95,
                    "Failed login count mapped directly.",
                )

                # If total attempts unavailable, estimate that
                # failed logins are part of login attempts.
                if "login_attempts" not in prepared_data:

                    FeatureUtils.add_feature(
                        feature_details,
                        prepared_data,
                        "login_attempts",
                        failed + 1,
                        "relationship_estimated",
                        0.60,
                        (
                            "Estimated login attempts from "
                            "failed-login count."
                        ),
                    )

    # =========================================================
    # UNUSUAL TIME
    # =========================================================

    def _derive_unusual_time(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        if "unusual_time_access" in prepared_data:
            return

        explicit = self._find_value(
            data,
            [
                "unusual_time_access",
                "unusual_time",
                "off_hours_access",
                "after_hours",
            ],
        )

        if explicit is not None:

            value = self._to_binary(explicit)

            if value is not None:

                FeatureUtils.add_feature(
                    feature_details,
                    prepared_data,
                    "unusual_time_access",
                    value,
                    "derived",
                    0.95,
                    "Explicit unusual-time indicator provided.",
                )

                return

        timestamp = self._find_timestamp(data)

        if timestamp is None:
            return

        # 22:00–06:00 treated as off-hours.
        hour = timestamp.hour

        unusual = (
            1
            if hour >= 22 or hour < 6
            else 0
        )

        FeatureUtils.add_feature(
            feature_details,
            prepared_data,
            "unusual_time_access",
            unusual,
            "derived",
            0.90,
            (
                f"Unusual-time access derived from event hour "
                f"{hour}."
            ),
        )

    # =========================================================
    # BROWSER
    # =========================================================

    def _derive_browser(
        self,
        data: Dict[str, Any],
        prepared_data: Dict[str, Any],
        feature_details: Dict[str, Dict[str, Any]],
    ):

        if "browser_type" in prepared_data:
            return

        browser = self._find_value(
            data,
            [
                "browser",
                "browser_type",
                "browser_name",
                "user_agent_browser",
            ],
        )

        if browser is not None:

            FeatureUtils.add_feature(
                feature_details,
                prepared_data,
                "browser_type",
                browser,
                "derived",
                0.95,
                "Browser identified from input data.",
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
            "network_packet_size": 500.0,
            "protocol_type": "TCP",
            "login_attempts": 1.0,
            "session_duration": 0.0,
            "encryption_used": "AES",
            "ip_reputation_score": 0.5,
            "failed_logins": 0.0,
            "browser_type": "Chrome",
            "unusual_time_access": 0.0,
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
                    0.35,
                    (
                        f"Zero Trust GB feature-specific "
                        f"default used for '{feature}'."
                    ),
                )

    def _default_for(
        self,
        feature: str,
    ):

        defaults = {
            "network_packet_size": 500.0,
            "protocol_type": "TCP",
            "login_attempts": 1.0,
            "session_duration": 0.0,
            "encryption_used": "AES",
            "ip_reputation_score": 0.5,
            "failed_logins": 0.0,
            "browser_type": "Chrome",
            "unusual_time_access": 0.0,
        }

        return defaults.get(feature, 0.0)

    # =========================================================
    # HELPERS
    # =========================================================

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
    def _find_numeric(
        data: Dict[str, Any],
        keys: list,
    ) -> Optional[float]:

        value = ZeroTrustGBDataPreparationService._find_value(
            data,
            keys,
        )

        return FeatureUtils.safe_float(value)

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

                timestamp = FeatureUtils.parse_timestamp(
                    data[key]
                )

                if timestamp is not None:
                    return timestamp

        return None

    @staticmethod
    def _to_binary(
        value: Any,
    ) -> Optional[float]:

        if isinstance(value, bool):
            return float(value)

        if isinstance(value, (int, float)):
            return 1.0 if value else 0.0

        value = str(value).strip().lower()

        if value in [
            "true",
            "yes",
            "1",
            "unusual",
            "abnormal",
            "off_hours",
            "after_hours",
        ]:
            return 1.0

        if value in [
            "false",
            "no",
            "0",
            "normal",
        ]:
            return 0.0

        return None

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
                "Zero Trust behavioral feature preparation "
                "for the trained Gradient Boosting model."
            ),
        }


zero_trust_gb_data_preparation_service = (
    ZeroTrustGBDataPreparationService()
)