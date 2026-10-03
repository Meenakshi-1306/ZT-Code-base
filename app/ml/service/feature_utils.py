from typing import Any, Dict, Optional
from datetime import datetime


# ============================================================
# NORMALIZE KEY
# ============================================================

def normalize_key(value: Any) -> str:
    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
        .replace(".", "")
        .replace("/", "")
    )


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int, float)):
        return float(value)

    try:
        text = str(value).strip()

        if not text:
            return None

        return float(text)

    except (TypeError, ValueError):
        return None


# ============================================================
# MAPPING
# ============================================================

def mapping(
    value: Any,
    source: str,
    confidence: float,
    reason: str,
) -> Dict[str, Any]:

    return {
        "value": value,
        "source": source,
        "confidence": confidence,
        "reason": reason,
    }


# ============================================================
# FIND INPUT VALUE
# ============================================================

def find_input_value(
    data: Dict[str, Any],
    feature: str,
    aliases=None,
):
    """
    Standalone version used by Network service.

    Returns:
        value, source, source_field
    """

    if not data:
        return None, None, None

    aliases = aliases or []

    candidates = [
        feature,
        *aliases,
    ]

    normalized_data = {
        normalize_key(key): key
        for key in data.keys()
    }

    for candidate in candidates:

        normalized_candidate = normalize_key(
            candidate
        )

        if normalized_candidate not in normalized_data:
            continue

        original_key = normalized_data[
            normalized_candidate
        ]

        value = data.get(original_key)

        if value is None:
            continue

        if value == "":
            continue

        return (
            value,
            "provided",
            original_key,
        )

    return (
        None,
        None,
        None,
    )


# ============================================================
# CLASSIFY FEATURES
# ============================================================

def classify_features(
    feature_details: Dict[str, Dict[str, Any]]
):
    """
    Standalone version used by Network service.
    """

    provided = []
    derived = []
    estimated = []
    imputed = []
    defaulted = []
    unavailable = []

    for feature, detail in feature_details.items():

        source = str(
            detail.get(
                "source",
                "",
            )
        ).lower()

        if source == "provided":

            provided.append(feature)

        elif source == "derived":

            derived.append(feature)

        elif source in (
            "estimated",
            "relationship_estimated",
        ):

            estimated.append(feature)

        elif source in (
            "imputed",
            "historical_imputed",
        ):

            imputed.append(feature)

        elif source == "default":

            defaulted.append(feature)

        elif source == "unavailable":

            unavailable.append(feature)

        else:

            unavailable.append(feature)

    return (
        provided,
        derived,
        estimated,
        imputed,
        defaulted,
        unavailable,
    )


# ============================================================
# QUALITY SCORE
# ============================================================

def quality_score(
    feature_details: Dict[str, Dict[str, Any]]
) -> float:

    if not feature_details:
        return 0.0

    scores = []

    for detail in feature_details.values():

        confidence = detail.get(
            "confidence",
            0.0,
        )

        try:
            scores.append(
                float(confidence)
            )

        except (
            TypeError,
            ValueError,
        ):
            scores.append(0.0)

    if not scores:
        return 0.0

    return round(
        sum(scores) / len(scores),
        4,
    )


# ============================================================
# ADD FEATURE
# ============================================================

def add_feature(
    feature_details: Dict[str, Dict[str, Any]],
    prepared_data: Dict[str, Any],
    feature: str,
    value: Any,
    source: str,
    confidence: float,
    reason: str,
):

    prepared_data[feature] = value

    feature_details[feature] = {
        "value": value,
        "source": source,
        "confidence": confidence,
        "reason": reason,
    }


# ============================================================
# UNKNOWN INPUT FEATURES
# ============================================================

def get_unknown_input_features(
    data: Dict[str, Any],
    known_features,
    aliases=None,
):

    if not data:
        return []

    known_features = known_features or set()
    aliases = aliases or {}

    normalized_known = {
        normalize_key(feature)
        for feature in known_features
    }

    normalized_aliases = set()

    for alias_list in aliases.values():

        for alias in alias_list:

            normalized_aliases.add(
                normalize_key(alias)
            )

    unknown = []

    for key in data.keys():

        normalized = normalize_key(key)

        if normalized in normalized_known:
            continue

        if normalized in normalized_aliases:
            continue

        unknown.append(key)

    return unknown


# ============================================================
# TIMESTAMP
# ============================================================

def parse_timestamp(
    value: Any,
) -> Optional[datetime]:

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value

    text = str(value).strip()

    if not text:
        return None

    try:

        return datetime.fromisoformat(
            text.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError:
        pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:

        try:

            return datetime.strptime(
                text,
                fmt,
            )

        except ValueError:
            continue

    return None


# ============================================================
# FEATURE UTILS CLASS
# ============================================================

class FeatureUtils:

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    @staticmethod
    def normalize_key(
        value: Any,
    ):
        return normalize_key(value)

    # --------------------------------------------------------
    # SAFE FLOAT
    # --------------------------------------------------------

    @staticmethod
    def safe_float(
        value: Any,
    ):
        return safe_float(value)

    # --------------------------------------------------------
    # MAPPING
    # --------------------------------------------------------

    @staticmethod
    def mapping(
        value: Any,
        source: str,
        confidence: float,
        reason: str,
    ):
        return mapping(
            value,
            source,
            confidence,
            reason,
        )

    # --------------------------------------------------------
    # ADD FEATURE
    # --------------------------------------------------------

    @staticmethod
    def add_feature(
        feature_details,
        prepared_data,
        feature,
        value,
        source,
        confidence,
        reason,
    ):

        add_feature(
            feature_details,
            prepared_data,
            feature,
            value,
            source,
            confidence,
            reason,
        )

    # --------------------------------------------------------
    # FIND INPUT VALUE
    # --------------------------------------------------------

    @staticmethod
    def find_input_value(
        data: Dict[str, Any],
        feature_name: str = None,
        aliases=None,
        feature: str = None,
    ):
        """
        IMPORTANT:
        Supports both:

            feature_name="..."

        and

            feature="..."

        because different services may use either.
        """

        actual_feature = (
            feature_name
            if feature_name is not None
            else feature
        )

        if actual_feature is None:
            return None

        value, source, source_field = (
            find_input_value(
                data=data,
                feature=actual_feature,
                aliases=aliases,
            )
        )

        if source is None:
            return None

        return {
            "value": value,
            "source": source,
            "source_field": source_field,
            "confidence": 1.0,
            "reason": (
                f"Input field '{source_field}' "
                f"matched model feature "
                f"'{actual_feature}'."
            ),
        }

    # --------------------------------------------------------
    # CLASSIFY
    # --------------------------------------------------------

    @staticmethod
    def classify_features(
        feature_details,
    ):

        (
            provided,
            derived,
            estimated,
            imputed,
            defaulted,
            unavailable,
        ) = classify_features(
            feature_details
        )

        return {
            "provided_features": provided,
            "derived_features": derived,
            "estimated_features": estimated,
            "imputed_features": imputed,
            "defaulted_features": defaulted,
            "unavailable_features": unavailable,
        }

    # --------------------------------------------------------
    # QUALITY SCORE
    # --------------------------------------------------------

    @staticmethod
    def calculate_quality_score(
        feature_details,
    ):
        return quality_score(
            feature_details
        )

    # --------------------------------------------------------
    # COVERAGE
    # --------------------------------------------------------

    @staticmethod
    def calculate_coverage(
        total_features,
        feature_details,
    ):
        """
        IMPORTANT:
        Existing services call:

            calculate_coverage(
                len(self.features),
                feature_details
            )

        So the argument order is intentionally:

            total_features
            feature_details
        """

        if total_features <= 0:
            return 0.0

        if not feature_details:
            return 0.0

        usable = 0

        for detail in feature_details.values():

            source = str(
                detail.get(
                    "source",
                    "",
                )
            ).lower()

            if source != "unavailable":
                usable += 1

        return round(
            usable / total_features,
            4,
        )

    # --------------------------------------------------------
    # UNKNOWN INPUT
    # --------------------------------------------------------

    @staticmethod
    def get_unknown_input_features(
        data,
        known_features,
        aliases=None,
    ):

        return get_unknown_input_features(
            data=data,
            known_features=known_features,
            aliases=aliases,
        )

    # --------------------------------------------------------
    # TIMESTAMP
    # --------------------------------------------------------

    @staticmethod
    def parse_timestamp(
        value,
    ):

        return parse_timestamp(
            value
        )