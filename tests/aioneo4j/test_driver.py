# Copyright 2021 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.
from async_generator import async_generator, yield_, asynccontextmanager
import asynctest as unittest
import os

from .. import HAS_NEO4J

from aiocypher.aioneo4j.driver import Driver
from aiocypher import Config

HOST = os.environ.get('NEO4J_HOST', 'localhost')
PORT = os.environ.get('NEO4J_PORT', 17687)
USER = 'neo4j'
PASSWORD = 'test'

DB = "neo4j"


def make_driver():
    config = Config(
        address=f'bolt://{HOST}:{PORT}',
        username=USER,
        password=PASSWORD
    )
    return Driver(config)


@unittest.skipUnless(HAS_NEO4J, "Don't test aioneo4j unless neo4j is installed")
class TestDriver(unittest.TestCase):
    @asynccontextmanager
    @async_generator
    async def _session_helper(self):
        async with self.driver as driver:
            async with driver.session(database=DB) as session:
                await yield_(session)

    async def setUp(self):
        self.driver = make_driver()
        async with self._session_helper() as session:
            async with session.begin_transaction() as tx:
                await tx.run("MATCH (n)\nDETACH DELETE n")

            async with session.begin_transaction() as tx:
                await tx.run("CALL apoc.schema.assert({}, {})")

    async def tearDown(self):
        async with self._session_helper() as session:
            async with session.begin_transaction() as tx:
                await tx.run("MATCH (n)\nDETACH DELETE n")

    async def test_basic_query(self):
        async with self._session_helper() as session:
            async with session.begin_transaction() as tx:
                await tx.run("CREATE(n:TestNode{name:'example'})")

            async with session.begin_transaction() as tx:
                result = await tx.run("MATCH(n:TestNode) RETURN n.name")
                record = result.single()
                self.assertEqual("example", record.value())
