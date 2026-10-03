from sqlalchemy.orm import Session

from app.models.user import User

from app.schemas.data_source import (
    DataSourceCreateRequest,
    DataSourceUpdateRequest
)

from app.services.data_source_service import (
    DataSourceService
)


class DataSourceController:

    @staticmethod
    def list_data_sources(
        db: Session,
        organization_id: str,
        current_user: User
    ):

        return DataSourceService.list_data_sources(
            db=db,
            organization_id=organization_id,
            current_user=current_user
        )

    @staticmethod
    def create_data_source(
        db: Session,
        organization_id: str,
        request: DataSourceCreateRequest,
        current_user: User
    ):

        return DataSourceService.create_data_source(
            db=db,
            organization_id=organization_id,
            name=request.name,
            source_type=request.source_type,
            description=request.description,
            connection_config=request.connection_config,
            current_user=current_user
        )

    @staticmethod
    def get_data_source(
        db: Session,
        data_source_id: str,
        current_user: User
    ):

        return DataSourceService.get_data_source(
            db=db,
            data_source_id=data_source_id,
            current_user=current_user
        )

    @staticmethod
    def update_data_source(
        db: Session,
        data_source_id: str,
        request: DataSourceUpdateRequest,
        current_user: User
    ):

        return DataSourceService.update_data_source(
            db=db,
            data_source_id=data_source_id,
            update_data=request.model_dump(
                exclude_unset=True
            ),
            current_user=current_user
        )

    @staticmethod
    def delete_data_source(
        db: Session,
        data_source_id: str,
        current_user: User
    ):

        return DataSourceService.delete_data_source(
            db=db,
            data_source_id=data_source_id,
            current_user=current_user
        )

    @staticmethod
    def test_connection(
        db: Session,
        data_source_id: str,
        current_user: User
    ):

        return DataSourceService.test_connection(
            db=db,
            data_source_id=data_source_id,
            current_user=current_user
        )

    @staticmethod
    def upload_file_source(
        db: Session,
        filename: str,
        content: bytes,
        name: str | None = None,
        event_type: str | None = None
    ):
        return DataSourceService.upload_file_source(
            db=db,
            filename=filename,
            content=content,
            name=name,
            event_type=event_type
        )

    @staticmethod
    def list_file_sources(db: Session):
        return DataSourceService.list_file_sources(db=db)

    @staticmethod
    def create_database_source(db: Session, request):
        return DataSourceService.create_database_source(
            db=db,
            request=request
        )

    @staticmethod
    def list_database_sources(db: Session):
        return DataSourceService.list_database_sources(db=db)

    @staticmethod
    def create_api_source(db: Session, request):
        return DataSourceService.create_api_source(
            db=db,
            request=request
        )

    @staticmethod
    def list_api_sources(db: Session):
        return DataSourceService.list_api_sources(db=db)

    @staticmethod
    def create_stream_source(db: Session, request):
        return DataSourceService.create_stream_source(
            db=db,
            request=request
        )

    @staticmethod
    def list_stream_sources(db: Session):
        return DataSourceService.list_stream_sources(db=db)