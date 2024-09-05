import abc
import datetime


class BaseLock(abc.ABC):
    @abc.abstractmethod
    async def try_lock(
        self,
        resource_id: str,
        lock_id: str,
        *,
        ttl: datetime.timedelta | None = None,
        owner: str | None = None,
    ) -> bool: ...

    @abc.abstractmethod
    async def unlock(self, resource_id: str, lock_id: str) -> None: ...
