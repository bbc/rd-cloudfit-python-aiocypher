# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

__all__ = ["HAS_AGENSGRAPH", "HAS_NEO4J"]


try:
    import agensgraph  # noqa: F401
except ImportError:
    HAS_AGENSGRAPH = False
else:
    HAS_AGENSGRAPH = True


try:
    import neo4j  # noqa: F401
except ImportError:
    HAS_NEO4J = False
else:
    HAS_NEO4J = True
