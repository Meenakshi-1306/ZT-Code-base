from sqlalchemy import inspect, text

from app.database.database import engine


def add_column_if_missing(
    connection,
    table_name: str,
    column_name: str,
    column_definition: str
):
    inspector = inspect(connection)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }

    if column_name not in existing_columns:
        connection.execute(
            text(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {column_definition}"
            )
        )
        print(f"Added column: {table_name}.{column_name}")
    else:
        print(f"Already exists: {table_name}.{column_name}")


def migrate():
    with engine.begin() as connection:

        add_column_if_missing(
            connection,
            "organizations",
            "organization_type",
            "VARCHAR"
        )

        add_column_if_missing(
            connection,
            "organizations",
            "email_domain",
            "VARCHAR"
        )

        add_column_if_missing(
            connection,
            "organizations",
            "country",
            "VARCHAR"
        )

        add_column_if_missing(
            connection,
            "organizations",
            "state",
            "VARCHAR"
        )

        add_column_if_missing(
            connection,
            "organizations",
            "gstin",
            "VARCHAR"
        )

        add_column_if_missing(
            connection,
            "organizations",
            "email_verified",
            "BOOLEAN DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "organizations",
            "verified_at",
            "DATETIME"
        )


if __name__ == "__main__":
    migrate()