from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


DATABASE_URL = "sqlite:///./data/live.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def initialize_database() -> None:
    """Create the agent's additional tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Create and return a new database session."""
    return SessionLocal()