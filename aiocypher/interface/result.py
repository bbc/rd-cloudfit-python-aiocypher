# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from abc import ABCMeta, abstractmethod

from typing import TypeVar, Awaitable, List, Dict, Any, Generic

from .record import Record
from .graph import Graph


R = TypeVar('R')


class Result (Generic[R], Awaitable[R], metaclass=ABCMeta):
    """A conceptual wrapper for a query which will return a result object of some kind.

    To execute the query and return the underlying object await this object.

    It also has other methods which return awaitable objects.
    """

    @abstractmethod
    def single(self) -> Record:
        """Returns a Record object

        Useful if the wrapped query is expected to return a single result.
        """
        ...

    @abstractmethod
    async def data(self) -> List[Dict[str, Any]]:
        """Deserialises the data in this result as a list of dictionaries and returns it.
        """
        ...

    @abstractmethod
    def graph(self) -> Graph:
        """Returns an Graph object which

        Useful if the wrapped query is expected to return multiple results.
        """
        ...
