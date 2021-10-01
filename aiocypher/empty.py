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
