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

import dateutil
from datetime import datetime, UTC
from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    HostLabel,
    HostLabelGenerator,
    Metric,
    render,
    Result,
    Service,
    State,
    StringTable,
)
from cmk.plugins.lib import uptime
from cmk.plugins.lib import cpu
from cmk_addons.plugins.opnsense.lib.utils import parse_json, JSONSection, parse_date


def host_labels_opnsense(section: JSONSection) -> HostLabelGenerator:
    yield HostLabel("cmk/os_family", "freebsd")
    yield HostLabel("cmk/os_name", f"{section['product']['product_name']} {section['product']['product_series']}")
    yield HostLabel("cmk/os_platform", section['product_id'])
    yield HostLabel("cmk/os_version", section['product_version'])


agent_section_opnsense_system = AgentSection(
    name='opnsense_system',
    parse_function=parse_json,
    host_label_function=host_labels_opnsense
)


def discovery_opnsense_system(section: JSONSection | None) -> DiscoveryResult:
    if section:
        yield Service()


def check_opnsense_system(params: dict, section: JSONSection) -> CheckResult:
    if section and section.get('product_id', None) == 'opnsense-business':
        yield Result(state=State.OK, summary='Business')

    yield Result(state=State.OK, summary=f"{section['product']['product_series']} ({section['product']['product_nickname']})")

    if 'last_check' not in section:
        yield Result(state=State.OK, summary=section['status_msg'])
        return

    last_check = parse_date(section['last_check'])
    last_check_age = (datetime.now(UTC) - last_check).seconds
    yield from check_levels(
        value=last_check_age,
        levels_upper=params.get('last_check', None),
        metric_name='last_check',
        render_func=render.timespan,
        label='Last update check',
        notice_only=True
    )

    if section['status'] == 'update':
        yield Result(state=State.OK, summary=section['status_msg'])
    yield Metric(name='updates', value=len(section['product']['product_check']['upgrade_packages']))

    if section and section.get('product_id', None) == 'opnsense-business':
        valid_to = datetime.fromisoformat(section['product']['product_license']['valid_to'])
        valid_to_days = (valid_to - datetime.now()).days
        yield from check_levels(
            value=valid_to_days,
            levels_lower=params.get('expiredays', ('fixed', (60, 30))),
            metric_name='expiredays',
            render_func=lambda x: f"{x} {'days' if x > 1 else 'day'}",
            label='License expires in',
            notice_only=True
        )


check_plugin_opnsense_system = CheckPlugin(
    name='opnsense_system',
    service_name='OPNsense',
    discovery_function=discovery_opnsense_system,
    check_function=check_opnsense_system,
    check_default_parameters={},
    check_ruleset_name='opnsense_system',
)


def parse_opnsense_uptime(string_table: StringTable) -> uptime.Section:
    section = parse_json(string_table)
    uptime_delta = dateutil.parser.parse(section['datetime']) - dateutil.parser.parse(section['boottime'])
    return uptime.Section(uptime_sec=uptime_delta.total_seconds(), message=None)


agent_section_opnsense_uptime = AgentSection(
    name='opnsense_uptime',
    parse_function=parse_opnsense_uptime,
    parsed_section_name='uptime'
)


def parse_opnsense_load(string_table: StringTable) -> uptime.Section:
    section = string_table[0][0].split(', ')
    return cpu.Section(
        load=cpu.Load(float(section[0]), float(section[1]), float(section[2])),
        num_cpus=1,
    )


agent_section_opnsense_load = AgentSection(
    name='opnsense_load',
    parse_function=parse_opnsense_load,
    parsed_section_name='cpu'
)
