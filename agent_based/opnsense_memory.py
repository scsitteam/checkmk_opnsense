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

from cmk.agent_based.v2 import AgentSection, StringTable
from cmk.plugins.lib.memory import SectionMemUsed
from cmk_addons.plugins.opnsense.lib.utils import parse_json


def parse_opnsense_memory(string_table: StringTable) -> SectionMemUsed | None:
    section = parse_json(string_table)

    try:
        Cached = int(section['memory']['arc'])
        MemTotal = int(section['memory']['total'])
        MemFree = MemTotal - int(section['memory']['used']) - Cached
        SwapTotal = sum(int(s['total']) for s in section['swap'])
        SwapFree = SwapTotal - sum(int(s['used']) for s in section['swap'])
    except Exception:
        return None

    return SectionMemUsed(
        Cached=Cached,
        MemFree=MemFree,
        MemTotal=MemTotal,
        SwapFree=SwapFree,
        SwapTotal=SwapTotal
    )


agent_section_aix_memory = AgentSection(
    name='opnsense_memory',
    parse_function=parse_opnsense_memory,
    parsed_section_name='mem_used',
)
