# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

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
