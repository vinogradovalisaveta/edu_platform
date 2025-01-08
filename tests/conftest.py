import os
from typing import Generator, Any

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

import settings
from db.session import get_db
from main import app

test_engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)

test_async_session = sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)

CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    os.system("alembic init migrations")
    os.system('alembic revision --autogenerate -m "test running migrations"')
    os.system("alembic upgrade head")


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """clean all the data from tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table in CLEAN_TABLES:
                await session.execute(f"""TRUNCATE TABLE {table};""")


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    """creates a fastapi testclient that uses db_session fixture for get_db dependency"""

    async def _get_test_db():
        try:
            yield test_async_session()
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
