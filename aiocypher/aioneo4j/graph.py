# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from ..interface.graph import Graph as AbstractGraph

from typing import TypeVar, Callable, Awaitable, Set

import neo4j


R = TypeVar('R')


class Graph (AbstractGraph[neo4j.graph.Graph]):
    """A conceptual wrapper for a neo4j query which will return a neo4j.graph.Graph object.

    To execute the query and return the underlying object await this object. But the
    returned neo4j.graph.Graph is unlikely to be very useful outside of the context managers
    in which it was created.

    A better way to use this object is to use the 'nodes' coroutine property.
    """
    def __init__(
        self,
        execute: Callable[[Callable[[neo4j.Transaction], neo4j.graph.Graph]], Awaitable[neo4j.graph.Graph]],
        func: Callable[[neo4j.Transaction], neo4j.graph.Graph]
    ):
        self._func = func
        self._execute = execute

    def __await__(self):
        return self._execute(self._func).__await__()

    @property
    async def nodes(self) -> Set[neo4j.graph.Node]:
        """This property is a Coroutine, which is weird, but better matches the neo4j interface.

        When awaited this property will execute the query and return you a Set[neo4j.graph.Node]
        containing all of the nodes which the query matched.
        """
        return await self._execute(lambda tx: set(self._func(tx).nodes))

    @property
    async def relationships(self) -> Set[neo4j.graph.Relationship]:
        """This property is a Coroutine, which is weird, but better matches the neo4j interface.

        When awaited this property will execute the query and return you a Set[neo4j.graph.Relationship]
        containing all of the relationships which the query matched.
        """
        return await self._execute(lambda tx: set(self._func(tx).relationships))
