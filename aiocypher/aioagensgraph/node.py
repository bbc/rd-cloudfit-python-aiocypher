# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

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
