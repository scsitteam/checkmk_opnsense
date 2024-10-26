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
import json
from pathlib import Path
from cmk.agent_based.v2 import (
    Result,
    Service,
    State,
    Metric,
)
from cmk_addons.plugins.opnsense.agent_based import opnsense_firmware

EXAMPLE_STRINGTABLE = [
    [Path('tests/unit/agent_based/test_data/firmware_info/uptodate.json').read_text()]
]

EXAMPLE_SECTION = json.load(Path('tests/unit/agent_based/test_data/firmware_info/uptodate.json').open())
EXAMPLE_SECTION_OUTDATED = json.load(Path('tests/unit/agent_based/test_data/firmware_info/outdated.json').open())
EXAMPLE_SECTION_NOSTATUS = json.load(Path('tests/unit/agent_based/test_data/firmware_info/nostatus.json').open())
EXAMPLE_SECTION_BUSINESS = {
    "product_id": "opnsense-business",
    "product": {"product_license": {"valid_to": "2025-07-31"}},
}


@pytest.mark.parametrize('string_table, result', [
    ([], None),
    (EXAMPLE_STRINGTABLE, EXAMPLE_SECTION),
])
def test_parse_opnsense_gateway(string_table, result):
    assert opnsense_firmware.parse_opnsense_firmware(string_table) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    (EXAMPLE_SECTION, [Service()]),
])
def test_discovery_opnsense_gateway(section, result):
    assert list(opnsense_firmware.discovery_opnsense_firmware(section)) == result


@pytest.mark.parametrize('params, section, result', [
    ({}, EXAMPLE_SECTION, [
        Result(state=State.OK, summary='24.7 (Thriving Tiger)'),
        Result(state=State.OK, notice='Last update check: 2 hours 57 minutes'),
        Metric('last_check', 10649.0),
        Metric('updates', 0.0),
    ]),
    ({'last_check': ('fixed', (7200, 14400))}, EXAMPLE_SECTION, [
        Result(state=State.OK, summary='24.7 (Thriving Tiger)'),
        Result(state=State.WARN, summary='Last update check: 2 hours 57 minutes (warn/crit at 2 hours 0 minutes/4 hours 0 minutes)'),
        Metric('last_check', 10649.0, levels=(7200.0, 14400.0)),
        Metric('updates', 0.0),
    ]),
    ({}, EXAMPLE_SECTION_NOSTATUS, [
        Result(state=State.OK, summary='24.7 (Thriving Tiger)'),
        Result(state=State.OK, summary='Firmware status requires to check for update first to provide more information.'),
    ]),
    ({}, EXAMPLE_SECTION_OUTDATED, [
        Result(state=State.OK, summary='24.7 (Thriving Tiger)'),
        Result(state=State.OK, notice='Last update check: 3 hours 27 minutes'),
        Metric('last_check', 12455.0),
        Result(state=State.OK, summary='There are 75 updates available, total download size is 289.8MiB. This update requires a reboot.'),
        Metric('updates', 4.0),
    ]),
])
def test_check_opnsense_firmware(freezer, params, section, result):
    freezer.move_to('2024-10-25 20:00')
    assert list(opnsense_firmware.check_opnsense_firmware(params, section)) == result


@pytest.mark.parametrize('section, result', [
    ({}, []),
    (EXAMPLE_SECTION, []),
    (EXAMPLE_SECTION_BUSINESS, [Service()]),
])
def test_discovery_opnsense_business(section, result):
    assert list(opnsense_firmware.discovery_opnsense_business(section)) == result


@pytest.mark.parametrize('params, result', [
    ({}, [
        Result(state=State.OK, summary='License expires in: 278 days'),
        Metric('expiredays', 278.0),
    ]),
    ({'expiredays': ('fixed', (360, 180))}, [
        Result(state=State.WARN, summary='License expires in: 278 days (warn/crit below 360 days/180 days)'),
        Metric('expiredays', 278.0),
    ]),
    ({'expiredays': ('fixed', (360, 300))}, [
        Result(state=State.CRIT, summary='License expires in: 278 days (warn/crit below 360 days/300 days)'),
        Metric('expiredays', 278.0),
    ]),
])
def test_check_opnsense_business(freezer, params, result):
    freezer.move_to('2024-10-25 20:00')
    assert list(opnsense_firmware.check_opnsense_business(params, EXAMPLE_SECTION_BUSINESS)) == result
