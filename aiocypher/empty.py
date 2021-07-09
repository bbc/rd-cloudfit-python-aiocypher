# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from typing import List, Dict, Any, Set

from .interface.result import Result
from .interface.record import Record
from .interface.graph import Graph
from .interface.node import Node
from .interface.relationship import Relationship


class EmptyGraph (Graph[None]):
    async def nodes(self) -> Set[Node]:
        return set()

    async def relationships(self) -> Set[Relationship]:
        return set()

    def __await__(self):
        async def __inner():
            return None
        return __inner().__await__()


class EmptyResult(Result[None]):
    def single(self) -> Record:
        """Returns a Record object

        Useful if the wrapped query is expected to return a single result.
        """
        raise RuntimeError("This result is empty")

    async def data(self) -> List[Dict[str, Any]]:
        """Deserialises the data in this result as a list of dictionaries and returns it.
        """
        return []

    def graph(self) -> EmptyGraph:
        """Returns an Graph object which

        Useful if the wrapped query is expected to return multiple results.
        """
        return EmptyGraph()

    def __await__(self):
        async def __inner():
            return None
        return __inner().__await__()
