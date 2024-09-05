from distlock.errors import BaseError


class NoLockError(BaseError):
    pass


class UninitializedError(BaseError):
    pass
