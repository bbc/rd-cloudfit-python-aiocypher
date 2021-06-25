# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from abc import ABCMeta, abstractproperty

from typing import TypeVar, Awaitable, Generic, Collection

from .relationship import Relationship
from .node import Node


R = TypeVar('R')


class Graph (Generic[R], Awaitable[R], metaclass=ABCMeta):
    """A conceptual wrapper for a query which will return a graph of nodes.

    To execute the query and return the underlying object await this object.

    A better way to use this object is to use the 'nodes' or 'relationships' coroutine properties.
    """
    @abstractproperty
    async def nodes(self) -> Collection[Node]:
        """This property is a Coroutine, which is weird, but better matches the neo4j interface.

        When awaited this property will execute the query and return you a Set[neo4j.graph.Node]
        containing all of the nodes which the query matched.
        """
        ...

    @abstractproperty
    async def relationships(self) -> Collection[Relationship]:
        """This property is a Coroutine, which is weird, but better matches the neo4j interface.

        When awaited this property will execute the query and return you a Set[neo4j.graph.Relationship]
        containing all of the relationships which the query matched.
        """
        ...
