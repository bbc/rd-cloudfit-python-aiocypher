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

from .result import Result


class Transaction (object, metaclass=ABCMeta):
    """A class which encapsulates a Transaction. Should never be created directly,
    but always via a Session object.

    Should always be used as an Async Context Manager. Using any of its methods outside of
    the context may lead to undefined behaviour.
    """
    async def __aenter__(self) -> "Transaction":
        return self

    async def __aexit__(self, *args):
        return False

    @abstractmethod
    def run(self, *args, **kwargs) -> Result:
        """This is the main routine for this class.

        The actual query will not be executed until such a time as the return value (or some derivative thereof)
        is awaited.

        :returns: an Result object
        """
        ...
