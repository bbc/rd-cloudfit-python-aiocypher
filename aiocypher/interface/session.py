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
from typing import AsyncContextManager

from .transaction import Transaction


class Session (object, metaclass=ABCMeta):
    """This object encapsulates a Session object. It should not be initialised directly, but
    created via a Driver object.

    It should always be used as an Async Context Manager, and using its methods outside of its
    context may lead to undefined behaviour.

    A Session object is the only supported way to interact with the cypher database.
    """
    async def __aenter__(self) -> 'Session':
        return self

    async def __aexit__(self, *args) -> bool:
        return False

    @abstractmethod
    def begin_transaction(self) -> AsyncContextManager[Transaction]:
        """This is the main method for interacting with the Session. It
        creates a new Transaction which is then represented by an Async Context Manager
        """
        ...
