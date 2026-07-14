"""PostgreSQL engine and session helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend_api.http.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables and seed default actions / admin user."""
    # Import models so metadata is registered.
    from backend_api.db import models  # noqa: F401
    from backend_api.db.base import Base
    from backend_api.http.services.auth_service import seed_auth_data

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_auth_data(db)
    finally:
        db.close()
