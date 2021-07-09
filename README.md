# aiocypher

A partial Python asyncio wrapper for various [Cypher Query Language](https://neo4j.com/developer/cypher/) drivers

This is not intended to be a full async driver, but a warpper implementation using
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

loop = asyncio.get_event_loop()
loop.run_until_complete(basic_query(driver))
```

## Developing with this project
To run the unit tests on this project you need a running database for it to test against - fortunately you can use
Docker to start one using the `docker-compose.yml` file provided in this repository.

To run the unit tests, try something like:
```
docker-compose up -d agensgraph neo4j
export NEO4J_PORT=$(docker-compose port neo4j 7687 | cut -d':' -f2)
export AGENSGRAPH_PORT=$(docker-compose port agensgraph 5432 | cut -d':' -f2)
tox
```

This will start a local instance of Neo4j Agensgraph on random ports, set those ports in environment variables and then
run the tests. Run `docker-compose down` to get rid of the database instances again.

Note that `docker-compose up -d` on it's own isn't likely to work, because it requires a containerised build of the
unit tests which depends on some internal tooling - see the next section.

You can also run the linter (`tox -e lint`) or typechecker (`tox -e mypy`).

## Developing with this project - using internal tools
This repository also contains various tooling used by the [Cloud-fit Production team](https://www.bbc.co.uk/rd/projects/cloud-fit-production)
internally to build software using Docker and Jenkins - if you have access to this tooling the first thing which needs
to be done before using this project is to run:

```bash
./initialise_common_tooling.sh
```
To which an optional parameter can be passed, which will be the branch name of
a branch in the commontooling repo to make use of for tooling. The default is
master. This will pull in a bunch of common components used by makefiles,
docker, jenkinsfiles, etc.

A Makefile is provided at the top-level of the repository to run common tasks. Run make in the top directory of this
repository to see what actions are available.

More information on how cloud-fit production services are built, tested, and
deployed is contained on our confluence pages: <https://confluence.dev.bbc.co.uk/display/CloudFit/Developing+and+Deploying+with+Containers>

## Questions?
Any questions, please contact one of the R&D Cloud-Fit Production team, or file an Issue on the repo.
