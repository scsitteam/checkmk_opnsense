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
from freezegun import freeze_time
from cmk.agent_based.v2 import (
    Result,
    Service,
    State,
    Metric,
)
from cmk_addons.plugins.opnsense.agent_based import opnsense_snapshot

EXAMPLE_STRINGTABLE = [
    ['{"active": "-", "created": 1748248680, "created_str": "2025-05-26 10:38", "mountpoint": "-", "name": "2025-05-26-10-38", "size": "886M", "uuid": "fb84e9bc-bf42-3980-b6e5-fa1272c0766c"}'],
    ['{"active": "NR", "created": 1714642080, "created_str": "2024-05-02 11:28", "mountpoint": "/", "name": "default", "size": "2.26G", "uuid": "e918b3ca-7846-3104-8c4d-feb016a9e618"}'],
]

EXAMPLE_SECTION = [
    {'name': '2025-05-26-10-38', 'created': 1748248680, 'current': False, 'reboot': False, 'size': 929038336},
    {'name': 'default', 'created': 1714642080, 'current': True, 'reboot': True, 'size': 2426656522},
]


@pytest.mark.parametrize('string_table, result', [
    ([], []),
    (EXAMPLE_STRINGTABLE, EXAMPLE_SECTION),
])
def test_parse_opnsense_snapshot(string_table, result):
    assert opnsense_snapshot.parse_opnsense_snapshot(string_table) == result


@pytest.mark.parametrize('section, result', [
    ([], []),
    (EXAMPLE_SECTION, [Service()]),
])
def test_discovery_opnsense_snapshot(section, result):
    assert list(opnsense_snapshot.discovery_opnsense_snapshot(section)) == result


@freeze_time('2025-05-28 10:55')
@pytest.mark.parametrize('params, result', [
    ({}, [
        Result(state=State.OK, summary='Running on default'),
        Result(state=State.OK, summary='Oldes snapshot age: 2 days 2 hours'),
        Metric('oldest', 181020.0),
        Result(state=State.OK, summary='Biggest snapshot: 929 MB'),
        Metric('maxsize', 929038336.0),
    ]),
    ({'running': 'pytest'}, [
        Result(state=State.WARN, summary='Running on default (expected: pytest)'),
        Result(state=State.OK, summary='Oldes snapshot age: 2 days 2 hours'),
        Metric('oldest', 181020.0),
        Result(state=State.OK, summary='Biggest snapshot: 929 MB'),
        Metric('maxsize', 929038336.0),
    ]),
    ({'oldest': ('fixed', (86400, 864000)), 'maxsize': ('fixed', (0.5 * 1024**3, 1024**3))}, [
        Result(state=State.OK, summary='Running on default'),
        Result(state=State.WARN, summary='Oldes snapshot age: 2 days 2 hours (warn/crit at 1 day 0 hours/10 days 0 hours)'),
        Metric('oldest', 181020.0, levels=(86400.0, 864000.0)),
        Result(state=State.WARN, summary='Biggest snapshot: 929 MB (warn/crit at 537 MB/1.07 GB)'),
        Metric('maxsize', 929038336.0, levels=(536870912.0, 1073741824.0)),
    ]),
])
def test_check_opnsense_snapshot(params, result):
    assert list(opnsense_snapshot.check_opnsense_snapshot(params, EXAMPLE_SECTION)) == result
