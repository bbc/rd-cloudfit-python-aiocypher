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

from typing import Optional, TypeVar, Awaitable, Dict, Union, Generic

from .node import Node

R = TypeVar('R')


class Record (Generic[R], Awaitable[R], metaclass=ABCMeta):
    """A conceptual wrapper for a query which will return a single record object.

    To execute the query and return the underlying object await this object.

    A better way to use this object is to use the 'data()' coroutine.
    """

    @abstractmethod
    async def data(self) -> Optional[Dict[str, Dict[str, Union[str, int]]]]:
        """Deserialises the data in this result as dictionary and returns it.
        """
        ...

    @abstractmethod
    async def value(self) -> Optional[Node]:
        """Return the Node object represented by the query"""
        ...
