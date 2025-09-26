#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_opnsense - Checkmk extension for OPNsense
#
# Copyright (C) 2025  Marius Rieder <marius.rieder@scs.ch>
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
from cmk_addons.plugins.opnsense.agent_based import opnsense_memory

EXAMPLE_STRINGTABLE = [['''{"memory": {"arc": "5652086360", "arc_frmt": "5390", "arc_txt": "ARC size 5390 MB", "total": "68538294272", "total_frmt": "65363", "used": 8770012124, "used_frmt": "8363"}, "swap": [{"device": "/dev/gpt/swapfs", "total": "9033912", "used": "0"}]}''']]

EXAMPLE_SECTION = {
    'Cached': 5652086360,
    'MemFree': 54116195788,
    'MemTotal': 68538294272,
    'SwapFree': 9033912,
    'SwapTotal': 9033912,
}


@pytest.mark.parametrize('string_table, result', [
    ({}, None),
    (EXAMPLE_STRINGTABLE, EXAMPLE_SECTION),
])
def test_parse_opnsense_gateway(string_table, result):
    assert opnsense_memory.parse_opnsense_memory(string_table) == result
