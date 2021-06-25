# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.graph import Graph as AbstractGraph

from typing import Set, Any, Awaitable, List, Dict, Optional

from .node import Node

Relationship = Any


class Graph (AbstractGraph[Optional[List[Dict[str, str]]]]):
    """A conceptual wrapper for a query which will return a Graph.
    """
    def __init__(
        self,
        coroutine: Awaitable[List[Dict[str, str]]]
    ):
        self._coroutine: Optional[Awaitable[List[Dict[str, str]]]] = coroutine
        self._result: Optional[List[Dict[str, str]]] = None

    def __await__(self):
        async def __inner():
            if self._result is None and self._coroutine is not None:
                c = self._coroutine
                self._coroutine = None
                self._result = await c
            return self._result
        return __inner().__await__()

    @property
    async def nodes(self) -> Set[Node]:
        """This property is a Coroutine, which is weird, but better matches the neo4j interface.
        """
        data = await self
        return {Node(n) for (n,) in data if 'vid' in n}

    @property
    async def relationships(self) -> Set[Relationship]:
        """This property is a Coroutine, which is weird, but better matches the neo4j interface.
        """
        ...
