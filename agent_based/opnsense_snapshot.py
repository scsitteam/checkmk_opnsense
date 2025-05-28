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

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
    StringTable,
)
from cmk_addons.plugins.opnsense.lib.utils import parse_jsonl

from datetime import datetime, UTC


def _parse_size(size: str) -> int:
    ext = {
        'k': 1024,
        'm': 1024**2,
        'g': 1024**3,
    }[size[-1].lower()]
    return int(float(size[:-1]) * ext)


def parse_opnsense_snapshot(string_table: StringTable) -> list:
    section = parse_jsonl(string_table) or []

    return [
        dict(
            name=s['name'],
            created=s['created'],
            current='N' in s['active'],
            reboot='R' in s['active'],
            size=_parse_size(s['size']),
        )
        for s in section
    ]


agent_section_opnsense_snapshot = AgentSection(
    name='opnsense_snapshot',
    parse_function=parse_opnsense_snapshot,
)


def discovery_opnsense_snapshot(
    section: list,
) -> DiscoveryResult:
    if len(section) > 0:
        yield Service()


def check_opnsense_snapshot(
        params: dict,
        section: dict,
) -> CheckResult:
    current = next(s for s in section if s['current'])
    reboot = next(s for s in section if s['reboot'])

    if params.get('running', None) in [None, current['name']]:
        yield Result(state=State.OK, summary=f"Running on {current['name']}")
    else:
        yield Result(state=State.WARN, summary=f"Running on {current['name']} (expected: {params.get('running', None)})")

    if not current['reboot']:
        yield Result(state=State.WARN, summary=f"Next boot: {reboot['name']}")

    inactive = [s for s in section if s['current'] is False and s['reboot'] is False]
    if inactive:
        now = datetime.now(UTC)
        oldest = min(s['created'] for s in inactive)
        yield from check_levels(
            value=int(now.timestamp() - oldest),
            levels_upper=params.get('oldest', None),
            metric_name='oldest',
            render_func=render.timespan,
            label="Oldes snapshot age",
        )

        biggest = max(s['size'] for s in inactive)
        yield from check_levels(
            value=biggest,
            levels_upper=params.get('maxsize', None),
            metric_name='maxsize',
            render_func=render.disksize,
            label="Biggest snapshot",
        )


check_plugin_opnsense_snapshot = CheckPlugin(
    name='opnsense_snapshot',
    service_name='Snapshot',
    discovery_function=discovery_opnsense_snapshot,
    check_function=check_opnsense_snapshot,
    check_default_parameters={},
    check_ruleset_name='opnsense_snapshot',
)
