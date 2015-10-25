#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# CyPy: Cypher Framework for Python
# Copyright 2015 Nigel Small
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sys import version_info

if version_info >= (3,):

    integer = int
    string = (bytes, str)
    unicode = str

    def bstr(s, encoding="utf-8"):
        if isinstance(s, bytes):
            return s
        elif isinstance(s, bytearray):
            return bytes(s)
        elif isinstance(s, str):
            return bytes(s, encoding)
        else:
            return bytes(str(s), encoding)

    def ustr(s, encoding="utf-8"):
        """ Convert argument to unicode string.
        """
        if isinstance(s, str):
            return s
        try:
            return s.decode(encoding)
        except AttributeError:
            return str(s)

    def xstr(s, encoding="utf-8"):
        """ Convert argument to string type returned by __str__.
        """
        return ustr(s, encoding)

else:
    integer = (int, long)
    string = (str, unicode)
    unicode = unicode

    def bstr(s, encoding="utf-8"):
        if isinstance(s, bytes):
            return s
        elif isinstance(s, bytearray):
            return bytes(s)
        elif isinstance(s, unicode):
            return s.encode(encoding)
        else:
            return str(s)

    def ustr(s, encoding="utf-8"):
        """ Convert argument to unicode string.
        """
        if isinstance(s, str):
            return s.decode(encoding)
        else:
            return unicode(s)

    def xstr(s, encoding="utf-8"):
        """ Convert argument to string type returned by __str__.
        """
        if isinstance(s, str):
            return s
        else:
            return unicode(s).encode(encoding)
