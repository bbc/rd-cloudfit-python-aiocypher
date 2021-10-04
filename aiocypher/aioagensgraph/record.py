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

from ..interface.record import Record as AbstractRecord

from typing import Optional, Awaitable, Dict, Union

from .node import Node


class Record (AbstractRecord[Optional[Dict[str, str]]]):
    """A conceptual wrapper for a query which will return a single record.

    To execute the query and return the underlying object await this object or the value() coroutine.

    Both produce slightly different flavours of dictionary representing the data.
    """
    def __init__(
        self,
        coroutine: Awaitable[Optional[Dict[str, str]]]
    ):
        self._coroutine: Optional[Awaitable[Optional[Dict[str, str]]]] = coroutine
        self._result: Optional[Dict[str, str]] = None

    def __await__(self):
        async def __inner():
            if self._result is None and self._coroutine is not None:
                c = self._coroutine
                self._coroutine = None
                self._result = await c

            return self._result
        return __inner().__await__()

    async def value(self) -> Optional[Node]:
        """When awaited this coroutine executes the query and returns a Node object
        which is contained inside this Record.

        This object is likely to be useful and what you actually want.

        :returns: A Node
        """
        result = await self
        if result is None:
            return None
        else:
            return Node(result)

    async def data(self) -> Optional[Dict[str, Dict[str, Union[str, int]]]]:
        """Deserialises the data in this result as dictionary and returns it.
        """
        result = await self

        if result is None or 'label' not in result:
            return None

        label = result['label']

        return {label: Node(result)}
