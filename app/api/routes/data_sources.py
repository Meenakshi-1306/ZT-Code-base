from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.dependencies import require_permission
from app.database.database import get_db

from app.controllers.data_source_controller import (
    DataSourceController
)

from app.schemas.common import APIResponse

from app.schemas.data_source import (
    DataSourceCreateRequest,
    DataSourceListResponse,
    DataSourceResponse,
    DataSourceTestResponse,
    DataSourceUpdateRequest,
    FileSourceResponse,
    FileSourceListResponse,
    DatabaseSourceCreateRequest,
    DatabaseSourceCreateResponse,
    DatabaseSourceListResponse,
    ApiSourceCreateRequest,
    ApiSourceCreateResponse,
    ApiSourceListResponse,
    StreamSourceCreateRequest,
    StreamSourceCreateResponse,
    StreamSourceListResponse
)


router = APIRouter(
    prefix="/api",
    tags=["Data Sources"]
)


# ============================================================
# FILE DATA SOURCES
# ============================================================

@router.post(
    "/data-sources/files",
    response_model=FileSourceResponse
)
async def upload_file_source(
    file: UploadFile = File(...),
    name: str = Form(None),
    event_type: str = Form(None),
    db: Session = Depends(get_db)
):
    content = await file.read()
    filename = file.filename or "file.csv"
    return DataSourceController.upload_file_source(
        db=db,
        filename=filename,
        content=content,
        name=name,
        event_type=event_type
    )


@router.get(
    "/data-sources/files",
    response_model=FileSourceListResponse
)
def list_file_sources(
    db: Session = Depends(get_db)
):
    return DataSourceController.list_file_sources(db=db)


# ============================================================
# DATABASE DATA SOURCES
# ============================================================

@router.post(
    "/data-sources/databases",
    response_model=DatabaseSourceCreateResponse
)
def create_database_source(
    request: DatabaseSourceCreateRequest,
    db: Session = Depends(get_db)
):
    return DataSourceController.create_database_source(
        db=db,
        request=request
    )


@router.get(
    "/data-sources/databases",
    response_model=DatabaseSourceListResponse
)
def list_database_sources(
    db: Session = Depends(get_db)
):
    return DataSourceController.list_database_sources(db=db)


# ============================================================
# API / WEBHOOK DATA SOURCES
# ============================================================

@router.post(
    "/data-sources/apis",
    response_model=ApiSourceCreateResponse
)
def create_api_source(
    request: ApiSourceCreateRequest,
    db: Session = Depends(get_db)
):
    return DataSourceController.create_api_source(
        db=db,
        request=request
    )


@router.get(
    "/data-sources/apis",
    response_model=ApiSourceListResponse
)
def list_api_sources(
    db: Session = Depends(get_db)
):
    return DataSourceController.list_api_sources(db=db)


# ============================================================
# LIVE STREAM DATA SOURCES
# ============================================================

@router.post(
    "/data-sources/streams",
    response_model=StreamSourceCreateResponse
)
def create_stream_source(
    request: StreamSourceCreateRequest,
    db: Session = Depends(get_db)
):
    return DataSourceController.create_stream_source(
        db=db,
        request=request
    )


@router.get(
    "/data-sources/streams",
    response_model=StreamSourceListResponse
)
def list_stream_sources(
    db: Session = Depends(get_db)
):
    return DataSourceController.list_stream_sources(db=db)



# ============================================================
# LIST
# ============================================================

@router.get(
    "/organizations/{organization_id}/data-sources",
    response_model=APIResponse[DataSourceListResponse]
)
def list_data_sources(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_VIEW")
    )
):

    try:

        data = DataSourceController.list_data_sources(
            db=db,
            organization_id=organization_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Data sources retrieved successfully"
        }

    except ValueError as exc:

        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# CREATE
# ============================================================

@router.post(
    "/organizations/{organization_id}/data-sources",
    response_model=APIResponse[DataSourceResponse]
)
def create_data_source(
    organization_id: str,
    request: DataSourceCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_UPDATE")
    )
):

    try:

        source = DataSourceController.create_data_source(
            db=db,
            organization_id=organization_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": {
                "id": source.id,
                "organization_id": source.organization_id,
                "name": source.name,
                "source_type": source.source_type,
                "description": source.description,
                "connection_config": request.connection_config,
                "status": source.status,
                "enabled": source.enabled,
                "last_sync_at": source.last_sync_at,
                "created_at": source.created_at,
                "updated_at": source.updated_at
            },
            "message": "Data source created successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# GET
# ============================================================

@router.get(
    "/data-sources/{data_source_id}",
    response_model=APIResponse[DataSourceResponse]
)
def get_data_source(
    data_source_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_VIEW")
    )
):

    try:

        data = DataSourceController.get_data_source(
            db=db,
            data_source_id=data_source_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Data source retrieved successfully"
        }

    except ValueError as exc:

        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# UPDATE
# ============================================================

@router.patch(
    "/data-sources/{data_source_id}",
    response_model=APIResponse[DataSourceResponse]
)
def update_data_source(
    data_source_id: str,
    request: DataSourceUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_UPDATE")
    )
):

    try:

        source = DataSourceController.update_data_source(
            db=db,
            data_source_id=data_source_id,
            request=request,
            current_user=current_user
        )

        return {
            "success": True,
            "data": DataSourceController.get_data_source(
                db=db,
                data_source_id=data_source_id,
                current_user=current_user
            ),
            "message": "Data source updated successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# DELETE
# ============================================================

@router.delete(
    "/data-sources/{data_source_id}"
)
def delete_data_source(
    data_source_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_UPDATE")
    )
):

    try:

        data = DataSourceController.delete_data_source(
            db=db,
            data_source_id=data_source_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Data source deleted successfully"
        }

    except ValueError as exc:

        status_code = 400

        if "not found" in str(exc).lower():
            status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )


# ============================================================
# TEST CONNECTION
# ============================================================

@router.post(
    "/data-sources/{data_source_id}/test",
    response_model=APIResponse[DataSourceTestResponse]
)
def test_data_source(
    data_source_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("TEAM_VIEW")
    )
):

    try:

        data = DataSourceController.test_connection(
            db=db,
            data_source_id=data_source_id,
            current_user=current_user
        )

        return {
            "success": True,
            "data": data,
            "message": "Data source test completed"
        }

    except ValueError as exc:

        status_code = 404

        if "access" in str(exc).lower():
            status_code = 403

        raise HTTPException(
            status_code=status_code,
            detail=str(exc)
        )