from datetime import datetime

from pydantic import BaseModel, Field


class DataSourceCreateRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=150
    )

    source_type: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    connection_config: dict | None = None


class DataSourceUpdateRequest(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    source_type: str | None = Field(
        default=None,
        max_length=50
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )

    connection_config: dict | None = None

    status: str | None = Field(
        default=None,
        pattern="^(active|inactive|error)$"
    )

    enabled: bool | None = None


class DataSourceResponse(BaseModel):

    id: str
    organization_id: str
    name: str
    source_type: str
    description: str | None = None
    connection_config: dict | None = None
    status: str
    enabled: bool
    last_sync_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DataSourceListResponse(BaseModel):

    organization_id: str
    data_sources: list[DataSourceResponse] = []
    total: int


class DataSourceTestResponse(BaseModel):

    data_source_id: str
    status: str
    message: str


# ============================================================
# NEW DATA SOURCE SCHEMAS
# ============================================================

class FileSourceResponse(BaseModel):
    success: bool = True
    source_id: str
    name: str
    file_name: str
    format: str
    status: str
    records: int


class FileSourceItem(BaseModel):
    source_id: str
    name: str
    file_name: str
    format: str
    records: int
    status: str


class FileSourceListResponse(BaseModel):
    success: bool = True
    sources: list[FileSourceItem] = []


class DatabaseSourceCreateRequest(BaseModel):
    name: str
    database_type: str
    connection_string: str | None = None
    database_file: str | None = None


class DatabaseSourceCreateResponse(BaseModel):
    success: bool = True
    source_id: str
    name: str
    database_type: str
    status: str
    tables: list[str]


class DatabaseSourceItem(BaseModel):
    source_id: str
    name: str
    database_type: str
    status: str
    tables: int
    last_sync: str | None = None


class DatabaseSourceListResponse(BaseModel):
    success: bool = True
    sources: list[DatabaseSourceItem] = []


class ApiSourceCreateRequest(BaseModel):
    name: str
    type: str
    url: str | None = None
    method: str | None = None
    authentication: dict | None = None
    event_type: str | None = None


class ApiSourceCreateResponse(BaseModel):
    success: bool = True
    source_id: str
    name: str
    type: str
    status: str
    webhook_url: str | None = None


class ApiSourceItem(BaseModel):
    source_id: str
    name: str
    type: str
    status: str
    last_sync: str | None = None
    events_received: int | None = None


class ApiSourceListResponse(BaseModel):
    success: bool = True
    sources: list[ApiSourceItem] = []


class StreamSourceCreateRequest(BaseModel):
    name: str
    stream_type: str
    broker: str
    topic: str
    event_type: str | None = None


class StreamSourceCreateResponse(BaseModel):
    success: bool = True
    source_id: str
    name: str
    stream_type: str
    status: str
    topic: str


class StreamSourceItem(BaseModel):
    source_id: str
    name: str
    stream_type: str
    topic: str
    status: str
    events_received: int


class StreamSourceListResponse(BaseModel):
    success: bool = True
    sources: list[StreamSourceItem] = []