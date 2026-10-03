from sqlalchemy.orm import Session

from app.models.data_source import DataSource


class DataSourceRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        data_source_id: str
    ) -> DataSource | None:

        return (
            db.query(DataSource)
            .filter(
                DataSource.id == data_source_id
            )
            .first()
        )

    @staticmethod
    def get_by_organization(
        db: Session,
        organization_id: str
    ) -> list[DataSource]:

        return (
            db.query(DataSource)
            .filter(
                DataSource.organization_id == organization_id
            )
            .order_by(
                DataSource.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def get_by_name(
        db: Session,
        organization_id: str,
        name: str
    ) -> DataSource | None:

        return (
            db.query(DataSource)
            .filter(
                DataSource.organization_id == organization_id,
                DataSource.name == name
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        data_source: DataSource
    ) -> DataSource:

        db.add(data_source)
        db.commit()
        db.refresh(data_source)

        return data_source

    @staticmethod
    def update(
        db: Session,
        data_source: DataSource,
        update_data: dict
    ) -> DataSource:

        for field, value in update_data.items():

            if hasattr(data_source, field):
                setattr(
                    data_source,
                    field,
                    value
                )

        db.commit()
        db.refresh(data_source)

        return data_source

    @staticmethod
    def delete(
        db: Session,
        data_source: DataSource
    ):

        db.delete(data_source)
        db.commit()