# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.transaction import Transaction as AbstractTransaction

from typing import Optional

import aiopg
from async_exit_stack import AsyncExitStack

from .result import Result


class Transaction (AbstractTransaction):
    """A class which encapsulates a Transaction. Should never be created directly,
    but always via an Session object.

    Should always be used as an Async Context Manager. Using any of its methods outside of
    the context may lead to undefined behaviour.
    """
    def __init__(self, connection: aiopg.Connection, database: str):
        self._exit_stack = AsyncExitStack()
        self._connection = connection
        self._dbname = database
        self._cursor: Optional[aiopg.Cursor] = None

    def __await__(self):
        async def __inner():
            if self._cursor is None:
                self._cursor = await self._exit_stack.enter_async_context(self._connection.cursor())
                await self._cursor.execute(f"CREATE GRAPH IF NOT EXISTS {self._dbname}")
                await self._cursor.execute(f"SET graph_path = {self._dbname}")
                await self._cursor.execute("BEGIN")
                await self._cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
            return self._cursor
        return __inner().__await__()

    async def __aenter__(self) -> "Transaction":
        await self._exit_stack.__aenter__()
        await self
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        if self._cursor is not None:
            if exc_v is None:
                try:
                    await self._cursor.execute("COMMIT")
                except Exception:
                    pass
            else:
                try:
                    await self._cursor.execute("ROLLBACK")
                except Exception:
                    pass
        return await self._exit_stack.__aexit__(exc_t, exc_v, exc_tb)

    def run(self, *args, **kwargs) -> Result:
        """This is the main routine for this class.

        :returns: a Result object
        """
        return Result(self._cursor, *args, **kwargs)
