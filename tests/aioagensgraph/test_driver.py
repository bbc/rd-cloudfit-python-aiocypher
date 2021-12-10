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

import unittest
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
    class TestDriver(unittest.IsolatedAsyncioTestCase):
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
