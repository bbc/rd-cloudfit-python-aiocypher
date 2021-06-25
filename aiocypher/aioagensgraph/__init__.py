# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""A limited asyncio wrapper for the agensgraph driver

This is not intended to be a full driver wrapper, but just to implement the things
we immediately need in a relatively simple fashion, replicating the interface of
aioneo4j where possible.
"""

from typing import List

__all__: List[str] = []

try:
    from .driver import Driver  # noqa: F401
except ImportError:
    pass
else:
    __all__.append('Driver')
