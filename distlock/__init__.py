# ruff: noqa

# Install `distlock[mongo]`.
try:
    from distlock import mongo
except ImportError:
    pass
