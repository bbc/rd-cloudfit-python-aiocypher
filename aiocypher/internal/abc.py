# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.


from abc import ABCMeta as ABCMeta

from typing import Type, List, Tuple, Callable, Optional

from ...config import Config

__all__ = [
    "AIOCypherABCMeta"
]


class AIOCypherABCMeta (ABCMeta):

    __concrete_lookup__: List[Tuple[Callable[[Config], bool], Type]] = []

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        return cls

    def register_concrete(cls, address_parser: Callable[[Config], bool]):
        def __decorator(subclass: Type) -> Type:
            subclass = cls.register(subclass)
            cls.__concrete_lookup__.append((address_parser, subclass))

            return subclass
        return __decorator

    def __call__(cls, *args, **kwargs) -> object:
        if 'config' in kwargs:
            config = kwargs.pop('address')
        elif len(args) > 0:
            config = args[0]
            args = args[1:]
        else:
            raise TypeError("Missing 1 required positional argument (config)")

        concrete_subclass: Optional[Type] = None
        for (address_parser, subclass) in cls.__concrete_lookup__:
            if address_parser(config):
                concrete_subclass = subclass

        if concrete_subclass is None:
            raise ValueError(f"Could not find any registered concrete subclass of {cls!r} for address "
                             f"{config.address}")

        return ABCMeta.__call__(concrete_subclass, config, *args, **kwargs)
