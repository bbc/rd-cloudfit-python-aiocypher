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
