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

"""A limited asyncio wrapper for various cypher drivers

This is not intended to be a full driver wrapper, but just to implement the things
we immediately need in a relatively simple fashion, replicating the interface of the wrapped
library where possible.
"""

from .interface.driver import Driver
from .interface.session import Session
from .interface.transaction import Transaction
from .interface.result import Result
from .interface.relationship import Relationship
from .interface.node import Node
from .interface.exceptions import QueryFailed
from .empty import EmptyResult
from .config import Config

try:
    from . import aioneo4j  # noqa: F401
except ImportError:
    pass


try:
    from . import aioagensgraph  # noqa: F401
except ImportError:
    pass


__all__ = [
    'Driver',
    'Session',
    'Transaction',
    'Result',
    'Relationship',
    'Node',
    'EmptyResult',
    'QueryFailed',
    'Config'
]
