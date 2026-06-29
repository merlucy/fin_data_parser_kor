from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings

engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


def get_session() -> Session:
    return SessionLocal()
