# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

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
