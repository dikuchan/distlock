import pytest
from motor.motor_asyncio import AsyncIOMotorClient as MotorClient

from distlock.mongo import MongoLock
from distlock.mongo.errors import NoLockError


@pytest.mark.asyncio
async def test_try_lock(client: MotorClient) -> None:
    collection = client.get_database("distlock").get_collection("lock")
    lock = await MongoLock.new(collection)

    assert await lock.try_lock(
        resource_id="1",
        lock_id="1",
    )
    assert not await lock.try_lock(
        resource_id="1",
        lock_id="1",
    )
    await lock.unlock(
        resource_id="1",
        lock_id="1",
    )
    with pytest.raises(NoLockError):
        await lock.unlock(
            resource_id="1",
            lock_id="1",
        )
