import datetime
import typing

import pymongo
import pymongo.errors
import pytz
from motor.motor_asyncio import AsyncIOMotorClientSession as MotorClientSession
from motor.motor_asyncio import AsyncIOMotorCollection as MotorCollection

from distlock.base import BaseLock
from distlock.mongo.errors import NoLockError, UninitializedError
from distlock.mongo.model import Resource, ResourceLock

T = typing.TypeVar("T", bound="MongoLock")


class MongoLock(BaseLock):
    def __init__(
        self,
        _use_new: object,
        collection: MotorCollection[Resource],
        session: MotorClientSession | None = None,
    ) -> None:
        self.session = session
        self.collection = collection
        self._initialized = False

    @classmethod
    async def new(
        cls: type[T],
        collection: MotorCollection[Resource],
        session: MotorClientSession | None = None,
    ) -> T:
        lock = cls(object(), collection, session)
        await lock.init()
        return lock

    async def _create_indexes(self) -> None:
        await self.collection.create_indexes(
            indexes=[
                pymongo.IndexModel(
                    "resource_id",
                    unique=True,
                    background=False,
                    sparse=True,
                ),
                pymongo.IndexModel("lock.lock_id"),
                pymongo.IndexModel("lock.expires_at"),
            ],
            session=self.session,
        )

    async def init(self) -> None:
        if self._initialized:
            return
        await self._create_indexes()
        self._initialized = True

    async def try_lock(
        self,
        resource_id: str,
        lock_id: str,
        *,
        ttl: datetime.timedelta | None = None,
        owner: str | None = None,
    ) -> bool:
        if not self._initialized:
            raise UninitializedError()
        now = datetime.datetime.now(pytz.UTC)
        try:
            await self.collection.find_one_and_update(
                filter={
                    "resource_id": resource_id,
                    "$or": [
                        {"lock.is_acquired": False},
                        {"lock.expires_at": {"$lte": now}},
                    ],
                },
                update={
                    "$set": Resource(
                        resource_id=resource_id,
                        lock=ResourceLock(
                            lock_id=lock_id,
                            owner=owner,
                            created_at=now,
                            expires_at=None if ttl is None else now + ttl,
                            is_acquired=True,
                        ),
                    ),
                },
                upsert=True,
                return_document=True,
                session=self.session,
            )
        except pymongo.errors.DuplicateKeyError:
            return False
        return True

    async def unlock(self, resource_id: str, lock_id: str) -> None:
        if not self._initialized:
            raise UninitializedError()
        response = await self.collection.find_one_and_update(
            filter={
                "resource_id": resource_id,
                "lock.lock_id": lock_id,
            },
            update={
                "$set": {
                    "lock": ResourceLock(
                        lock_id=None,
                        created_at=None,
                        is_acquired=False,
                        owner=None,
                        expires_at=None,
                    ),
                },
            },
            session=self.session,
        )
        if response is None:
            raise NoLockError()
