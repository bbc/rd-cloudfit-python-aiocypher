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


from abc import ABCMeta as ABCMeta

from typing import Type, List, Tuple, Callable, Optional

from ..config import Config

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
