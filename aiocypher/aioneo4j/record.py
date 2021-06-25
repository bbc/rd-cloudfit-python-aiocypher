# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.record import Record as AbstractRecord

from typing import Optional, TypeVar, Callable, Awaitable, Dict, cast, Union

import neo4j


R = TypeVar('R')


class Record (AbstractRecord[neo4j.Record]):
    """A conceptual wrapper for a neo4j query which will return a neo4j.Record object.

    To execute the query and return the underlying object await this object. But the
    returned neo4j.Record is unlikely to be very useful outside of the context managers
    in which it was created.

    A better way to use this object is to use the 'value()' coroutine.
    """
    def __init__(
        self,
        execute: Callable[[Callable[[neo4j.Transaction], neo4j.Record]], Awaitable[neo4j.Record]],
        func: Callable[[neo4j.Transaction], neo4j.Record]
    ):
        self._func = func
        self._execute = execute

    def __await__(self):
        return self._execute(self._func).__await__()

    async def value(self) -> Optional[neo4j.graph.Node]:
        """When awaited this coroutine executes the query and returns the underlying neo4j.graph.Node object
        which is contained inside this Record.

        This object is likely to be useful and what you actually want.

        :returns: A neo4j.graph.Node
        """
        def __inner(tx) -> Optional[neo4j.graph.Node]:
            record = self._func(tx)
            if record is not None:
                return record.value()
            else:
                return None

        return await self._execute(__inner)

    async def data(self) -> Optional[Dict[str, Dict[str, Union[str, int]]]]:
        """Deserialises the data in this result as dictionary and returns it.
        """
        def __inner(tx) -> Optional[Dict[str, Union[str, int]]]:
            record = self._func(tx)
            if record is not None:
                return record.data()
            else:
                return None

        return cast(Optional[Dict[str, Dict[str, Union[str, int]]]], await self._execute(__inner))
