import os
from datetime import datetime, timedelta
from typing import Any, Generator
from uuid import uuid4

import pytest
from src.orm.models import Base, Competition, Organization, Cause, CompetitionMember
from src.main import app as main_app
from src.api.deps import get_db, auth
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.JWTBearer import JWTAuthorizationCredentials
from src.orm.models import User


# Default to using sqlite in memory for fast tests.
# Can be overridden by environment variable for testing in CI against other
# database engines
SQLALCHEMY_DATABASE_URL = os.getenv('TEST_DATABASE_URL', "sqlite://")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    Base.metadata.create_all(engine)  # Create the tables.
    _app = main_app
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def db_session(app: FastAPI) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()


@pytest.fixture()
def client(app: FastAPI, db_session: Session, user_sub) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    def _override_auth():
        return JWTAuthorizationCredentials(
            claims={"sub": user_sub},
            jwt_token="test",
            header={"Authorization": "Bearer xyz"},
            signature="test",
            message="test"
        )

    app.dependency_overrides[auth] = _override_auth
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def user_sub():
    return str(uuid4())


@pytest.fixture()
def auth_user(db_session: Session, user_sub: str):
    user = User(
        sub=user_sub,
        email="test@email.com",
        full_name="test user",
        given_name="test",
        timezone="America/New_York"
    )
    db_session.add(user)
    db_session.commit()

    return user
