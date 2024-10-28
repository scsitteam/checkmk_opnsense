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

from datetime import datetime
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
    Metric,
)
from cmk_addons.plugins.opnsense.lib.utils import parse_json, JSONSection


agent_section_opnsense_firmware = AgentSection(
    name='opnsense_firmware',
    parse_function=parse_json,
)


def discovery_opnsense_firmware(section: JSONSection | None) -> DiscoveryResult:
    if section:
        yield Service()


def check_opnsense_firmware(params: dict, section: JSONSection) -> CheckResult:
    yield Result(state=State.OK, summary=f"{section['product']['product_series']} ({section['product']['product_nickname']})")

    if 'last_check' not in section:
        yield Result(state=State.OK, summary=section['status_msg'])
        return

    last_check = datetime.strptime(section['last_check'], "%a %b %d %X %Z %Y")
    last_check_age = (datetime.now() - last_check).seconds
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


check_plugin_opnsense_firmware = CheckPlugin(
    name='opnsense_firmware',
    service_name='OPNsense Firmware',
    discovery_function=discovery_opnsense_firmware,
    check_function=check_opnsense_firmware,
    check_default_parameters={},
    check_ruleset_name='opnsense_firmware',
)


def discovery_opnsense_business(section: JSONSection) -> DiscoveryResult:
    if section and section.get('product_id', None) == 'opnsense-business':
        yield Service()


def check_opnsense_business(params: dict, section: JSONSection) -> CheckResult:
    valid_to = datetime.fromisoformat(section['product']['product_license']['valid_to'])
    valid_to_days = (valid_to - datetime.now()).days
    yield from check_levels(
        value=valid_to_days,
        levels_lower=params.get('expiredays', ('fixed', (60, 30))),
        metric_name='expiredays',
        render_func=lambda x: f"{x} days",
        label='License expires in',
    )


check_plugin_opnsense_business = CheckPlugin(
    name='opnsense_business',
    sections=['opnsense_firmware'],
    service_name='OPNsense Business',
    discovery_function=discovery_opnsense_business,
    check_function=check_opnsense_business,
    check_default_parameters={},
    check_ruleset_name='opnsense_business',
)
