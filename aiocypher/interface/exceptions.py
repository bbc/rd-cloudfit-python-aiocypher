# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from typing import Dict, Union


class QueryFailed (Exception):
    def __init__(self, query: str, params: Dict[str, Union[str, int]]):
        super().__init__(f"Query failed: << {query} >> with parameters {params!r}")
