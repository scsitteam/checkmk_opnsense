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
from cmk_addons.plugins.opnsense.agent_based import opnsense_vip

EXAMPLE_CARP_SECTION = {"allow": "1", "demotion": "0", "maintenancemode": False, "status_msg": ""}

EXAMPLE_VIP_SECTION = [
    {"advbase": "1", "advskew": "0", "interface": "wan", "mode": "carp", "status": "MASTER", "status_txt": "MASTER", "subnet": "10.0.0.1", "vhid": "1", "vhid_txt": "1 (freq. 1/0)"},
    {"advbase": "1", "advskew": "0", "interface": "lan", "mode": "carp", "status": "MASTER", "status_txt": "MASTER", "subnet": "192.168.0.1", "vhid": "2", "vhid_txt": "2 (freq. 1/0)"},
    {"advbase": "1", "advskew": "0", "interface": "lan", "mode": "carp", "status": "BACKUP", "status_txt": "BACKUP", "subnet": "192.168.0.2", "vhid": "3", "vhid_txt": "3 (freq. 1/0)"},
    {"advbase": "1", "advskew": "0", "interface": "lan", "mode": "vrrp2", "status": "MASTER", "status_txt": "MASTER", "subnet": "192.168.0.3", "vhid": "4", "vhid_txt": "4 (freq. 1/0)"},
]

@pytest.mark.parametrize('string_table, result', [
    ([], None),
    (
        [['{"allow": "1", "demotion": "0", "maintenancemode": false, "status_msg": ""}']],
        EXAMPLE_CARP_SECTION
    ),
])
def test_parse_opnsense_carp(string_table, result):
    assert opnsense_vip.parse_opnsense_carp(string_table) == result


@pytest.mark.parametrize('string_table, result', [
    ([], []),
    (
        [
            ['{"advbase": "1", "advskew": "0", "interface": "wan", "mode": "carp", "status": "MASTER", "status_txt": "MASTER", "subnet": "10.0.0.1", "vhid": "1", "vhid_txt": "1 (freq. 1/0)"}'],
            ['{"advbase": "1", "advskew": "0", "interface": "lan", "mode": "carp", "status": "MASTER", "status_txt": "MASTER", "subnet": "192.168.0.1", "vhid": "2", "vhid_txt": "2 (freq. 1/0)"}'],
            ['{"advbase": "1", "advskew": "0", "interface": "lan", "mode": "carp", "status": "BACKUP", "status_txt": "BACKUP", "subnet": "192.168.0.2", "vhid": "3", "vhid_txt": "3 (freq. 1/0)"}'],
            ['{"advbase": "1", "advskew": "0", "interface": "lan", "mode": "vrrp2", "status": "MASTER", "status_txt": "MASTER", "subnet": "192.168.0.3", "vhid": "4", "vhid_txt": "4 (freq. 1/0)"}'],
        ],
        EXAMPLE_VIP_SECTION
    ),
])
def test_parse_opnsense_vip(string_table, result):
    assert list(opnsense_vip.parse_opnsense_vip(string_table)) == result


@pytest.mark.parametrize('section, result', [
    (None, []),
    (
        {"allow": "1", "demotion": "0", "maintenancemode": False, "status_msg": ""},
        [Service()]
    ),
])
def test_discovery_opnsense_carp(section, result):
    assert list(opnsense_vip.discovery_opnsense_carp(section, None)) == result


@pytest.mark.parametrize('params, section_carp, result', [
    ({}, None, []),
    (
        {},
        {"allow": "1", "demotion": "0", "maintenancemode": False, "status_msg": ""},
        [
            Result(state=State.OK, summary='OK'),
            Metric('demotion', 0.0),
            Result(state=State.OK, summary='Master: 2'),
            Metric('carp_master', 2.0, boundaries=(0.0, 3.0)),
            Result(state=State.OK, summary='Backup: 1'),
            Metric('carp_backup', 1.0, boundaries=(0.0, 3.0)),
        ]
    ),
    (
        {},
        {"allow": "1", "demotion": "240", "maintenancemode": True, "status_msg": "Foo"},
        [
            Result(state=State.OK, summary='Foo'),
            Metric('demotion', 240.0),
            Result(state=State.WARN, summary='Maintenance Mode is active'),
            Result(state=State.OK, summary='Master: 2'),
            Metric('carp_master', 2.0, boundaries=(0.0, 3.0)),
            Result(state=State.OK, summary='Backup: 1'),
            Metric('carp_backup', 1.0, boundaries=(0.0, 3.0)),
        ]
    ),
    (
        {'master_levels_lower': ('fixed', (3, 2)), 'backup_levels_upper': ('fixed', (1, 1))},
        {"allow": "1", "demotion": "0", "maintenancemode": False, "status_msg": "Foo"},
        [
            Result(state=State.OK, summary='Foo'),
            Metric('demotion', 0.0),
            Result(state=State.WARN, summary='Master: 2 (warn/crit below 3/2)'),
            Metric('carp_master', 2.0, boundaries=(0.0, 3.0)),
            Result(state=State.CRIT, summary='Backup: 1 (warn/crit at 1/1)'),
            Metric('carp_backup', 1.0, levels=(1.0, 1.0), boundaries=(0.0, 3.0)),
        ]
    ),
])
def test_check_opnsense_carp(params, section_carp, result):
    assert list(opnsense_vip.check_opnsense_carp(params, section_carp, EXAMPLE_VIP_SECTION)) == result



@pytest.mark.parametrize('params, section, result', [
    ({}, None, []),
    ({}, EXAMPLE_VIP_SECTION, []),
    ({'discover': 'master'}, EXAMPLE_VIP_SECTION, [
        Service(item='wan@1', parameters={'interface': 'wan', 'vhid': '1', 'discovery_status': 'MASTER'}),
        Service(item='lan@2', parameters={'interface': 'lan', 'vhid': '2', 'discovery_status': 'MASTER'}),
        Service(item='lan@4', parameters={'interface': 'lan', 'vhid': '4', 'discovery_status': 'MASTER'}),
    ]),
    ({'discover': 'all'}, EXAMPLE_VIP_SECTION, [
        Service(item='wan@1', parameters={'interface': 'wan', 'vhid': '1', 'discovery_status': 'MASTER'}),
        Service(item='lan@2', parameters={'interface': 'lan', 'vhid': '2', 'discovery_status': 'MASTER'}),
        Service(item='lan@3', parameters={'interface': 'lan', 'vhid': '3', 'discovery_status': 'BACKUP'}),
        Service(item='lan@4', parameters={'interface': 'lan', 'vhid': '4', 'discovery_status': 'MASTER'}),
    ]),
    ({'discover': 'all', 'groupby': 'interface'}, EXAMPLE_VIP_SECTION, [
        Service(item='lan', parameters={'interface': 'lan', 'discovery_status': {'2': 'MASTER', '3': 'BACKUP', '4': 'MASTER'}}),
        Service(item='wan', parameters={'interface': 'wan', 'discovery_status': {'1': 'MASTER'}}),
    ]),
])
def test_discovery_opnsense_vip(params, section, result):
    assert list(opnsense_vip.discovery_opnsense_vip(params, section)) == result


@pytest.mark.parametrize('params, result', [
    ({'interface': 'none'}, []),
    (
        {'interface': 'wan', 'vhid': '1', 'discovery_status': 'MASTER'},
        [
            Result(state=State.OK, summary='MASTER: 10.0.0.1'),
        ]
    ),
    (
        {'interface': 'wan', 'vhid': '1', 'discovery_status': 'BACKUP'},
        [
            Result(state=State.WARN, summary='MASTER: 10.0.0.1 (expected: BACKUP)'),
        ]
    ),
    (
        {'interface': 'wan', 'vhid': '1', 'expected_status': 'BACKUP',  'discovery_status': 'MASTER'},
        [
            Result(state=State.WARN, summary='MASTER: 10.0.0.1 (expected: BACKUP)'),
        ]
    ),
    (
        {'interface': 'wan', 'vhid': '0', 'discovery_status': 'BACKUP'},
        [
        ]
    ),
    (
        {'interface': 'wan2', 'vhid': '1', 'discovery_status': 'BACKUP'},
        [
        ]
    ),
    (
        {'interface': 'lan', 'discovery_status': {'2': 'MASTER', '3': 'MASTER', '4': 'MASTER'}},
        [
            Result(state=State.OK, summary='MASTER: 192.168.0.1'),
            Result(state=State.WARN, summary='BACKUP: 192.168.0.2 (expected: MASTER)'),
            Result(state=State.OK, summary='MASTER: 192.168.0.3'),
        ]
    ),
    (
        {'interface': 'lan', 'discovery_status': {'2': 'MASTER', '3': 'BACKUP', '4': 'MASTER'}},
        [
            Result(state=State.OK, summary='MASTER: 192.168.0.1'),
            Result(state=State.OK, summary='BACKUP: 192.168.0.2'),
            Result(state=State.OK, summary='MASTER: 192.168.0.3'),
        ]
    ),
    (
        {'interface': 'lan', 'expected_status': 'MASTER', 'discovery_status': {'2': 'MASTER', '3': 'BACKUP', '4': 'MASTER'}},
        [
            Result(state=State.OK, summary='MASTER: 192.168.0.1'),
            Result(state=State.WARN, summary='BACKUP: 192.168.0.2 (expected: MASTER)'),
            Result(state=State.OK, summary='MASTER: 192.168.0.3'),
        ]
    ),
])
def test_check_opnsense_vip(params, result):
    assert list(opnsense_vip.check_opnsense_vip('item', params, EXAMPLE_VIP_SECTION)) == result
