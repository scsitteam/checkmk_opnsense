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
    Service,
)
from cmk_addons.plugins.opnsense.lib.utils import parse_json, JSONSection


agent_section_opnsense_pf_states = AgentSection(
    name='opnsense_pf_states',
    parse_function=parse_json,
)


agent_section_opnsense_alias_table = AgentSection(
    name='opnsense_alias_table',
    parse_function=parse_json,
)


def discovery_opnsense_firewall(
        section_opnsense_pf_states: JSONSection | None,
        section_opnsense_alias_table: JSONSection | None,
) -> DiscoveryResult:
    if section_opnsense_pf_states or section_opnsense_alias_table:
        yield Service()


def check_opnsense_firewall(
        params: dict,
        section_opnsense_pf_states: JSONSection | None,
        section_opnsense_alias_table: JSONSection | None,
) -> CheckResult:

    yield from check_levels(
        value=int(section_opnsense_pf_states['current']),
        levels_upper=params.get('pf_states', None),
        metric_name='pf_states',
        render_func=int,
        label='PF States',
        boundaries=(0, int(section_opnsense_pf_states['limit'])),
    )

    yield from check_levels(
        value=int(section_opnsense_alias_table['used']),
        levels_upper=params.get('aliases', None),
        metric_name='aliases',
        render_func=int,
        label='Aliases',
        boundaries=(0, int(section_opnsense_alias_table['size'])),
    )


check_plugin_opnsense_firewall = CheckPlugin(
    name='opnsense_firewall',
    service_name='OPNsense Firewall',
    sections=['opnsense_pf_states', 'opnsense_alias_table'],
    discovery_function=discovery_opnsense_firewall,
    check_function=check_opnsense_firewall,
    check_default_parameters={},
    check_ruleset_name='opnsense_firmware',
)
