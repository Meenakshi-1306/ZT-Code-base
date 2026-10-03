from typing import Any, Dict, Optional

import joblib

from app.ml.service.feature_utils import (
    classify_features,
    find_input_value,
    mapping,
    normalize_key,
    quality_score,
    safe_float,
)


class NetworkDataPreparationService:
    """
    Network Random Forest data preparation service.

    Prepares heterogeneous organization network information
    against the exact 52-feature schema of the trained model.

    This service DOES NOT retrain the model.
    """

    MODEL_NAME = "network_rf"

    MODEL_PATH = (
        r"C:\Users\meena\FinalYearProject"
        r"\Final_py\models\network_logs_rf_model.pkl"
    )

    def __init__(self):

        self.model = joblib.load(
            self.MODEL_PATH
        )

        self.features = list(
            self.model.feature_names_in_
        )

        self.ALIASES = {

            "Destination Port": [
                "destination_port",
                "dest_port",
                "destinationPort",
            ],

            "Flow Duration": [
                "flow_duration",
            ],

            "Total Fwd Packets": [
                "total_fwd_packets",
                "forward_packets",
            ],

            "Total Length of Fwd Packets": [
                "total_length_of_fwd_packets",
                "total_fwd_bytes",
            ],

            "Fwd Packet Length Max": [
                "fwd_packet_length_max",
            ],

            "Fwd Packet Length Min": [
                "fwd_packet_length_min",
            ],

            "Fwd Packet Length Mean": [
                "fwd_packet_length_mean",
            ],

            "Fwd Packet Length Std": [
                "fwd_packet_length_std",
            ],

            "Bwd Packet Length Max": [
                "bwd_packet_length_max",
            ],

            "Bwd Packet Length Min": [
                "bwd_packet_length_min",
            ],

            "Bwd Packet Length Mean": [
                "bwd_packet_length_mean",
            ],

            "Bwd Packet Length Std": [
                "bwd_packet_length_std",
            ],

            "Flow Bytes/s": [
                "flow_bytes_per_second",
                "flow_bytes_s",
            ],

            "Flow Packets/s": [
                "flow_packets_per_second",
                "flow_packets_s",
            ],

            "Flow IAT Mean": [
                "flow_iat_mean",
            ],

            "Flow IAT Std": [
                "flow_iat_std",
            ],

            "Flow IAT Max": [
                "flow_iat_max",
            ],

            "Flow IAT Min": [
                "flow_iat_min",
            ],

            "Fwd IAT Total": [
                "fwd_iat_total",
            ],

            "Fwd IAT Mean": [
                "fwd_iat_mean",
            ],

            "Fwd IAT Std": [
                "fwd_iat_std",
            ],

            "Fwd IAT Max": [
                "fwd_iat_max",
            ],

            "Fwd IAT Min": [
                "fwd_iat_min",
            ],

            "Bwd IAT Total": [
                "bwd_iat_total",
            ],

            "Bwd IAT Mean": [
                "bwd_iat_mean",
            ],

            "Bwd IAT Std": [
                "bwd_iat_std",
            ],

            "Bwd IAT Max": [
                "bwd_iat_max",
            ],

            "Bwd IAT Min": [
                "bwd_iat_min",
            ],

            "Fwd Header Length": [
                "fwd_header_length",
            ],

            "Bwd Header Length": [
                "bwd_header_length",
            ],

            "Fwd Packets/s": [
                "fwd_packets_per_sec",
                "fwd_packets_s",
            ],

            "Bwd Packets/s": [
                "bwd_packets_per_sec",
                "bwd_packets_s",
            ],

            "Min Packet Length": [
                "min_packet_length",
            ],

            "Max Packet Length": [
                "max_packet_length",
            ],

            "Packet Length Mean": [
                "packet_length_mean",
            ],

            "Packet Length Std": [
                "packet_length_std",
            ],

            "Packet Length Variance": [
                "packet_length_variance",
            ],

            "FIN Flag Count": [
                "fin_flag_count",
            ],

            "PSH Flag Count": [
                "psh_flag_count",
            ],

            "ACK Flag Count": [
                "ack_flag_count",
            ],

            "Average Packet Size": [
                "average_packet_size",
            ],

            "Subflow Fwd Bytes": [
                "subflow_fwd_bytes",
            ],

            "Init_Win_bytes_forward": [
                "init_win_bytes_forward",
            ],

            "Init_Win_bytes_backward": [
                "init_win_bytes_backward",
            ],

            "act_data_pkt_fwd": [
                "act_data_pkt_fwd",
            ],

            "min_seg_size_forward": [
                "min_seg_size_forward",
            ],

            "Active Mean": [
                "active_mean",
            ],

            "Active Max": [
                "active_max",
            ],

            "Active Min": [
                "active_min",
            ],

            "Idle Mean": [
                "idle_mean",
            ],

            "Idle Max": [
                "idle_max",
            ],

            "Idle Min": [
                "idle_min",
            ],
        }

    # ========================================================
    # PREPARE
    # ========================================================

    def prepare(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        context = context or {}

        details = {}
        prepared = {}

        # ----------------------------------------------------
        # 1. DIRECT / ALIAS MATCHING
        # ----------------------------------------------------

        for feature in self.features:

            value, source, source_field = find_input_value(
                data,
                feature,
                self.ALIASES.get(
                    feature,
                    [],
                ),
            )

            if source:

                prepared[feature] = value

                details[feature] = mapping(
                    value,
                    source,
                    0.98,
                    (
                        f"Normalized input match: "
                        f"'{source_field}' -> "
                        f"'{feature}'."
                    ),
                )

        # ----------------------------------------------------
        # HELPER
        # ----------------------------------------------------

        def set_if_missing(
            feature,
            value,
            source,
            confidence,
            reason,
        ):

            if feature not in prepared:

                prepared[feature] = value

                details[feature] = mapping(
                    value,
                    source,
                    confidence,
                    reason,
                )

        # ----------------------------------------------------
        # COMMON VALUES
        # ----------------------------------------------------

        dst_port = safe_float(
            prepared.get(
                "Destination Port"
            )
        )

        duration = safe_float(
            prepared.get(
                "Flow Duration"
            )
        )

        fwd_packets = safe_float(
            prepared.get(
                "Total Fwd Packets"
            )
        )

        bwd_packets = safe_float(
            data.get(
                "total_bwd_packets"
            )
        )

        total_fwd_bytes = safe_float(
            prepared.get(
                "Total Length of Fwd Packets"
            )
        )

        total_bwd_bytes = safe_float(
            data.get(
                "total_length_bwd_packets"
            )
        )

        fwd_mean = safe_float(
            prepared.get(
                "Fwd Packet Length Mean"
            )
        )

        bwd_mean = safe_float(
            prepared.get(
                "Bwd Packet Length Mean"
            )
        )

        # ----------------------------------------------------
        # 2. DERIVATIONS
        # ----------------------------------------------------

        if (
            "Flow Packets/s" not in prepared
            and duration
            and duration > 0
            and fwd_packets is not None
        ):

            total_packets = fwd_packets

            if bwd_packets is not None:
                total_packets += bwd_packets

            prepared["Flow Packets/s"] = (
                total_packets
                / duration
                * 1_000_000
            )

            details["Flow Packets/s"] = mapping(
                prepared["Flow Packets/s"],
                "derived",
                0.95,
                "Derived from packet count and flow duration.",
            )

        if (
            "Fwd Packets/s" not in prepared
            and duration
            and duration > 0
            and fwd_packets is not None
        ):

            prepared["Fwd Packets/s"] = (
                fwd_packets
                / duration
                * 1_000_000
            )

            details["Fwd Packets/s"] = mapping(
                prepared["Fwd Packets/s"],
                "derived",
                0.95,
                "Derived from forward packet count and flow duration.",
            )

        if (
            "Bwd Packets/s" not in prepared
            and duration
            and duration > 0
            and bwd_packets is not None
        ):

            prepared["Bwd Packets/s"] = (
                bwd_packets
                / duration
                * 1_000_000
            )

            details["Bwd Packets/s"] = mapping(
                prepared["Bwd Packets/s"],
                "derived",
                0.95,
                "Derived from backward packet count and flow duration.",
            )

        if (
            "Flow Bytes/s" not in prepared
            and duration
            and duration > 0
        ):

            total_bytes = 0

            if total_fwd_bytes is not None:
                total_bytes += total_fwd_bytes

            if total_bwd_bytes is not None:
                total_bytes += total_bwd_bytes

            if total_bytes > 0:

                prepared["Flow Bytes/s"] = (
                    total_bytes
                    / duration
                    * 1_000_000
                )

                details["Flow Bytes/s"] = mapping(
                    prepared["Flow Bytes/s"],
                    "derived",
                    0.95,
                    "Derived from total flow bytes and duration.",
                )

        if (
            "Subflow Fwd Bytes" not in prepared
            and total_fwd_bytes is not None
        ):

            prepared["Subflow Fwd Bytes"] = (
                total_fwd_bytes
            )

            details["Subflow Fwd Bytes"] = mapping(
                total_fwd_bytes,
                "derived",
                0.90,
                "Derived from total forward bytes.",
            )

        # ----------------------------------------------------
        # 3. PACKET-LENGTH DERIVATIONS
        # ----------------------------------------------------

        if (
            "Fwd Packet Length Mean"
            not in prepared
            and total_fwd_bytes is not None
            and fwd_packets
            and fwd_packets > 0
        ):

            prepared[
                "Fwd Packet Length Mean"
            ] = (
                total_fwd_bytes
                / fwd_packets
            )

            details[
                "Fwd Packet Length Mean"
            ] = mapping(
                prepared[
                    "Fwd Packet Length Mean"
                ],
                "derived",
                0.85,
                "Derived from total forward bytes and forward packet count.",
            )

        if (
            "Bwd Packet Length Mean"
            not in prepared
            and total_bwd_bytes is not None
            and bwd_packets
            and bwd_packets > 0
        ):

            prepared[
                "Bwd Packet Length Mean"
            ] = (
                total_bwd_bytes
                / bwd_packets
            )

            details[
                "Bwd Packet Length Mean"
            ] = mapping(
                prepared[
                    "Bwd Packet Length Mean"
                ],
                "derived",
                0.85,
                "Derived from total backward bytes and backward packet count.",
            )

        # ----------------------------------------------------
        # 4. FEATURE-SPECIFIC NETWORK DEFAULTS
        # ----------------------------------------------------

        defaults = {

            "Fwd Header Length": 0,
            "Bwd Header Length": 0,

            "FIN Flag Count": 0,
            "PSH Flag Count": 0,
            "ACK Flag Count": 0,

            "Active Mean": 0,
            "Active Max": 0,
            "Active Min": 0,

            "Idle Mean": 0,
            "Idle Max": 0,
            "Idle Min": 0,

            "Fwd IAT Std": 0,
            "Bwd IAT Std": 0,

            "Packet Length Std": 0,
            "Packet Length Variance": 0,

            "Init_Win_bytes_forward": 0,
            "Init_Win_bytes_backward": 0,

            "act_data_pkt_fwd": 0,
            "min_seg_size_forward": 0,
        }

        for feature, value in defaults.items():

            set_if_missing(
                feature,
                value,
                "default",
                0.30,
                (
                    f"Feature-specific network "
                    f"default used for '{feature}'."
                ),
            )

        # ----------------------------------------------------
        # 5. PACKET STATISTICS
        # ----------------------------------------------------

        if (
            "Average Packet Size"
            not in prepared
            and fwd_mean is not None
        ):

            prepared[
                "Average Packet Size"
            ] = fwd_mean

            details[
                "Average Packet Size"
            ] = mapping(
                fwd_mean,
                "estimated",
                0.65,
                "Estimated from available forward packet statistics.",
            )

        if (
            "Packet Length Mean"
            not in prepared
            and fwd_mean is not None
        ):

            prepared[
                "Packet Length Mean"
            ] = fwd_mean

            details[
                "Packet Length Mean"
            ] = mapping(
                fwd_mean,
                "estimated",
                0.65,
                "Estimated from forward packet mean.",
            )

        if (
            "Min Packet Length"
            not in prepared
            and fwd_mean is not None
        ):

            prepared[
                "Min Packet Length"
            ] = min(
                fwd_mean,
                40.0,
            )

            details[
                "Min Packet Length"
            ] = mapping(
                prepared[
                    "Min Packet Length"
                ],
                "estimated",
                0.60,
                "Estimated minimum packet size from available packet statistics.",
            )

        if (
            "Max Packet Length"
            not in prepared
            and fwd_mean is not None
        ):

            prepared[
                "Max Packet Length"
            ] = max(
                fwd_mean,
                1500.0,
            )

            details[
                "Max Packet Length"
            ] = mapping(
                prepared[
                    "Max Packet Length"
                ],
                "estimated",
                0.60,
                "Estimated maximum packet size from available packet statistics.",
            )

        # ----------------------------------------------------
        # 6. REMAINING FEATURES
        # ----------------------------------------------------

        for feature in self.features:

            if feature not in prepared:

                prepared[feature] = 0

                details[feature] = mapping(
                    0,
                    "default",
                    0.20,
                    (
                        f"No reliable value available "
                        f"for '{feature}'; safe numeric "
                        f"fallback used."
                    ),
                )

        # ----------------------------------------------------
        # 7. CLASSIFICATION
        # ----------------------------------------------------

        (
            provided,
            derived,
            estimated,
            imputed,
            defaulted,
            unavailable,
        ) = classify_features(
            details
        )

        # ----------------------------------------------------
        # 8. COVERAGE
        # ----------------------------------------------------

        coverage = round(
            (
                len(provided)
                + len(derived)
                + len(estimated)
                + len(imputed)
                + len(defaulted)
            )
            / len(self.features),
            4,
        )

        score = quality_score(
            details
        )

        # ----------------------------------------------------
        # 9. MODEL COMPATIBILITY
        # ----------------------------------------------------

        model_compatible = (
            len(prepared)
            == len(self.features)
            and all(
                feature in prepared
                for feature in self.features
            )
        )

        # ----------------------------------------------------
        # 10. ML READINESS
        # ----------------------------------------------------

        ml_ready = (
            model_compatible
            and len(unavailable) == 0
            and score >= 0.50
        )

        return {

            "model": "network_rf",

            "features": self.features,

            "prepared_data": prepared,

            "feature_details": details,

            "provided_features": provided,

            "derived_features": derived,

            "estimated_features": estimated,

            "imputed_features": imputed,

            "defaulted_features": defaulted,

            "unavailable_features": unavailable,

            "missing_features": unavailable,

            "extra_input_features": [
                key
                for key in data
                if normalize_key(key)
                not in {
                    normalize_key(x)
                    for x in self.ALIASES.keys()
                }
                and normalize_key(key)
                not in {
                    normalize_key(alias)
                    for aliases in self.ALIASES.values()
                    for alias in aliases
                }
            ],

            "coverage": coverage,

            "model_compatible": model_compatible,

            "ml_ready": ml_ready,

            "can_run_model": ml_ready,

            "reason": (
                "Network input prepared against "
                "the exact 52-feature schema of "
                "the trained model."
                if ml_ready
                else
                "Network input is structurally "
                "prepared but does not meet "
                "ML-quality requirements."
            ),
        }


network_data_preparation_service = (
    NetworkDataPreparationService()
)