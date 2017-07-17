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

from cypy.data import Value, Record


class ValueTestCase(TestCase):

    def test_null(self):
        self.assertEqual(Value.coerce(None), None)

    def test_true(self):
        self.assertEqual(Value.coerce(True), True)

    def test_false(self):
        self.assertEqual(Value.coerce(False), False)

    def test_int(self):
        self.assertEqual(Value.coerce(1), 1)

    def test_int_overflow(self):
        with self.assertRaises(ValueError):
            _ = Value.coerce(2 ** 63)

    def test_float(self):
        self.assertEqual(Value.coerce(3.14), 3.14)

    def test_byte_string(self):
        self.assertEqual(Value.coerce(bytearray(b"hello")), bytearray(b"hello"))

    def test_unicode_string(self):
        self.assertEqual(Value.coerce(u"hello"), u"hello")

    def test_default_string(self):
        self.assertEqual(Value.coerce("hello"), u"hello")

    def test_dict(self):
        self.assertEqual(Value.coerce({"one": 1, "two": 2}), {"one": 1, "two": 2})

    def test_list(self):
        self.assertEqual(Value.coerce([1, 2, 3]), [1, 2, 3])

    def test_set(self):
        self.assertEqual(Value.coerce({1, 2, 3}), [1, 2, 3])

    def test_tuple(self):
        self.assertEqual(Value.coerce((1, 2, 3)), [1, 2, 3])

    def test_frozenset(self):
        self.assertEqual(Value.coerce(frozenset([1, 2, 3])), [1, 2, 3])

    def test_other_iterable(self):

        def ten():
            for n in range(1, 11):
                yield n

        self.assertEqual(Value.coerce(ten()), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_other_type(self):
        with self.assertRaises(TypeError):
            _ = Value.coerce(object())


class RecordTestCase(TestCase):

    record_data = [("one", "eins"), ("two", "zwei"), ("three", "drei")]
    record = Record(record_data)

    def test_record_size(self):
        self.assertEqual(len(self.record), len(self.record_data))

    def test_record_keys(self):
        self.assertEqual(list(self.record.keys()), [key for key, _ in self.record_data])

    def test_record_values(self):
        self.assertEqual(list(self.record.values()), [value for _, value in self.record_data])

    def test_record_items(self):
        self.assertEqual(list(self.record.items()), self.record_data)

    def test_record_as_dict(self):
        self.assertEqual(dict(self.record), dict(self.record_data))

    def test_record_as_list(self):
        self.assertEqual(list(self.record), [value for _, value in self.record_data])

    def test_record_as_tuple(self):
        self.assertEqual(tuple(self.record), tuple(value for _, value in self.record_data))

    def test_uneven_data(self):
        with self.assertRaises(ValueError):
            _ = Record([("one",), ("two", "zwei"), ("three", "drei", 3)])

    def test_get_item_by_index(self):
        self.assertEqual(self.record[0], "eins")
        self.assertEqual(self.record[1], "zwei")
        self.assertEqual(self.record[2], "drei")
        with self.assertRaises(IndexError):
            _ = self.record[3]

    def test_get_item_by_name(self):
        self.assertEqual(self.record["one"], "eins")
        self.assertEqual(self.record["two"], "zwei")
        self.assertEqual(self.record["three"], "drei")
        with self.assertRaises(KeyError):
            _ = self.record["four"]

    def test_get_method(self):
        self.assertEqual(self.record.get("one"), "eins")
        self.assertEqual(self.record.get("two"), "zwei")
        self.assertEqual(self.record.get("three"), "drei")
        self.assertIsNone(self.record.get("four"))

    def test_slice_type(self):
        self.assertIsInstance(self.record[0:2], Record)

    def test_slice_boundaries(self):
        self.assertEqual(self.record[0:2], Record([("one", "eins"), ("two", "zwei")]))
        self.assertEqual(self.record[1:2], Record([("two", "zwei")]))
        self.assertEqual(self.record[1:3], Record([("two", "zwei"), ("three", "drei")]))
        self.assertEqual(self.record[1:], Record([("two", "zwei"), ("three", "drei")]))

    def test_get_item_with_other_type(self):
        with self.assertRaises(KeyError):
            _ = self.record[object()]
