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

from async_generator import asynccontextmanager
import os
import asyncio
from functools import wraps


from aiocypher.aioneo4j.driver import Driver
from aiocypher import Config


def clean_session(f=None):
    """This helper gives you a Session on the database, but does some extra work before and after to
    make sure everything is deleted.

    It can be used as an async context manager or a decorator
    """
    @asynccontextmanager
    async def __clean_session():
        HOST = os.environ.get('NEO4J_HOST', 'localhost')
        PORT = os.environ.get('NEO4J_PORT', 17687)
        USER = 'neo4j'
        PASSWORD = 'test'

        DB = "neo4j"

        config = Config(
            address=f'bolt://{HOST}:{PORT}',
            username=USER,
            password=PASSWORD
        )
        async with Driver(config) as driver:
            async with driver.session(database=DB) as session:
                # Delete content in the database
                async with session.begin_transaction() as tx:
                    await tx.run("MATCH (n)\nDETACH DELETE n")

                # Delete any schemata in the database
                async with session.begin_transaction() as tx:
                    await tx.run("CALL apoc.schema.assert({}, {})")

            async with driver.session(database=DB) as session:
                yield session

            async with driver.session(database=DB) as session:
                # Delete content in the database
                async with session.begin_transaction() as tx:
                    await tx.run("MATCH (n)\nDETACH DELETE n")

    if f is None:
        return __clean_session()
    else:
        @wraps(f)
        async def __inner(*args, **kwargs):
            async with __clean_session() as session:
                r = f(*args, session, **kwargs)
                if asyncio.iscoroutinefunction(f):
                    return await r
                else:
                    return r

        return __inner
