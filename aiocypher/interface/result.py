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

from abc import ABCMeta, abstractmethod

from typing import TypeVar, Awaitable, List, Dict, Any, Generic

from .record import Record
from .graph import Graph


R = TypeVar('R')


class Result (Generic[R], Awaitable[R], metaclass=ABCMeta):
    """A conceptual wrapper for a query which will return a result object of some kind.

    To execute the query and return the underlying object await this object.

    It also has other methods which return awaitable objects.
    """

    @abstractmethod
    def single(self) -> Record:
        """Returns a Record object

        Useful if the wrapped query is expected to return a single result.
        """
        ...

    @abstractmethod
    async def data(self) -> List[Dict[str, Any]]:
        """Deserialises the data in this result as a list of dictionaries and returns it.
        """
        ...

    @abstractmethod
    def graph(self) -> Graph:
        """Returns an Graph object which

        Useful if the wrapped query is expected to return multiple results.
        """
        ...
