# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.result import Result as AbstractResult

from typing import TypeVar, Callable, Awaitable, List, Dict, cast, Any

import neo4j

from .record import Record
from .graph import Graph


R = TypeVar('R')


class Result (AbstractResult[neo4j.Result]):
    """A conceptual wrapper for a neo4j query which will return a neo4j.Result object.

    To execute the query and return the underlying object await this object. But the
    returned neo4j.Result is unlikely to be very useful outside of the context managers
    in which it was created.

    A better way to use this object is to use the 'single()' or 'graph()' methods.
    """
    def __init__(
        self,
        execute: Callable[[Callable[[neo4j.Transaction], R]], Awaitable[R]],
        func: Callable[[neo4j.Transaction], neo4j.Result]
    ):
        self._func = func
        self._execute = execute

    def __await__(self):
        return self._execute(self._func).__await__()

    def single(self) -> Record:
        """Returns an aioneo4j.Record object, which is an Awaitable[neo4j.Record]

        Useful if the wrapped query is expected to return a single result.
        """
        return Record(self._execute, lambda tx: self._func(tx).single())

    def graph(self) -> Graph:
        """Returns an aioneo4j.graph.Graph object which is an Awaitable[neo4j.graph.Graph]

        Useful if the wrapped query is expected to return multiple results.
        """
        return Graph(self._execute, lambda tx: self._func(tx).graph())

    async def data(self) -> List[Dict[str, Any]]:
        """Deserialises the data in this result as a list of dictionaries and returns it.
        """
        return cast(List[Dict[str, Any]], await self._execute(lambda tx: self._func(tx).data()))
