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


from unittest import TestCase

from cypy.collections import ReactiveSet


class ReactiveSetTestCase(TestCase):

    @staticmethod
    def new_set(elements, added, removed):
        s = ReactiveSet(elements, on_add=lambda *x: added.update(set(x)), on_remove=lambda *x: removed.update(set(x)))
        added.clear()
        removed.clear()
        return s

    def test_ior(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s |= {2, 3}
        assert s == {1, 2, 3}
        assert added == {3}
        assert not removed

    def test_iand(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s &= {2, 3}
        assert s == {2}
        assert not added
        assert removed == {1, 3}

    def test_isub(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s -= {2, 3}
        assert s == {1}
        assert not added
        assert removed == {2}

    def test_ixor(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s ^= {2, 3}
        assert s == {1, 3}
        assert added == {3}
        assert removed == {2}

    def test_add_existing(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s.add(2)
        assert s == {1, 2}
        assert not added
        assert not removed

    def test_add_other(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s.add(3)
        assert s == {1, 2, 3}
        assert added == {3}
        assert not removed

    def test_remove_existing(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s.remove(2)
        assert s == {1}
        assert not added
        assert removed == {2}

    def test_remove_other(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        with self.assertRaises(KeyError):
            s.remove(3)

    def test_discard_existing(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s.discard(2)
        assert s == {1}
        assert not added
        assert removed == {2}

    def test_discard_other(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s.discard(3)
        assert s == {1, 2}
        assert not added
        assert not removed

    def test_pop_from_populated(self):
        added = set()
        removed = set()
        s = self.new_set({1}, added, removed)
        popped = s.pop()
        assert popped == 1
        assert not s
        assert not added
        assert removed == {1}

    def test_pop_from_empty(self):
        added = set()
        removed = set()
        s = self.new_set({}, added, removed)
        with self.assertRaises(KeyError):
            _ = s.pop()

    def test_clear(self):
        added = set()
        removed = set()
        s = self.new_set({1, 2}, added, removed)
        s.clear()
        assert not s
        assert not added
        assert removed == {1, 2}
