#!/usr/bin/env python
# coding: utf-8

# Copyright 2011-2017, Nigel Small
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


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


__author__ = "Nigel Small <technige@nige.tech>"
__copyright__ = "2011-2017, Nigel Small"
__email__ = "cypy@nige.tech"
__license__ = "Apache License, Version 2.0"
__package__ = "cypy"
__version__ = "1.0.0a1"


packages = find_packages(exclude=("test", "test.*"))
package_metadata = {
    "name": __package__,
    "version": __version__,
    "description": "Cypher resource library for Python",
    "long_description": "",
    "author": __author__,
    "author_email": __email__,
    "url": "http://nige.tech/cypy",
    "entry_points": {
    },
    "packages": packages,
    "py_modules": [],
    "install_requires": [
    ],
    "license": __license__,
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
        "Topic :: Software Development",
    ],
    "zip_safe": False,
}

setup(**package_metadata)
