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
from itertools import groupby
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    RuleSetType,
    DiscoveryResult,
    CheckResult,
)
from cmk_addons.plugins.opnsense.lib.utils import parse_json, parse_jsonl, JSONSection, JSONLSection


agent_section_opnsense_carp = AgentSection(
    name='opnsense_carp',
    parse_function=parse_json,
)


agent_section_opnsense_vip = AgentSection(
    name='opnsense_vip',
    parse_function=parse_jsonl,
)


def discovery_opnsense_carp(
    section_opnsense_carp: JSONSection | None,
    section_opnsense_vip: JSONLSection | None
) -> DiscoveryResult:
    if section_opnsense_carp:
        yield Service()


def check_opnsense_carp(
    params: dict,
    section_opnsense_carp: JSONSection | None,
    section_opnsense_vip: JSONLSection | None
) -> CheckResult:
    if not section_opnsense_carp:
        return

    yield Result(state=State.OK, summary=section_opnsense_carp.get('status_msg') or 'OK')
    yield Metric(name='demotion', value=int(section_opnsense_carp.get('demotion')))

    if section_opnsense_carp.get('maintenancemode'):
        yield Result(state=State.WARN, summary='Maintenance Mode is active')

    if section_opnsense_vip or True:
        master = 0
        backup = 0
        for vip in section_opnsense_vip:
            if vip['mode'] != 'carp':
                continue
            if vip['status'] == 'MASTER':
                master += 1
            else:
                backup += 1
        yield from check_levels(
            value=master,
            levels_lower=params.get('master_levels_lower', None),
            levels_upper=params.get('master_levels_upper', None),
            metric_name='carp_master',
            render_func=int.__str__,
            label='Master',
            boundaries=(0, master + backup),
            notice_only=master == 0
        )
        yield from check_levels(
            value=backup,
            levels_lower=params.get('backup_levels_lower', None),
            levels_upper=params.get('backup_levels_upper', None),
            metric_name='carp_backup',
            render_func=int.__str__,
            label='Backup',
            boundaries=(0, master + backup),
            notice_only=backup == 0
        )


check_plugin_opnsense_carp = CheckPlugin(
    name='opnsense_carp',
    sections=['opnsense_carp', 'opnsense_vip'],
    service_name='CARP',
    discovery_function=discovery_opnsense_carp,
    check_function=check_opnsense_carp,
    check_default_parameters={},
    check_ruleset_name='opnsense_carp',
)


def discovery_opnsense_vip(params, section: JSONLSection):
    if params.get('discover', 'none') == 'none':
        return

    if params.get('discover', 'none') == 'master':
        section = [
            vip
            for vip in section
            if vip['status'] == 'MASTER'
        ]

    if params.get('groupby', 'none') == 'interface':
        section = sorted(section, key=lambda i: i['interface'])
        for interface, vips in groupby(section, lambda i: i['interface']):
            yield Service(item=f"{interface}", parameters=dict(interface=interface, discovery_status={v['vhid']: v['status'] for v in vips}))
        return

    for vip in section:
        yield Service(item=f"{vip['interface']}@{vip['vhid']}", parameters=dict(interface=vip['interface'], vhid=vip['vhid'], discovery_status=vip['status']))


def check_opnsense_vip(item, params, section: JSONLSection):
    for vip in section:
        if vip['interface'] != params['interface']:
            continue
        if 'vhid' in params and vip['vhid'] != params['vhid']:
            continue

        expected_status = params.get('discovery_status')
        if 'expected_status' in params:
            expected_status = params.get('expected_status')
        elif 'vhid' not in params:
            expected_status = expected_status.get(vip['vhid'])

        if vip['status'] == expected_status:
            yield Result(state=State.OK, summary=f"{vip['status']}: {vip['subnet']}")
        else:
            yield Result(state=State.WARN, summary=f"{vip['status']}: {vip['subnet']} (expected: {expected_status})")


check_plugin_opnsense_vip = CheckPlugin(
    name='opnsense_vip',
    service_name='VirtualIP %s',
    discovery_function=discovery_opnsense_vip,
    discovery_default_parameters={'discover': 'none'},
    discovery_ruleset_name='discovery_opnsense_vip',
    discovery_ruleset_type=RuleSetType.MERGED,
    check_function=check_opnsense_vip,
    check_default_parameters={},
    check_ruleset_name='opnsense_vip',
)
