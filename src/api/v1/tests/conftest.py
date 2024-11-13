import sys
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

# Make the app.py accessible in tree structure.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from app import app
from src.api.v1.schemas.user import UserCreate
from src.api.v1.utils.user_service import UserService
from database.db_connection import Base, get_db

SQLITE_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()

    Base.metadata.create_all(bind=engine)

    session = TestSession(bind=connection)
    yield session

    session.close()

    Base.metadata.drop_all(bind=engine)

    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def create_user(db_session):
    return UserService().create_user(
        UserCreate(
            full_name="Admin", email="admin@gmail.com", password="Admin@123"
        ),
        db_session,
    )
