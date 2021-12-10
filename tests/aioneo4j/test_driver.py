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

from .. import HAS_NEO4J
from .fixtures import clean_session


@unittest.skipUnless(HAS_NEO4J, "Don't test aioneo4j unless neo4j is installed")
class TestDriver(unittest.IsolatedAsyncioTestCase):
    @clean_session
    async def test_basic_query(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example'})")

        async with session.begin_transaction() as tx:
            result = await tx.run("MATCH(n:TestNode) RETURN n.name")
            record = result.single()

        self.assertEqual("example", record.value())

    @clean_session
    async def test_single(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example'})")

        async with session.begin_transaction() as tx:
            record = await tx.run("MATCH(n:TestNode) RETURN n.name").single()

        self.assertEqual("example", record.value())

    @clean_session
    async def test_single_value(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example'})")

        async with session.begin_transaction() as tx:
            name = await tx.run("MATCH(n:TestNode) RETURN n.name").single().value()

        self.assertEqual("example", name)

    @clean_session
    async def test_single_data(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")

        async with session.begin_transaction() as tx:
            n = await tx.run("MATCH(n:TestNode) RETURN n").single().data()

        self.assertEqual(n, {
            'n': {
                'name': 'example',
                'potato': 'desirée'
            }
        })

    @clean_session
    async def test_result_data__one_record(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")

        async with session.begin_transaction() as tx:
            n = await tx.run("MATCH(n:TestNode) RETURN n").data()

        self.assertEqual(n, [{
            'n': {
                'name': 'example',
                'potato': 'desirée'
            }
        }])

    @clean_session
    async def test_result_data__two_records(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")
            await tx.run("CREATE(n:TestNode{name:'模範', potato:'じゃが芋'})")

        async with session.begin_transaction() as tx:
            n = await tx.run("MATCH(n:TestNode) RETURN n").data()

        self.assertCountEqual(n, [
            {
                'n': {
                    'name': 'example',
                    'potato': 'desirée'
                }
            },
            {
                'n': {
                    'name': '模範',
                    'potato': 'じゃが芋'
                }
            }
        ])

    @clean_session
    async def test_result_data__relationship(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")
            await tx.run("CREATE(n:TestNode{name:'模範', potato:'じゃが芋'})")
            await tx.run("""\
MATCH(a:TestNode{name:'example'})
MATCH(b:TestNode{name:'模範'})
CREATE (a)-[:Translation {lang:'ja'}]->(b)""")

        async with session.begin_transaction() as tx:
            data = await tx.run("MATCH (a:TestNode)-[r:Translation]-(b:TestNode) RETURN a,r,b").data()

        # It's a weird thing that this doesn't return you the properties of the relationship, but
        # that's down to the underlying synchronous library's behaviour
        self.assertCountEqual(data, [
            {
                'a': {'name': 'example', 'potato': 'desirée'},
                'r': ({'name': 'example', 'potato': 'desirée'}, 'Translation', {'name': '模範', 'potato': 'じゃが芋'}),
                'b': {'name': '模範', 'potato': 'じゃが芋'}
            },
            {
                'b': {'name': 'example', 'potato': 'desirée'},
                'r': ({'name': 'example', 'potato': 'desirée'}, 'Translation', {'name': '模範', 'potato': 'じゃが芋'}),
                'a': {'name': '模範', 'potato': 'じゃが芋'}
            }
        ])

    @clean_session
    async def test_result_data__two_values(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")
            await tx.run("CREATE(n:TestNode{name:'模範', potato:'じゃが芋'})")

        async with session.begin_transaction() as tx:
            n = await tx.run("MATCH(n:TestNode) RETURN n.name AS name, n.potato AS potato").data()

        self.assertCountEqual(n, [
            {
                'name': 'example',
                'potato': 'desirée'
            },
            {
                'name': '模範',
                'potato': 'じゃが芋'
            }
        ])

    @clean_session
    async def test_graph_nodes(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")
            await tx.run("CREATE(n:TestNode{name:'模範', potato:'じゃが芋'})")
            await tx.run("""\
MATCH(a:TestNode{name:'example'})
MATCH(b:TestNode{name:'模範'})
CREATE (a)-[:Translation {lang:'ja'}]->(b)""")

        async with session.begin_transaction() as tx:
            nodes = await tx.run("MATCH (a:TestNode)-[r:Translation]-(b:TestNode) RETURN a,r,b").graph().nodes

        self.assertEqual(len(nodes), 2)
        self.assertCountEqual(
            [n.labels for n in nodes],
            [{'TestNode'}, {'TestNode'}]
        )
        self.assertCountEqual(
            [n['name'] for n in nodes],
            ['example', '模範']
        )
        self.assertCountEqual(
            [n['potato'] for n in nodes],
            ['desirée', 'じゃが芋']
        )

    @clean_session
    async def test_graph_relationships(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")
            await tx.run("CREATE(n:TestNode{name:'模範', potato:'じゃが芋'})")
            await tx.run("""\
MATCH(a:TestNode{name:'example'})
MATCH(b:TestNode{name:'模範'})
CREATE (a)-[:Translation {lang:'ja'}]->(b)""")

        async with session.begin_transaction() as tx:
            rels = await tx.run("MATCH (a:TestNode)-[r:Translation]-(b:TestNode) RETURN a,r,b").graph().relationships

        self.assertEqual(len(rels), 1)
        rel = next(iter(rels))
        self.assertEqual(rel.type, 'Translation')
        self.assertEqual(rel['lang'], 'ja')
        self.assertEqual(rel.start_node.labels, {'TestNode'})
        self.assertEqual(rel.start_node['name'], 'example')
        self.assertEqual(rel.start_node['potato'], 'desirée')
        self.assertEqual(rel.end_node.labels, {'TestNode'})
        self.assertEqual(rel.end_node['name'], '模範')
        self.assertEqual(rel.end_node['potato'], 'じゃが芋')

    @clean_session
    async def test_graph_nodes_and_relationships(self, session):
        async with session.begin_transaction() as tx:
            await tx.run("CREATE(n:TestNode{name:'example', potato:'desirée'})")
            await tx.run("CREATE(n:TestNode{name:'模範', potato:'じゃが芋'})")
            await tx.run("""\
MATCH(a:TestNode{name:'example'})
MATCH(b:TestNode{name:'模範'})
CREATE (a)-[:Translation {lang:'ja'}]->(b)""")

        async with session.begin_transaction() as tx:
            graph = tx.run("MATCH (a:TestNode)-[r:Translation]-(b:TestNode) RETURN a,r,b").graph()
            nodes = await graph.nodes
            rels = await graph.relationships

        self.assertEqual(len(nodes), 2)
        self.assertCountEqual(
            [n.labels for n in nodes],
            [{'TestNode'}, {'TestNode'}]
        )
        self.assertCountEqual(
            [n['name'] for n in nodes],
            ['example', '模範']
        )
        self.assertCountEqual(
            [n['potato'] for n in nodes],
            ['desirée', 'じゃが芋']
        )

        self.assertEqual(len(rels), 1)
        rel = next(iter(rels))
        self.assertEqual(rel.type, 'Translation')
        self.assertEqual(rel['lang'], 'ja')
        self.assertEqual(rel.start_node.labels, {'TestNode'})
        self.assertEqual(rel.start_node['name'], 'example')
        self.assertEqual(rel.start_node['potato'], 'desirée')
        self.assertEqual(rel.end_node.labels, {'TestNode'})
        self.assertEqual(rel.end_node['name'], '模範')
        self.assertEqual(rel.end_node['potato'], 'じゃが芋')
