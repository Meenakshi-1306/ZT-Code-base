from pathlib import Path

from app.database.database import DATABASE_URL


def test_database_url_is_absolute_and_points_to_project_db():
    root = Path(__file__).resolve().parents[1]
    db_path = (root / "zero_trust.db").resolve()
    assert DATABASE_URL == f"sqlite:///{db_path.as_posix()}"
