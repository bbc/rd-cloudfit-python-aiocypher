# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.result import Result as AbstractResult
from ..interface.exceptions import QueryFailed

from typing import List, Dict, Any

import aiopg

import re

from .record import Record
from .graph import Graph


def convert_cypher_parameters_to_postgres(query: str, params: Dict[str, str]) -> str:
    q = str(query)
    for key in params:
        # Replace entries of the form $name with %(name)s
        # (Ignoring instances of $$)
        q = re.sub(r'(?<!\$)\$' + key + r'(?!\w)', r'%(' + key + ')s', q)

    return q


class Result (AbstractResult[Any]):
    """A conceptual wrapper for a query which will return a result of some sort.

    To execute the query and return the underlying object await this object. But the
    returned object is unlikely to be very useful outside of the context managers
    in which it was created.

    A better way to use this object is to use the 'data()', single()' or 'graph()' methods.
    """
    def __init__(self, cursor: aiopg.Cursor, *args, **kwargs):
        self._cursor = cursor
        self._args = args
        self._kwargs = kwargs

    def __await__(self):
        async def __inner():
            query = convert_cypher_parameters_to_postgres(self._args[0], self._kwargs)
            try:
                await self._cursor.execute(query, parameters=self._kwargs)
            except Exception as e:
                raise QueryFailed(query, self._kwargs) from e
            else:
                return self._cursor
        return __inner().__await__()

    def single(self) -> Record:
        """Returns an Record object

        Useful if the wrapped query is expected to return a single result.
        """
        async def __inner():
            await self
            result = await self._cursor.fetchone()
            return result[0] if result else None
        return Record(__inner())

    def graph(self) -> Graph:
        """Returns an Graph object

        Useful if the wrapped query is expected to return multiple results.
        """
        async def __inner():
            await self
            result = await self._cursor.fetchall()
            return result
        return Graph(__inner())

    async def data(self) -> List[Dict[str, Any]]:
        """Deserialises the data in this result as a list of dictionaries and returns it.
        """
        ...
