# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from abc import ABCMeta

from typing import Mapping, Union

from .node import Node


class Relationship (Mapping[str, Union[str, int]], metaclass=ABCMeta):
    type: str
    start_node: Node
    end_node: Node
