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
from .session import Session
from ..config import Config

import asyncio
import time
from typing import Optional, Callable, TypeVar, AsyncContextManager
from functools import wraps

import neo4j
from neo4j.exceptions import ServiceUnavailable
from async_generator import asynccontextmanager

from urllib.parse import urlparse
import re

T = TypeVar('T')


def _wrapped_in_executor(f: Callable[..., T]) -> Callable[..., 'asyncio.Future[T]']:
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(
            None,
            lambda: f(*args, **kwargs))

    return wrapper


def is_neo4j_address(config: Config) -> bool:
    address = config.address
    return any(re.match(regex, urlparse(address).scheme) for regex in (r'^neo4j(\+.+)?$', r'^bolt(\+.+)?$'))


@AbstractDriver.register_concrete(is_neo4j_address)
class Driver (AbstractDriver):
    """This class encapsulates the neo4j.Driver object, it's interface is similar but
    limited to what has been implemented yet.
    """
    def __init__(self,
                 config: Config):
        super().__init__(config)
        self._sync_driver: Optional['asyncio.Future[neo4j.Driver]'] = None

    def database_type(self) -> str:
        return "neo4j"

    @property
    def sync_driver(self) -> 'asyncio.Future[neo4j.Driver]':
        """This property is an asyncio Future wrapping the underlying neo4j.Driver object.
        """
        @_wrapped_in_executor
        def __create_sync_driver(address, auth, max_retries=20):
            backoff = 0
            while True:
                try:
                    return neo4j.GraphDatabase.driver(address, auth=auth)
                except (ServiceUnavailable, ConnectionRefusedError) as e:
                    backoff += 1
                    if backoff > max_retries:
                        raise TimeoutError from e
                    time.sleep(backoff)

        if self._sync_driver is None:
            self._sync_driver = __create_sync_driver(
                self._address,
                auth=self._auth)

        return self._sync_driver

    def __await__(self):
        return self.sync_driver.__await__()

    async def close(self) -> None:
        """This coroutine should be awaited when the driver is no longer needed.
        """
        if self._sync_driver is not None:
            sync_driver = await self._sync_driver
            await _wrapped_in_executor(sync_driver.close)()
            self._sync_driver = None

    def session(self, **kwargs) -> AsyncContextManager[Session]:
        """This method is used to create a aioneo4j.Session object, which can be used as an
        asynchronous context manager.

        All interactions should be done via a Session object. Accessing the driver
        without one is not supported.
        """
        @asynccontextmanager
        async def __inner(sync_driver: 'asyncio.Future[neo4j.Driver]'):
            session = Session(sync_driver, **kwargs)
            async with session:
                yield session

        return __inner(self.sync_driver)
