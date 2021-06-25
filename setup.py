# Copyright 2021 British Broadcasting Corporation
#
# This is an internal BBC tool and is not licensed externally
# If you have received a copy of this erroneously then you do
# not have permission to reproduce it.

from setuptools import setup

# Basic metadata
name = 'aiocypher'
version = '0.1.0'
description = 'AsyncIO wrapper around the neo4j driver'
url = 'https://github.com/bbc/rd-apmm-python-aiocypher'
author = 'James Weaver'
author_email = 'james.barett@bbc.co.uk'
license = ''
long_description = description

packages = {
    name: name
}
package_names = packages.keys()

# This is where you list packages which are required
packages_required = []

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
      scripts=[],
      data_files=[],
      long_description=long_description)
