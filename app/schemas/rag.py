from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# DOCUMENT RESPONSE
# ============================================================

class RagDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    filename: str
    original_filename: str

    standard: str | None = None
    version: str | None = None

    pages: int
    chunks: int

    file_path: str
    status: str

    uploaded_by: str | None = None

    created_at: Any
    updated_at: Any


# ============================================================
# QUERY REQUEST
# ============================================================

class RagQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Compliance or security question",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


# ============================================================
# QUERY RESPONSE
# ============================================================

class RagQueryResponse(BaseModel):
    organization_id: str

    question: str

    answer: str

    compliance: list[dict[str, Any]]

    risk_assessment: dict[str, Any]

    recommendation: str

    risk_explanation: dict[str, Any]

    results: list[dict[str, Any]]


# ============================================================
# ACCESS CHECK REQUEST
# ============================================================

class RagAccessCheckRequest(BaseModel):
    resource: str = Field(
        ...,
        min_length=1,
        description="Resource being accessed",
    )

    resource_type: str = Field(
        default="resource",
        min_length=1,
    )

    action: str = Field(
        ...,
        min_length=1,
        description="Requested action such as read, write, delete",
    )

    context: dict[str, Any] = Field(
        default_factory=dict,
    )


# ============================================================
# ACCESS CHECK RESPONSE
# ============================================================

class RagAccessCheckResponse(BaseModel):
    organization_id: str

    user_id: str

    resource: str

    resource_type: str

    action: str

    access_granted: bool

    permission: str | None = None

    risk_level: str

    risk_score: float

    reason: str

    recommendation: str

    context: dict[str, Any]