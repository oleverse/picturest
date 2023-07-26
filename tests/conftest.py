import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from api.database.models import Base
from api.database.db import get_db

from pathlib import Path


TEST_DB_FILE_NAME = Path(__file__).parent / "test.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        os.remove(TEST_DB_FILE_NAME)


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "testuser", "email": "testuser@example.com", "password": "123456789"}
