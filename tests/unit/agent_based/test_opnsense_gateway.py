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
from cmk.agent_based.v2 import (
    Result,
    Service,
    State,
    Metric,
)
from cmk_addons.plugins.opnsense.agent_based import opnsense_gateway

EXAMPLE_STRINGTABLE = [
    ['{"name":"GW_A","address":"192.168.0.1","status":"none","loss":"0.0 %","delay":"0.9 ms","stddev":"0.1 ms","monitor":"192.168.0.11","status_translated":"Online"}'],
    ['{"name":"GW_B","address":"192.168.0.2","status":"none","loss":"5.0 %","delay":"6.6 ms","stddev":"0.1 ms","monitor":"192.168.0.22","status_translated":"Online"}'],
    ['{"name":"GW_C","address":"192.168.0.3","status":"none","loss":"~","delay":"~","stddev":"~","monitor":"~","status_translated":"Online"}'],
    ['{"name":"GW_D","address":"192.168.0.4","status":"none","loss":"100.0 %","delay":"6.6 ms","stddev":"0.1 ms","monitor":"192.168.0.44","status_translated":"Offline"}'],
]

EXAMPLE_SECTION = {
    "GW_A": {"name": "GW_A", "address": "192.168.0.1", "status": "none", "loss": 0.0, "delay": 0.0009, "stddev": 0.0001, "monitor": "192.168.0.11", "status_translated": "Online"},
    "GW_B": {"name": "GW_B", "address": "192.168.0.2", "status": "none", "loss": 5.0, "delay": 0.0066, "stddev": 0.0001, "monitor": "192.168.0.22", "status_translated": "Online"},
    "GW_C": {"name": "GW_C", "address": "192.168.0.3", "status": "none", "loss": None, "delay": None, "stddev": None, "monitor": None, "status_translated": "Online"},
    "GW_D": {"name": "GW_D", "address": "192.168.0.4", "status": "none", "loss": 100.0, "delay": 0.0066, "stddev": 0.0001, "monitor": "192.168.0.44", "status_translated": "Offline"},
}


@pytest.mark.parametrize('string_table, result', [
    ([], {}),
    (EXAMPLE_STRINGTABLE, EXAMPLE_SECTION),
])
def test_parse_opnsense_gateway(string_table, result):
    assert opnsense_gateway.parse_opnsense_gateway(string_table) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    (
        EXAMPLE_SECTION,
        [
            Service(item='GW_A'),
            Service(item='GW_B'),
            Service(item='GW_D'),
        ]
    ),
])
def test_discovery_opnsense_gateway(section, result):
    assert list(opnsense_gateway.discovery_opnsense_gateway(section)) == result


@pytest.mark.parametrize('item, params, result', [
    ('', {}, []),
    ('GW_A', {}, [
        Result(state=State.OK, summary='Online'),
        Result(state=State.OK, summary='Monitor 192.168.0.11'),
        Result(state=State.OK, summary='rtt: 900 microseconds'),
        Metric('rta', 0.0009, levels=(0.1, 0.2)),
        Result(state=State.OK, summary='loss: 0%'),
        Metric('pl', 0, levels=(10.0, 20.0)),
    ]),
    ('GW_A', {'status': 'Offline'}, [
        Result(state=State.WARN, summary='Online (expected: Offline)'),
        Result(state=State.OK, summary='Monitor 192.168.0.11'),
        Result(state=State.OK, summary='rtt: 900 microseconds'),
        Metric('rta', 0.0009, levels=(0.1, 0.2)),
        Result(state=State.OK, summary='loss: 0%'),
        Metric('pl', 0, levels=(10.0, 20.0)),
    ]),
    ('GW_C', {}, [
        Result(state=State.OK, summary='Online')
    ]),
    ('GW_D', {}, [
        Result(state=State.WARN, summary='Offline (expected: Online)'),
        Result(state=State.OK, summary='Monitor 192.168.0.44'),
        Result(state=State.OK, summary='rtt: 7 milliseconds'),
        Metric('rta', 0.0066, levels=(0.1, 0.2)),
        Result(state=State.CRIT, summary='loss: 100.00% (warn/crit at 10.00%/20.00%)'),
        Metric('pl', 100, levels=(10.0, 20.0)),
    ]),
])
def test_check_opnsense_gateway(item, params, result):
    assert list(opnsense_gateway.check_opnsense_gateway(item, params, EXAMPLE_SECTION)) == result
