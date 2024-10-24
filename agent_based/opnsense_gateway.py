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

import json
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
)


_Section = list[dict]


def _parse_time(v: str) -> float:
    if v == '~':
        return None

    parts = v.split()
    if parts[1] == "ms":
        return float(parts[0]) / 1000.0
    return float(parts[0])


def parse_opnsense_gateway(string_table):
    section = [
        json.loads(line[0])
        for line in string_table
    ]
    for gw in section:
        if gw['loss'] == '~':
            gw['loss'] = None
        else:
            gw['loss'] = float(gw['loss'][:-2])
        gw['delay'] = _parse_time(gw['delay'])
        gw['stddev'] = _parse_time(gw['stddev'])
        if gw['monitor'] == '~':
            gw['monitor'] = None

    return {
        gw['name']: gw
        for gw in section
    }


agent_section_opnsense_gateway = AgentSection(
    name='opnsense_gateway',
    parse_function=parse_opnsense_gateway,
)


def discovery_opnsense_gateway(
    section: _Section,
) -> DiscoveryResult:
    for gw in section.values():
        if gw['delay'] is None:
            continue
        yield Service(item=gw['name'])


def check_opnsense_gateway(
        item: str,
        params: dict,
        section: _Section,
) -> CheckResult:
    if item not in section:
        return

    gw = section.get(item)

    if gw['status_translated'] == params.get('status', 'Online'):
        yield Result(state=State.OK, summary=gw['status_translated'])
    else:
        yield Result(state=State.WARN, summary=f"{gw['status_translated']} (expected: {params.get('status', 'Online')})")

    if gw['delay']:
        yield Result(state=State.OK, summary=f"Monitor {gw['monitor']}")
        yield from check_levels(
            value=gw['delay'],
            levels_upper=params.get('delay', ('fixed', (0.1, 0.2))),
            metric_name='rta',
            render_func=render.timespan,
            label="rtt",
        )
        yield from check_levels(
            value=gw['loss'],
            levels_upper=params.get('loss', ('fixed', (10, 20))),
            metric_name='pl',
            render_func=render.percent,
            label="loss",
        )


check_plugin_opnsense_gateway = CheckPlugin(
    name='opnsense_gateway',
    service_name='GW',
    discovery_function=discovery_opnsense_gateway,
    check_function=check_opnsense_gateway,
    check_default_parameters={},
    check_ruleset_name='opnsense_gateway',
)
