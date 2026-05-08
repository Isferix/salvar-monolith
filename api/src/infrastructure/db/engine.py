from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.orm import Base

from ...settings import get_settings

settings = get_settings()

engine = create_engine(
    str(settings.db_uri),
    echo=settings.echo_sql,
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    # solo para dev; en prod usar Alembic
    Base.metadata.create_all(bind=engine)


def get_db():
    with SessionLocal() as session:
        yield session


if __name__ == "__main__":
    init_db()
