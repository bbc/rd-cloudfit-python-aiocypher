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

"""A limited asyncio wrapper for the agensgraph driver

This is not intended to be a full driver wrapper, but just to implement the things
we immediately need in a relatively simple fashion, replicating the interface of
aioneo4j where possible.
"""

from typing import List

__all__: List[str] = []

try:
    from .driver import Driver  # noqa: F401
except ImportError:
    pass
else:
    __all__.append('Driver')
