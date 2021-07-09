# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from abc import ABCMeta

from typing import Mapping, Union, Set, List


class Node (Mapping[str, Union[str, int, List[Union[str, int]]]], metaclass=ABCMeta):
    labels: Set[str]
