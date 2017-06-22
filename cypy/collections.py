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
class ReactiveSet(set):
    """ A :class:`set` that can trigger callbacks for each element added
    or removed.
    """

    def __init__(self, iterable=(), on_add=None, on_remove=None):
        self._on_add = on_add
        self._on_remove = on_remove
        elements = set(iterable)
        set.__init__(self, elements)
        if callable(self._on_add):
            self._on_add(*elements)

    def __ior__(self, other):
        elements = other - self
        set.__ior__(self, other)
        if callable(self._on_add):
            self._on_add(*elements)
        return self

    def __iand__(self, other):
        elements = self ^ other
        set.__iand__(self, other)
        if callable(self._on_remove):
            self._on_remove(*elements)
        return self

    def __isub__(self, other):
        elements = self & other
        set.__isub__(self, other)
        if callable(self._on_remove):
            self._on_remove(*elements)
        return self

    def __ixor__(self, other):
        added = other - self
        removed = self & other
        set.__ixor__(self, other)
        if callable(self._on_add):
            self._on_add(*added)
        if callable(self._on_remove):
            self._on_remove(*removed)
        return self

    def add(self, element):
        if element not in self:
            set.add(self, element)
            if callable(self._on_add):
                self._on_add(element)

    def remove(self, element):
        set.remove(self, element)
        if callable(self._on_remove):
            self._on_remove(element)

    def discard(self, element):
        if element in self:
            set.discard(self, element)
            if callable(self._on_remove):
                self._on_remove(element)

    def pop(self):
        element = set.pop(self)
        if callable(self._on_remove):
            self._on_remove(element)
        return element

    def clear(self):
        elements = set(self)
        set.clear(self)
        if callable(self._on_remove):
            self._on_remove(*elements)