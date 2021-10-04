#
#
# Copyright 2020-21 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from ..interface.driver import Driver as AbstractDriver

from typing import Tuple, AsyncContextManager, Optional

from urllib.parse import urlparse
import re

import aiopg
import agensgraph as ag  # noqa: F401

from async_exit_stack import AsyncExitStack

from .session import Session
from ..config import Config


def is_agensgraph_address(config: Config) -> bool:
    address = config.address
    return bool(re.match(r'^postgresql(\+.+)?$', urlparse(address).scheme))


def _construct_dsn(address: str, auth: Tuple[str, str]) -> str:
    addr = urlparse(address)
    hostname = addr.hostname or '127.0.0.1'
    port = addr.port or '5432'
    return f"host={hostname} user={auth[0]} password={auth[1]} port={port}"


@AbstractDriver.register_concrete(is_agensgraph_address)
class Driver (AbstractDriver):
    """This class encapsulates an agensgraph db driver
    """
    def __init__(self,
                 config: Config):
        super().__init__(config)
        self._exit_stack = AsyncExitStack()
        self._pool: Optional[aiopg.Pool] = None

        self.dsn = _construct_dsn(self._address, self._auth)

    def database_type(self) -> str:
        return "agensgraph"

    async def __aenter__(self) -> "Driver":
        await self
        return self

    async def __aexit__(self, e_t, e_v, e_tb) -> Optional[bool]:
        return await self._exit_stack.__aexit__(e_t, e_v, e_tb)

    def __await__(self):
        async def __inner():
            if self._pool is None:
                self._pool = await self._exit_stack.enter_async_context(aiopg.create_pool(self.dsn))
            return self._pool
        return __inner().__await__()

    def session(self, **kwargs) -> AsyncContextManager[Session]:
        """This method is used to create a Session object, which can be used as an
        asynchronous context manager.

        All interactions should be done via a Session object. Accessing the driver
        without one is not supported.
        """
        assert (self._pool is not None)
        return Session(self._pool, **kwargs)
