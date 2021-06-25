# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

"""A limited asyncio wrapper for various cypher drivers

This is not intended to be a full driver wrapper, but just to implement the things
we immediately need in a relatively simple fashion, replicating the interface of the wrapped
library where possible.
"""

from .interface.driver import Driver
from .interface.session import Session
from .interface.transaction import Transaction
from .interface.result import Result
from .interface.relationship import Relationship
from .interface.node import Node
from .interface.exceptions import QueryFailed
from .empty import EmptyResult
from .config import Config

try:
    from . import aioneo4j  # noqa: F401
except ImportError:
    pass


try:
    from . import aioagensgraph  # noqa: F401
except ImportError:
    pass


__all__ = [
    'Driver',
    'Session',
    'Transaction',
    'Result',
    'Relationship',
    'Node',
    'EmptyResult',
    'QueryFailed',
    'Config'
]
