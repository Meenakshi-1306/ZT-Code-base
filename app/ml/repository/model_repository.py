from pathlib import Path
import os
import joblib
from typing import Dict, List, Any


class ModelRepository:
    """
    Central repository for loading and accessing all trained ML models.

    This class:
    - Loads existing .pkl models
    - Does NOT retrain models
    - Does NOT modify models
    - Dynamically discovers model feature schemas
    - Provides model metadata to the data-preparation service
    """

    def __init__(self, model_directory: str = None):
        if model_directory is None:
            model_directory = str(Path(__file__).resolve().parent.parent / "models")
        self.model_directory = model_directory

        # Loaded models
        self.network_model = None
        self.aws_model = None
        self.gb_model = None
        self.zt_if_model = None
        self.zt_encoder = None

        # Feature schemas
        self.network_features: List[str] = []
        self.aws_features: List[str] = []
        self.gb_features: List[str] = []
        self.zt_encoder_features: List[str] = []

        # ZT Isolation Forest does not necessarily contain
        # feature_names_in_, so we keep its expected count.
        self.zt_if_feature_count: int = 0

        self._load_models()
        self._discover_schemas()

    # ============================================================
    # MODEL LOADING
    # ============================================================

    def _load_models(self):
        """Load all trained models from the models directory."""

        model_paths = {
            "network": "network_logs_rf_model.pkl",
            "aws": "awscloud_logs_if_model.pkl",
            "gb": "zero_trust_gradient_boosting.pkl",
            "zt_if": "zero_trust_isolation_forest.pkl",
            "zt_encoder": "zero_trust_encoder.pkl",
        }

        loaded_models = {}

        for model_name, filename in model_paths.items():

            path = os.path.join(
                self.model_directory,
                filename
            )

            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Model file not found: {path}"
                )

            try:
                loaded_models[model_name] = joblib.load(path)

            except Exception as e:
                raise RuntimeError(
                    f"Failed to load model '{filename}': {str(e)}"
                ) from e

        self.network_model = loaded_models["network"]
        self.aws_model = loaded_models["aws"]
        self.gb_model = loaded_models["gb"]
        self.zt_if_model = loaded_models["zt_if"]
        self.zt_encoder = loaded_models["zt_encoder"]

    # ============================================================
    # FEATURE SCHEMA DISCOVERY
    # ============================================================

    def _discover_schemas(self):
        """
        Dynamically discover the feature schemas stored in the
        trained models.

        We do NOT manually hardcode the complete feature list.
        """

        # --------------------------------------------------------
        # Network Random Forest
        # --------------------------------------------------------

        if hasattr(self.network_model, "feature_names_in_"):
            self.network_features = list(
                self.network_model.feature_names_in_
            )
        else:
            raise ValueError(
                "Network model does not contain feature_names_in_."
            )

        # --------------------------------------------------------
        # AWS CloudTrail Isolation Forest
        # --------------------------------------------------------

        if hasattr(self.aws_model, "feature_names_in_"):
            self.aws_features = list(
                self.aws_model.feature_names_in_
            )
        else:
            raise ValueError(
                "AWS model does not contain feature_names_in_."
            )

        # --------------------------------------------------------
        # Zero Trust Gradient Boosting
        # --------------------------------------------------------

        if hasattr(self.gb_model, "feature_names_in_"):
            self.gb_features = list(
                self.gb_model.feature_names_in_
            )
        else:
            raise ValueError(
                "Gradient Boosting model does not contain "
                "feature_names_in_."
            )

        # --------------------------------------------------------
        # Zero Trust Encoder
        # --------------------------------------------------------

        if hasattr(self.zt_encoder, "feature_names_in_"):
            self.zt_encoder_features = list(
                self.zt_encoder.feature_names_in_
            )
        else:
            raise ValueError(
                "Zero Trust encoder does not contain "
                "feature_names_in_."
            )

        # --------------------------------------------------------
        # Zero Trust Isolation Forest
        # --------------------------------------------------------

        if hasattr(self.zt_if_model, "n_features_in_"):
            self.zt_if_feature_count = int(
                self.zt_if_model.n_features_in_
            )
        else:
            raise ValueError(
                "Zero Trust Isolation Forest does not contain "
                "n_features_in_."
            )

    # ============================================================
    # MODEL GETTERS
    # ============================================================

    def get_network_model(self):
        return self.network_model

    def get_aws_model(self):
        return self.aws_model

    def get_gb_model(self):
        return self.gb_model

    def get_zt_if_model(self):
        return self.zt_if_model

    def get_zt_encoder(self):
        return self.zt_encoder

    # ============================================================
    # FEATURE GETTERS
    # ============================================================

    def get_network_features(self) -> List[str]:
        return self.network_features.copy()

    def get_aws_features(self) -> List[str]:
        return self.aws_features.copy()

    def get_gb_features(self) -> List[str]:
        return self.gb_features.copy()

    def get_zt_encoder_features(self) -> List[str]:
        return self.zt_encoder_features.copy()

    def get_zt_if_feature_count(self) -> int:
        return self.zt_if_feature_count

    # ============================================================
    # COMPLETE MODEL SCHEMA
    # ============================================================

    def get_model_schema(self) -> Dict[str, Any]:
        """
        Return complete information about all loaded models.

        This is useful for the Data Preparation Service because
        it can discover exactly what each model expects.
        """

        return {
            "network": {
                "model_type": type(
                    self.network_model
                ).__name__,
                "feature_count": len(
                    self.network_features
                ),
                "features": self.network_features.copy(),
            },

            "aws": {
                "model_type": type(
                    self.aws_model
                ).__name__,
                "feature_count": len(
                    self.aws_features
                ),
                "features": self.aws_features.copy(),
            },

            "gradient_boosting": {
                "model_type": type(
                    self.gb_model
                ).__name__,
                "feature_count": len(
                    self.gb_features
                ),
                "features": self.gb_features.copy(),
            },

            "zero_trust_encoder": {
                "model_type": type(
                    self.zt_encoder
                ).__name__,
                "feature_count": len(
                    self.zt_encoder_features
                ),
                "features": self.zt_encoder_features.copy(),
            },

            "zero_trust_isolation_forest": {
                "model_type": type(
                    self.zt_if_model
                ).__name__,
                "feature_count": self.zt_if_feature_count,
            },
        }

    # ============================================================
    # MODEL FEATURE CHECK
    # ============================================================

    def get_missing_features(
        self,
        model_name: str,
        provided_features: List[str]
    ) -> List[str]:
        """
        Return the features required by a model but not supplied
        by the organization.

        This does NOT fill the missing values.
        It only identifies them.
        """

        model_features_map = {
            "network": self.network_features,
            "aws": self.aws_features,
            "gradient_boosting": self.gb_features,
            "zero_trust_encoder": self.zt_encoder_features,
        }

        if model_name not in model_features_map:
            raise ValueError(
                f"Unknown model name: {model_name}"
            )

        required_features = set(
            model_features_map[model_name]
        )

        provided = set(provided_features)

        return sorted(
            required_features - provided
        )

    # ============================================================
    # MODEL FEATURE CHECK
    # ============================================================

    def get_extra_features(
        self,
        model_name: str,
        provided_features: List[str]
    ) -> List[str]:
        """
        Return organization-provided fields that are not required
        by the selected model.

        These fields are NOT errors.
        They can simply be ignored for that model.
        """

        model_features_map = {
            "network": self.network_features,
            "aws": self.aws_features,
            "gradient_boosting": self.gb_features,
            "zero_trust_encoder": self.zt_encoder_features,
        }

        if model_name not in model_features_map:
            raise ValueError(
                f"Unknown model name: {model_name}"
            )

        required_features = set(
            model_features_map[model_name]
        )

        provided = set(provided_features)

        return sorted(
            provided - required_features
        )

    # ============================================================
    # PRINT SCHEMA
    # ============================================================

    def print_model_schema(self):
        """
        Print all discovered model schemas.
        Useful during development/debugging.
        """

        schema = self.get_model_schema()

        print("\n" + "=" * 70)
        print("ML MODEL SCHEMAS")
        print("=" * 70)

        for model_name, model_info in schema.items():

            print(f"\nMODEL: {model_name}")
            print(
                f"TYPE: {model_info['model_type']}"
            )
            print(
                f"FEATURE COUNT: {model_info['feature_count']}"
            )

            if "features" in model_info:
                print("FEATURES:")

                for index, feature in enumerate(
                    model_info["features"],
                    start=1
                ):
                    print(
                        f"  {index:03d}. {feature}"
                    )

        print("\n" + "=" * 70)


# ================================================================
# SINGLE REPOSITORY INSTANCE
# ================================================================

model_repository = ModelRepository()