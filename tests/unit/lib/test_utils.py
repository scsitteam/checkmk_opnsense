#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_opnsense - Checkmk extension for OPNsense
#
# Copyright (C) 2024  Marius Rieder <marius.rieder@scs.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pytest  # type: ignore[import]
from cmk_addons.plugins.opnsense.lib import utils


@pytest.mark.parametrize('string_table, result', [
    ([], None),
    ([['{"key":"value"}']], {'key': 'value'}),
])
def test_parse_json(string_table, result):
    assert utils.parse_json(string_table) == result

@pytest.mark.parametrize('string_table, result', [
    ([], None),
    ([['{"key":"value"}']], [{'key': 'value'}]),
    ([['{"key":"value 1"}'], ['{"key":"value 2"}']], [{'key': 'value 1'}, {'key': 'value 2'}]),
])
def test_parse_jsonl(string_table, result):
    assert utils.parse_jsonl(string_table) == result
