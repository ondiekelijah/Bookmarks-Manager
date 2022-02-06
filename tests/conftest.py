# All fixtures available in this file are made available to all test files automatically
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app

from app.config import settings
from app.database import get_db
from app.database import Base
from app.oath2 import create_access_token
from app import models
from alembic import command


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.test_database}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture()
def session():
    """
    Every time a test is run, we create and drop tables, connect to a testing database,
    and use it for all the tests,
    so we create a database connection that is independent of the main app.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    """
    Connects to the new test database and overrides the initial database
    connection set for the main app

    """

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    user_data = {"email": "test@gmail.com", "password": "Test123&^$"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    assert res.status_code == 201
    return new_user


@pytest.fixture()
def test_user2(client):
    user_data = {"email": "test2@gmail.com", "password": "Test123&^$"}
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user["password"] = user_data["password"]
    assert res.status_code == 201
    return new_user


@pytest.fixture()
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture()
def authorized_client(client, token):
    """
    Takes original client and adds the token from the token fixture - adds the
    Authorization header
    """
    # Update the headers so that it contains a token
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture()
def test_bookmarks(test_user, test_user2, session):
    data = [
        {
            "body": "GitHub",
            "url": "https://github.com/Dev-Elie",
            "user_id": test_user["id"],
        },
        {
            "body": "Twitter",
            "url": "https://twitter.com/dev_elie",
            "user_id": test_user["id"],
        },
        {
            "body": "Linkedin",
            "url": "https://www.linkedin.com/in/ondiek-elijah-2aaba4198/",
            "user_id": test_user["id"],
        },
        {
            "body": "Hashnode",
            "url": "https://develie.hashnode.dev/",
            "user_id": test_user2["id"],
        },
    ]

    def create_bookmark_model(bookmark):
        return models.Bookmarks(**bookmark)

    mapped_bookmarks = map(create_bookmark_model, data)
    bookmarks = list(mapped_bookmarks)

    session.add_all(bookmarks)
    session.commit()

    bookmarks = session.query(models.Bookmarks).all()

    # Returns an sqlalchemy model
    return bookmarks
