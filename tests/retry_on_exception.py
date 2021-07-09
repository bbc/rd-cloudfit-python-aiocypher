# Copyright 2021 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from typing import TypeVar, Optional, Callable
import logging
import functools
import time


T = TypeVar('T')


def retry_on_exception(
    exception=Exception,
    timeout=20.0,
    logger: Optional[logging.Logger] = None,
    msg="Retrying ..."
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """This method returns a decorator which causes the decorated function to
    retry repeatedly for a specified timeout if an exception is raised. If the
    timeout is exceded then any further exception is raised as normal.
    :param exception: An exception class to restrict to, any other exceptions will be raised as normal
    :param timeout: the timeout in seconds
    :param logger: a logger to use to log messages
    :param msg: A message to log each time an exception is suppressed and the call is retried
    :returns: A decorator
    """
    def __decorator(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        async def __inner(*args, **kwargs) -> T:
            start = time.clock_gettime(time.CLOCK_MONOTONIC)
            while True:
                try:
                    return await f(*args, **kwargs)
                except exception as e:
                    if time.clock_gettime(time.CLOCK_MONOTONIC) - start > timeout:
                        raise Exception("Timeout exceeded whilst retrying") from e
                    else:
                        if logger is not None:
                            logger.warning(msg)
                        time.sleep(1)
                else:
                    break
        return __inner
    return __decorator
