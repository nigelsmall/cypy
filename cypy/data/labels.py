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


from cypy.encoding import cypher_escape


class LabelSetView(object):

    def __init__(self, elements=(), selected=(), **kwargs):
        self.__elements = frozenset(elements)
        self.__selected = tuple(selected)
        self.__kwargs = kwargs

    def __repr__(self):
        if self.__selected:
            return "".join(":%s" % cypher_escape(e, **self.__kwargs) for e in self.__selected if e in self.__elements)
        else:
            return "".join(":%s" % cypher_escape(e, **self.__kwargs) for e in sorted(self.__elements))

    def __getattr__(self, element):
        if element in self.__selected:
            return self.__class__(self.__elements, self.__selected)
        else:
            return self.__class__(self.__elements, self.__selected + (element,))

    def __len__(self):
        return len(self.__elements)

    def __iter__(self):
        return iter(self.__elements)

    def __contains__(self, element):
        return element in self.__elements

    def __and__(self, other):
        return self.__elements & set(other)

    def __or__(self, other):
        return self.__elements | set(other)

    def __sub__(self, other):
        return self.__elements - set(other)

    def __xor__(self, other):
        return self.__elements ^ set(other)