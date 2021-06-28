# Copyright 2020 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

import asyncio
import asynctest as unittest
import os

import psycopg2

from ..retry_on_exception import retry_on_exception
from .. import HAS_AGENSGRAPH

if HAS_AGENSGRAPH:
    from aiocypher.aioagensgraph.driver import Driver
    from aiocypher import Config
    import aiopg

    HOST = os.environ.get('AGENSGRAPH_HOST', 'localhost')
    PORT = os.environ.get('AGENSGRAPH_PORT', 15432)
    USER = 'neo4j'
    PASSWORD = 'test'

    DB = "testdb"

    def make_driver():
        config = Config(
            address=f'postgresql://{HOST}:{PORT}',
            username=USER,
            password=PASSWORD)
        return Driver(config)

    @retry_on_exception(exception=psycopg2.OperationalError)
    async def _check_db_connection():
        async with aiopg.connect(f"host={HOST} user={USER} password={PASSWORD} port={PORT}"):
            # Database is connected, tests can continue
            pass

    @unittest.skipUnless(HAS_AGENSGRAPH, "Don't test aioagensgraph unless agensgraph is installed")
    class TestDriver(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            # asynctest doesn't start a loop here, so instead we do it manually
            asyncio.get_event_loop().run_until_complete(_check_db_connection())

        async def setUp(self):
            async with aiopg.connect(f"host={HOST} user={USER} password={PASSWORD} port={PORT}") as conn:
                async with conn.cursor() as cur:
                    await cur.execute(f"DROP GRAPH IF EXISTS {DB} CASCADE")
                    await cur.execute(f"CREATE GRAPH IF NOT EXISTS {DB}")

        async def tearDown(self):
            async with aiopg.connect(f"host={HOST} user={USER} password={PASSWORD} port={PORT}") as conn:
                async with conn.cursor() as cur:
                    await cur.execute(f"DROP GRAPH IF EXISTS {DB} CASCADE")

        async def test_driver_manual_access_to_underlying_connection_pool(self):
            async with make_driver() as UUT:
                pool = await UUT
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(f"SET graph_path = {DB}")
                        await cur.execute("CREATE (:v {name: 'AgensGraph'})")
                        await cur.execute("MATCH (n) RETURN n")
                        v = (await cur.fetchone())[0]
            self.assertEqual(v, {'type': 'vertex', 'label': 'v', 'vid': '3.1', 'name': 'AgensGraph'})

        async def test_driver_session_manual_access_to_underlying_connection(self):
            async with make_driver() as UUT:
                async with UUT.session(database=DB) as session:
                    conn = await session

                    async with conn.cursor() as cur:
                        await cur.execute(f"SET graph_path = {DB}")
                        await cur.execute("CREATE (:v {name: 'AgensGraph'})")
                        await cur.execute("MATCH (n) RETURN n")
                        v = (await cur.fetchone())[0]
            self.assertEqual(v, {'type': 'vertex', 'label': 'v', 'vid': '3.1', 'name': 'AgensGraph'})

        async def test_driver_session_transaction_manual_access_to_underlying_cursor(self):
            async with make_driver() as UUT:
                async with UUT.session(database=DB) as session:
                    async with session.begin_transaction() as tx:
                        cur = await tx

                        await cur.execute("CREATE (:v {name: 'AgensGraph'})")
                        await cur.execute("MATCH (n) RETURN n")
                        v = (await cur.fetchone())[0]
            self.assertEqual(v, {'type': 'vertex', 'label': 'v', 'vid': '3.1', 'name': 'AgensGraph'})

        async def test_driver_session_transaction_run_result_manual_access_to_underlying_cursor(self):
            async with make_driver() as UUT:
                async with UUT.session(database=DB) as session:
                    async with session.begin_transaction() as tx:
                        await tx.run("CREATE (:v {name: 'AgensGraph'})")
                        cur = await tx.run("MATCH (n) RETURN n")
                        v = (await cur.fetchone())[0]
            self.assertEqual(v, {'type': 'vertex', 'label': 'v', 'vid': '3.1', 'name': 'AgensGraph'})

        async def test_driver_session_transaction_run_result_single_manual_access_to_underlying_data(self):
            async with make_driver() as UUT:
                async with UUT.session(database=DB) as session:
                    async with session.begin_transaction() as tx:
                        await tx.run("CREATE (:v {name: 'AgensGraph'})")
                        v = await tx.run("MATCH (n) RETURN n").single()
            self.assertEqual(v, {'type': 'vertex', 'label': 'v', 'vid': '3.1', 'name': 'AgensGraph'})

        async def test_driver_session_transaction_run_result_single_value(self):
            async with make_driver() as UUT:
                async with UUT.session(database=DB) as session:
                    async with session.begin_transaction() as tx:
                        await tx.run("CREATE (:v {name: 'AgensGraph'})")
                        node = await tx.run("MATCH (n) RETURN n").single().value()
            self.assertIn('name', node)
            self.assertEqual('AgensGraph', node['name'])
