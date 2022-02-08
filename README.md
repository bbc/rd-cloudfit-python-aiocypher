# aiocypher

A partial Python asyncio wrapper for various [Cypher Query Language](https://neo4j.com/developer/cypher/) drivers

This is not intended to be a full async driver, but a wrapper implementation using
[run_in_executor](https://bbc.github.io/cloudfit-public-docs/asyncio/asyncio-part-5.html#executors-and-multithreading)
to allow asynchronous usage of the underlying synchronous driver, replicating the interface of the wrapped library where
possible.

## Installation & Usage
`pip3 install aiocypher`

Note the neo4j driver is installed by default, if you want to use AgensGraph,
try `pip3 install aiocypher[agensgraph]`.

### Usage Example
```python
import asyncio
from aiocypher.aioneo4j.driver import Driver
from aiocypher import Config

config = Config(
    address='bolt://localhost:17687',
    username='neo4j',
    password='test'
)
driver = Driver(config)


async def basic_query(driver: Driver):
    async with driver as driver:
        async with driver.session(database='neo4j') as session:
            async with session.begin_transaction() as tx:
                await tx.run("CREATE(n:TestNode{name:'example'})")

            async with session.begin_transaction() as tx:
                result = await tx.run("MATCH(n:TestNode) RETURN n.name")
                record = result.single()
                print(record)

asyncio.run(basic_query(driver))
```

## Developing with this project
A Makefile is provided at the top-level of the repository to run common tasks. Run make in the top directory of this
repository to see what actions are available.

## Questions?
Any questions, please contact one of the R&D Cloud-Fit Production team on <cloudfit-opensource@rd.bbc.co.uk>, or file an
Issue on the repo.
