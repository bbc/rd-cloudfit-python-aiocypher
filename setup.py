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

from setuptools import setup

# Basic metadata
name = 'aiocypher'
version = '0.1.1'
description = 'AsyncIO wrapper around the neo4j driver'
url = 'https://github.com/bbc/rd-cloudfit-python-aiocypher'
author = 'James Weaver'
author_email = 'james.barett@bbc.co.uk'
license = 'License :: OSI Approved :: Apache Software License'
long_description = description

packages = {
    name: name,
    name + ".aioagensgraph": name + "/aioagensgraph",
    name + ".aioneo4j": name + "/aioneo4j",
    name + ".interface": name + "/interface",
    name + ".internal": name + "/internal",
}
package_names = packages.keys()

packages_required = [
    "async_generator",
    "neo4j < 4.3.0",
    "janus",
]

extras_require = {
    "agensgraph": [
        "agensgraph",
        "aiopg",
        "async_exit_stack"
    ],
    "neo4j": []
}

setup(name=name,
      python_requires='>=3.6',
      version=version,
      description=description,
      url=url,
      author=author,
      author_email=author_email,
      license=license,
      packages=package_names,
      package_dir=packages,
      package_data={
          package_name: ["py.typed"] for package_name in package_names
      },
      install_requires=packages_required,
      extras_require=extras_require,
      scripts=[],
      data_files=[],
      long_description=long_description)
