# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.transaction import Transaction as AbstractTransaction

from typing import Optional, TypeVar, Callable, Awaitable

import neo4j

from .result import Result

R = TypeVar('R')


class Transaction (AbstractTransaction):
    """A class which encapsulates a neo4j.Transaction object. Should never be created directly,
    but always via an aioneo4j.Session object.

    Should always be used as an Async Context Manager. Using any of its methods outside of
    the context may lead to undefined behaviour.
    """
    def __init__(self, session_execute: Callable[[Callable[[neo4j.Session], R]], Awaitable[R]]):
        self._session_execute = session_execute
        self._sync_transaction: Optional[neo4j.Transaction] = None

    async def __aenter__(self) -> "Transaction":
        self._sync_transaction = await self._session_execute(lambda session: session.begin_transaction().__enter__())
        return self

    async def __aexit__(self, *args):
        if self._sync_transaction is not None:
            return await self._session_execute(lambda session: self._sync_transaction.__exit__(*args))
        else:
            return False

    async def _execute(self, f: Callable[[neo4j.Transaction], R]) -> R:
        """Although not strictly part of the public interface this coroutine
        may occasionally be useful when doing things not yet supported by
        the interface methods.

        When awaited it executes a provided Synchronous callable on the IO thread and
        returns the return value. If the callable raises an exception then this is
        propogated out of this await.

        :param f: A callable which takes a neo4j.Transaction object as a parameter.
        :returns: The return value of f
        :raises: Any exception raised by f
        """
        return await self._session_execute(lambda session: f(self._sync_transaction))

    def run(self, *args, **kwargs) -> Result:
        """This is the main routine for this class.

        It has an interface identical to neo4j.Transaction.run.

        The actual query will not be executed until such a time as the return value (or some derivative thereof)
        is awaited.

        :returns: an aioneo4j.Result object, which is a subclass of Awaitable[neo4j.Result]
        """
        return Result(self._execute, lambda tx: tx.run(*args, **kwargs))
