import os

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient as MockMotorClient
from motor.motor_asyncio import AsyncIOMotorClient as MotorClient


@pytest.fixture
def client_url() -> str | None:
    return os.getenv("DISTLOCK_MONGO_URL")


@pytest_asyncio.fixture
async def client(client_url: str | None) -> MotorClient | MockMotorClient:
    if client_url is None:
        return MockMotorClient()
    print("Running integration tests")
    return MotorClient(client_url)
