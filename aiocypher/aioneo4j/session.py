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

import asyncio
import time
from typing import Optional, TypeVar, Callable, AsyncContextManager, Tuple, Any, cast
from queue import Empty, Full

import neo4j
import janus
from async_generator import asynccontextmanager

from .transaction import Transaction


R = TypeVar('R')


class Session (AbstractSession):
    """This object encapsulates a neo4j.Session object. It should not be initialised directly, but
    created via an aioneo4j.Driver object.

    It should always be used as an Async Context Manager, and using its methods outside of its
    context may lead to undefined behaviour.


    Each Session object maintains its own connection thread for performing IO. A Session object is
    the only supported way to interact with the neo4j database.
    """
    def __init__(self, sync_driver: 'asyncio.Future[neo4j.Driver]', **kwargs):
        self.sync_driver = sync_driver
        self.__thread: Optional['asyncio.Future[None]'] = None
        self.__die = False

        self.__kwargs = kwargs

        if "database" in self.__kwargs and self.__kwargs['database'] is None:
            self.__kwargs['database'] = neo4j.DEFAULT_DATABASE

        self._command_queue: janus.Queue[Callable[[neo4j.Transaction], Any]] = janus.Queue(maxsize=1)
        self._response_queue: janus.Queue[Tuple[Any, Optional[BaseException]]] = janus.Queue(maxsize=1)

        self._transaction: Optional[Transaction] = None

    async def __aenter__(self) -> 'Session':
        self.__die = False
        loop = asyncio.get_running_loop()
        self.__thread = cast(
            'asyncio.Future[None]',
            loop.run_in_executor(None, self._thread_main, await self.sync_driver))
        return self

    async def __aexit__(self, *args) -> bool:
        self.__die = True
        if self.__thread is not None:
            await self.__thread
        return False

    def _thread_main(self, sync_driver: neo4j.Driver) -> None:
        with sync_driver.session(**self.__kwargs) as session:
            while not self.__die:
                try:
                    cmd = self._command_queue.sync_q.get(block=False)
                except Empty:
                    time.sleep(0.01)
                    continue

                try:
                    (r, e) = (cmd(session), None)
                except BaseException as ex:
                    (r, e) = (None, ex)

                while not self.__die:
                    try:
                        self._response_queue.sync_q.put((r, e), block=False)
                    except Full:
                        time.sleep(0.01)
                        continue
                    else:
                        break

    async def _execute(self, f: Callable[[neo4j.Session], R]) -> R:
        """Although not strictly part of the public interface this coroutine
        may occasionally be useful when doing things not yet supported by
        the interface methods.

        When awaited it executes a provided Synchronous callable on the IO thread and
        returns the return value. If the callable raises an exception then this is
        propogated out of this await.

        :param f: A callable which takes a neo4j.Session object as a parameter.
        :returns: The return value of f
        :raises: Any exception raised by f
        """
        await self._command_queue.async_q.put(f)
        (r, e) = await self._response_queue.async_q.get()
        if e is not None:
            raise e
        return r

    def begin_transaction(self) -> AsyncContextManager[Transaction]:
        """This is the main method for interacting with the Session. It
        creates a new Transaction which is then represented by an Async Context Manager
        yielding an aioneo4j.Transaction object.
        """
        @asynccontextmanager
        async def __inner():
            if self._transaction is not None:
                raise neo4j.exceptions.TransactionError()

            self._transaction = Transaction(self._execute)

            async with self._transaction:
                yield self._transaction

            self._transaction = None

        return __inner()
