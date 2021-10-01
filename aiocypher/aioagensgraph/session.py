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

from ..interface.session import Session as AbstractSession

from typing import AsyncContextManager, Optional
from async_exit_stack import AsyncExitStack

import aiopg

from .transaction import Transaction


class Session (AbstractSession):
    """This object encapsulates a session with an agensgraph database. It should not be initialised directly, but
    created via an Driver object.

    It should always be used as an Async Context Manager, and using its methods outside of its
    context may lead to undefined behaviour.
    """
    def __init__(self, pool: aiopg.Pool, **kwargs):
        self._exit_stack = AsyncExitStack()
        self._pool = pool
        self._connection: Optional[aiopg.Connection] = None
        self.__kwargs = kwargs

        self._dbname = self.__kwargs.get('database', "database") or "database"

    async def __aenter__(self) -> 'Session':
        await self._exit_stack.__aenter__()
        await self
        return self

    async def __aexit__(self, *args) -> bool:
        return await self._exit_stack.__aexit__(*args)

    def __await__(self):
        async def __inner():
            if self._connection is None:
                self._connection = await self._exit_stack.enter_async_context(self._pool.acquire())
            return self._connection
        return __inner().__await__()

    def begin_transaction(self) -> AsyncContextManager[Transaction]:
        """This is the main method for interacting with the Session. It
        creates a new Transaction which is then represented by an Async Context Manager
        """
        if self._connection is None:
            raise RuntimeError("Cannot begin a transaction unless the session is open")
        return Transaction(self._connection, self._dbname)
