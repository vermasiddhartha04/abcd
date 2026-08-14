from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


def test_connection():
    try:
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            print("=" * 60)
            print("✅ PostgreSQL Connected Successfully!")
            print("=" * 60)

            database = conn.execute(
                text("SELECT current_database();")
            ).scalar()

            version = conn.execute(
                text("SELECT version();")
            ).scalar()

            print(f"Database : {database}")
            print(f"Version  : {version}")

            print("=" * 60)

    except SQLAlchemyError as e:
        print("=" * 60)
        print("❌ Database Connection Failed")
        print("=" * 60)
        print(e)


if __name__ == "__main__":
    test_connection()