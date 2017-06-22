#!/usr/bin/env python
# -*- encoding: utf-8 -*-

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


from re import compile as re_compile


WORD_FIRST = re_compile(r"(.)([A-Z][a-z]+)")
WORD_ALL = re_compile(r"([a-z0-9])([A-Z])")


def snake_case(s):
    words = s.replace("_", " ").replace("-", " ").split()
    return "_".join(word.lower() for word in words)


def title_case(s):
    s1 = WORD_FIRST.sub(r"\1 \2", s)
    return WORD_ALL.sub(r"\1 \2", s1).title()


def relationship_case(s):
    s1 = WORD_FIRST.sub(r"\1_\2", s)
    return WORD_ALL.sub(r"\1_\2", s1).upper()


def label_case(s):
    return "".join(word.title() for word in s.split("_"))
