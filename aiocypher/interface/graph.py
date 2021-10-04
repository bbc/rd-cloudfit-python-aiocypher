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
