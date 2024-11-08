from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.config import settings
from database.unit_of_work import SQLAlchemyUnitOfWork

SQLALCHEMY_DATABASE_URI = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"

Base = declarative_base()


async def get_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with SQLAlchemyUnitOfWork(session) as db:
        yield db
