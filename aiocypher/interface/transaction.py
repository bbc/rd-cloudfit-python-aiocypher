# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

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
