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

from ..interface.node import Node as AbstractNode

from typing import Dict, Union


class Node (AbstractNode, Dict[str, Union[str, int]]):
    def __init__(self, data: Dict[str, Union[str, int]]):
        if 'vid' in data:
            self._hash = hash(data['vid'])
        else:
            self._hash = hash(str(data))
        super().__init__({key: value for (key, value) in data.items()})

    def __hash__(self):
        return self._hash
