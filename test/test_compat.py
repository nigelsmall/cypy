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

from cypy.compat import bstr, ustr


class ByteStringTestCase(TestCase):

    def test_should_convert_bytearray(self):
        b = bytearray([65, 98, 99])
        self.assertIs(bstr(b), b)

    def test_should_convert_bytes(self):
        self.assertEqual(bstr(b"Abc"), bytearray(b"Abc"))

    def test_should_convert_unicode(self):
        self.assertEqual(bstr(u"Äbc"), bytearray(b'\xC3\x84bc'))

    def test_should_convert_coercible_object(self):

        class Date(object):

            def __init__(self, year, month, day):
                self.year = year
                self.month = month
                self.day = day

            def __bytes__(self):
                return bytearray([self.year // 0x100, self.year % 0x100, self.month, self.day])

        d = Date(1963, 11, 23)
        self.assertEqual(bstr(d), bytearray(b'\x07\xAB\x0B\x17'))

    def test_should_convert_integer(self):
        self.assertEqual(bstr(1), bytearray(b'1'))

    def test_should_convert_float(self):
        self.assertEqual(bstr(3.1415), bytearray(b'3.1415'))


class UnicodeStringTestCase(TestCase):

    def test_should_convert_unicode(self):
        u = u"Äbc"
        self.assertIs(ustr(u), u)

    def test_should_convert_bytearray(self):
        self.assertEqual(ustr(bytearray([65, 98, 99])), u"Abc")

    def test_should_convert_bytes(self):
        self.assertEqual(ustr(b"Abc"), u"Abc")

    def test_should_convert_coercible_object(self):

        class Date(object):

            def __init__(self, year, month, day):
                self.year = year
                self.month = month
                self.day = day

            def __str__(self):
                return "{}-{}-{}".format(self.year, self.month, self.day)

            def __unicode__(self):
                return u"{}-{}-{}".format(self.year, self.month, self.day)

        d = Date(1963, 11, 23)
        self.assertEqual(ustr(d), u"1963-11-23")

    def test_should_convert_integer(self):
        self.assertEqual(ustr(1), u'1')

    def test_should_convert_float(self):
        self.assertEqual(ustr(3.1415), u'3.1415')
