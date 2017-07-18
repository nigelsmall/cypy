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

from cypy.meta import __distribution__, __version__, __description__, __author__, __email__, __url__, __license__


with open("README.rst") as f:
    long_description = f.read()


packages = find_packages(exclude=("bin", "test", "test.*"))
package_metadata = {
    "name": __distribution__,
    "version": __version__,
    "description": __description__,
    "long_description": long_description,
    "author": __author__,
    "author_email": __email__,
    "url": __url__,
    "entry_points": {
    },
    "packages": packages,
    "py_modules": [],
    "install_requires": [
    ],
    "license": __license__,
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
        "Topic :: Software Development",
    ],
    "zip_safe": False,
}

setup(**package_metadata)
