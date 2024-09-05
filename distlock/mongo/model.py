import datetime
import typing


class ResourceLock(typing.TypedDict):
    lock_id: str | None
    created_at: datetime.datetime | None
    is_acquired: bool
    owner: str | None
    expires_at: datetime.datetime | None


class Resource(typing.TypedDict):
    resource_id: str
    lock: ResourceLock
