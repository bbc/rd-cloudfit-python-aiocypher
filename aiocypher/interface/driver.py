# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from .session import Session
from ..config import Config

from ..internal.abc import AIOCypherABCMeta

from typing import Tuple, Optional, AsyncContextManager


class Driver (object, metaclass=AIOCypherABCMeta):
    """This class encapsulates a driver object for a cypher database. Concrete subclasses specialise in
    different databases.
    """
    def __init__(self,
                 config: Config):
        self._address = config.address
        self._auth: Tuple[str, str] = config.auth

    async def __aenter__(self) -> 'Driver':
        return self

    async def __aexit__(self, e_t, e_v, e_tb) -> Optional[bool]:
        await self.close()
        return False

    def __await__(self):
        ...

    async def close(self) -> None:
        """This coroutine should be awaited when the driver is no longer needed.
        """
        ...

    def session(self, **kwargs) -> AsyncContextManager[Session]:
        """This method is used to create a Session object, which can be used as an
        asynchronous context manager.

        All interactions should be done via a Session object. Accessing the driver
        without one is not supported.
        """
        ...

    def database_type(self) -> str:
        ...
