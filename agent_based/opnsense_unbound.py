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

import time

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
    Result,
    State,
    get_rate,
    get_value_store,
    render,
)
from cmk_addons.plugins.opnsense.lib.utils import parse_json, JSONSection


agent_section_opnsense_unbound = AgentSection(
    name='opnsense_unbound',
    parse_function=parse_json,
)


def discovery_opnsense_unbound(section: JSONSection) -> DiscoveryResult:
    if section:
        yield Service()


def check_opnsense_unbound(
        params: dict,
        section: JSONSection,
) -> CheckResult:

    if section.get('status') == 'ok':
        yield Result(state=State.OK, summary=f"Status {section.get('status')}")
    else:
        yield Result(state=State.WARN, summary=f"Status {section.get('status')}")

    value_store = get_value_store()
    now = float(section.get('time', {}).get('now', time.time()))

    for i in ['queries', 'cachehits', 'cachemiss', 'recursivereplies']:
        try:
            value = get_rate(value_store, f"opnsense_unbound.total_{i}", now, int(section['data']['total']['num'][i]), raise_overflow=True)
            yield from check_levels(
                value=value,
                metric_name=f"total_{i}",
                render_func=lambda v: "%.1f/s" % v,
                label=i.title(),
            )
        except Exception:
            pass

    yield from check_levels(
        value=float(section['data']['total']['recursion']['time']['avg']),
        metric_name="recursion_time_avg",
        render_func=render.timespan,
        label='Average Recursion Time',
        notice_only=True,
    )

    yield from check_levels(
        value=float(section['data']['total']['recursion']['time']['median']),
        metric_name="recursion_time_median",
        render_func=render.timespan,
        label='Median Recursion Time',
        notice_only=True,
    )

    # Query Type
    for qtype, count in section['data']['num']['query']['type'].items():
        try:
            value = get_rate(value_store, f"opnsense_unbound.query_type_{qtype}".lower(), now, int(count), raise_overflow=True)
            yield from check_levels(
                value=value,
                metric_name=f"query_type_{qtype}".lower(),
                render_func=lambda v: "%.1f/s" % v,
                label=f"Query Type {qtype}",
                notice_only=True,
            )
        except Exception:
            pass

    # Rcode
    for rcode, count in section['data']['num']['answer']['rcode'].items():
        try:
            value = get_rate(value_store, f"opnsense_unbound.rcode_{rcode}".lower(), now, int(count), raise_overflow=True)
            yield from check_levels(
                value=value,
                metric_name=f"rcode_{rcode}".lower(),
                render_func=lambda v: "%.1f/s" % v,
                label=f"Answer RCode: {rcode}",
                notice_only=True,
            )
        except Exception:
            pass

    # Cache Count
    for i in ['msg', 'rrset', 'infra', 'key']:
        yield from check_levels(
            value=int(section['data'][i]['cache']['count']),
            metric_name=f"{i}_cache_count",
            render_func=str,
            label=f"Cache Count {i.title()}",
            notice_only=True,
        )


check_plugin_opnsense_unbound = CheckPlugin(
    name='opnsense_unbound',
    service_name='OPNsense Unbound',
    discovery_function=discovery_opnsense_unbound,
    check_function=check_opnsense_unbound,
    check_default_parameters={},
    check_ruleset_name='opnsense_unbound',
)
