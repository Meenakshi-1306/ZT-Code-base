from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MLDataPreparationRequest(BaseModel):
    organization_id: str
    source: str
    data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


class FeatureMapping(BaseModel):
    value: Any = None
    source: str
    confidence: float
    reason: str


class ModelPreparationResult(BaseModel):
    model: str
    features: List[str]
    prepared_data: Dict[str, Any]

    feature_details: Dict[str, FeatureMapping]

    provided_features: List[str] = Field(default_factory=list)
    derived_features: List[str] = Field(default_factory=list)
    estimated_features: List[str] = Field(default_factory=list)
    imputed_features: List[str] = Field(default_factory=list)
    defaulted_features: List[str] = Field(default_factory=list)

    unavailable_features: List[str] = Field(default_factory=list)
    missing_features: List[str] = Field(default_factory=list)
    extra_input_features: List[str] = Field(default_factory=list)

    coverage: float = 0.0

    # Structural compatibility
    model_compatible: bool = False

    # Whether data is good enough to actually invoke the model
    ml_ready: bool = False

    # Backward compatibility
    can_run_model: bool = False

    reason: str = ""


class DataQuality(BaseModel):
    total_input_fields: int = 0
    mapped_fields: int = 0
    derived_fields: int = 0
    estimated_fields: int = 0
    imputed_fields: int = 0
    defaulted_fields: int = 0
    unavailable_fields: int = 0
    unknown_fields: int = 0

    overall_coverage: float = 0.0
    overall_quality_score: float = 0.0


class MLDataPreparationResponse(BaseModel):
    success: bool

    organization_id: str
    source: str

    models_considered: List[str] = Field(default_factory=list)
    models_ready: List[str] = Field(default_factory=list)
    models_skipped: List[str] = Field(default_factory=list)

    prepared_models: Dict[str, ModelPreparationResult] = Field(
        default_factory=dict
    )

    data_quality: DataQuality

    message: str