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
    get_rate,
    get_value_store,
    render,
    Result,
    Service,
    State,
    StringTable,
)
from cmk_addons.plugins.opnsense.lib.utils import parse_jsonl, JSONSection, JSONLSection


agent_section_opnsense_ipsec = AgentSection(
    name='opnsense_ipsec',
    parse_function=parse_jsonl,
)

agent_section_opnsense_ipsec_phase1 = AgentSection(
    name='opnsense_ipsec_phase1',
    parse_function=parse_jsonl,
)


def parse_opnsense_ipsec_phase2(string_table: StringTable) -> JSONLSection:
    return [
        phase2
        for phase2 in parse_jsonl(string_table)
        if phase2['state'] == 'INSTALLED'
    ]


agent_section_opnsense_ipsec_phase2 = AgentSection(
    name='opnsense_ipsec_phase2',
    parse_function=parse_opnsense_ipsec_phase2,
)


def discovery_opnsense_ipsec(
    section_opnsense_ipsec: JSONSection | None,
    section_opnsense_ipsec_phase1: JSONLSection | None,
    section_opnsense_ipsec_phase2: JSONLSection | None,
) -> DiscoveryResult:
    for conn in section_opnsense_ipsec or []:
        params = {}
        for phase1 in section_opnsense_ipsec_phase1:
            if phase1['name'] == conn['uuid']:
                params['version'] = phase1['version']
                break
        params['phase2'] = [
            {
                'name': phase2['phase2desc'],
                'encr_alg': phase2['encr-alg'],
                'integ_alg': phase2.get('integ-alg', None),
                'protocol': phase2['protocol'],
            }
            for phase2 in section_opnsense_ipsec_phase2
            if phase2['ikeid'] == conn['uuid']
        ]
        yield Service(item=conn['description'], parameters=dict(discovered=params))


def check_opnsense_ipsec(
    item: str,
    params: dict,
    section_opnsense_ipsec: JSONSection | None,
    section_opnsense_ipsec_phase1: JSONLSection | None,
    section_opnsense_ipsec_phase2: JSONLSection | None,
) -> CheckResult:

    for conn in section_opnsense_ipsec:
        if conn['description'] == item:
            break
    else:
        return

    for phase1 in section_opnsense_ipsec_phase1:
        if phase1['name'] == conn['uuid']:
            break
    else:
        yield Result(state=State.UNKNOWN, summary='Phase1 not found')
        return

    if not phase1['connected']:
        yield Result(state=State.CRIT, summary='Phase1 not connected')
        return

    discovered = params['discovered']

    # Check Phase 1
    expected_version = params.get('version', 'discovered')
    if expected_version == 'discovered':
        expected_version = discovered.get('version', None)
    if expected_version and expected_version != phase1['version']:
        yield Result(state=State.WARN, summary=f"{phase1['version']} (expected: {expected_version})")
    else:
        yield Result(state=State.OK, summary=f"{phase1['version']}")

    try:
        yield from check_levels(
            value=float(phase1['install-time']),
            metric_name='install_time',
            render_func=render.timespan,
            label='Install Time',
            notice_only=True
        )
    except Exception:
        pass

    value_store = get_value_store()
    for key in ['in', 'out']:
        try:
            value = get_rate(value_store, f"check_opnsense_ipsec.{conn['uuid']}.if_{key}_bps", time.time(), int(phase1[f"bytes-{key}"]) * 8, raise_overflow=True)
            yield from check_levels(
                value=value,
                metric_name=f"if_{key}_bps",
                boundaries=(0, None),
                label=f"Bandwith {key}",
                notice_only=True,
            )
        except Exception:
            pass

        try:
            value = get_rate(value_store, f"check_opnsense_ipsec.{conn['uuid']}.if_{key}_pkts", time.time(), int(phase1[f"packets-{key}"]), raise_overflow=True)
            yield from check_levels(
                value=value,
                metric_name=f"if_{key}_pkts",
                boundaries=(0, None),
                label=f"Packets {key}",
                notice_only=True,
            )
        except Exception:
            pass

    # Check Phase 2
    section_opnsense_ipsec_phase2 = [
        phase2
        for phase2 in section_opnsense_ipsec_phase2
        if phase2['ikeid'] == conn['uuid']
    ]

    yield from check_levels(
        value=len(section_opnsense_ipsec_phase2),
        metric_name='childs',
        render_func=str,
        boundaries=(0, None),
        label='Childs',
        notice_only=True
    )

    for dphase2 in discovered['phase2']:
        for phase2 in section_opnsense_ipsec_phase2 or []:
            if phase2['ikeid'] != conn['uuid']:
                continue

            if dphase2['name'] == phase2['phase2desc']:
                state = State.OK
                notice = [f"{dphase2['name']}:"]
                if dphase2['protocol'] == phase2['protocol']:
                    notice.append(phase2['protocol'])
                else:
                    notice.append(f"{phase2['protocol']} (expected: {dphase2['protocol']})")
                    state = State.WARN

                if dphase2['integ_alg']:
                    if dphase2['integ_alg'] == phase2.get('integ-alg', None):
                        notice.append(phase2.get('integ-alg', None))
                    else:
                        notice.append(f"{phase2.get('integ-alg', None)} (expected: {dphase2['integ_alg']})")
                        state = State.WARN

                if dphase2['encr_alg'] == phase2['encr-alg']:
                    notice.append(phase2['encr-alg'])
                else:
                    notice.append(f"{phase2['encr-alg']} (expected: {dphase2['encr_alg']})")
                    state = State.WARN

                yield Result(state=state, notice=' '.join(notice))
                break
        else:
            yield Result(state=State.WARN, summary=f"{dphase2['name']}: not found")

    if section_opnsense_ipsec_phase2:
        for phase2 in section_opnsense_ipsec_phase2:
            if phase2['ikeid'] != conn['uuid']:
                continue

            for dphase2 in discovered['phase2']:
                if dphase2['name'] == phase2['phase2desc']:
                    break
            else:
                yield Result(state=State.WARN, summary=f"{phase2['phase2desc']}: Unexpected Connection")


check_plugin_opnsense_ipsec = CheckPlugin(
    name='opnsense_ipsec',
    sections=['opnsense_ipsec', 'opnsense_ipsec_phase1', 'opnsense_ipsec_phase2'],
    service_name='IPSec %s',
    discovery_function=discovery_opnsense_ipsec,
    check_function=check_opnsense_ipsec,
    check_default_parameters={'version': 'discovered'},
    check_ruleset_name='opnsense_ipsec',
)


def discovery_opnsense_ipsec_child(
    section_opnsense_ipsec: JSONSection | None,
    section_opnsense_ipsec_phase2: JSONLSection | None,
) -> DiscoveryResult:
    for child in section_opnsense_ipsec_phase2:
        if child['state'] != 'INSTALLED':
            continue

        for conn in section_opnsense_ipsec:
            if child['ikeid'] == conn['uuid']:
                break
        else:
            continue

        yield Service(item=f"{conn['description']} {child['local-ts']} > {child['remote-ts']}")


def render_timespan(seconds: float) -> str:
    return f"{render.timespan(-seconds)} ago" if seconds < 0 else render.timespan(seconds)


def check_opnsense_ipsec_child(
    item: str,
    section_opnsense_ipsec: JSONSection | None,
    section_opnsense_ipsec_phase2: JSONLSection | None,
) -> CheckResult:
    for child in section_opnsense_ipsec_phase2:
        for conn in section_opnsense_ipsec:
            if child['ikeid'] == conn['uuid']:
                break
        else:
            continue

        if child['state'] != 'INSTALLED' or item != f"{conn['description']} {child['local-ts']} > {child['remote-ts']}":
            continue

        yield Result(state=State.OK, summary=f"{child['protocol']}")
        yield Result(state=State.OK, summary=f"E:{child['encr-alg']}:{child['encr-keysize']}")
        if 'integ-alg' in child:
            yield Result(state=State.OK, summary=f"I:{child['integ-alg']}")
        if 'dh-group' in child:
            yield Result(state=State.OK, summary=f"D:{child['dh-group']}")

        yield from check_levels(
            value=float(child['install-time']),
            metric_name='install_time',
            render_func=render.timespan,
            label='Install Time',
            notice_only=True
        )

        yield from check_levels(
            value=float(child['rekey-time']),
            metric_name='rekey_time',
            render_func=render_timespan,
            label='Rekey Time',
            notice_only=True
        )

        yield from check_levels(
            value=float(child['life-time']),
            metric_name='life_time',
            render_func=render_timespan,
            label='Life Time',
            notice_only=True
        )


check_plugin_opnsense_ipsec_child = CheckPlugin(
    name='opnsense_ipsec_child',
    sections=['opnsense_ipsec', 'opnsense_ipsec_phase2'],
    service_name='IPSec %s',
    discovery_function=discovery_opnsense_ipsec_child,
    check_function=check_opnsense_ipsec_child,
)
