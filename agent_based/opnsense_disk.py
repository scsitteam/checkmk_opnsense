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
from cmk.plugins.lib.df import DfBlock
from cmk_addons.plugins.opnsense.lib.utils import parse_json


def _parse_size_to_mb(size: str) -> int:
    ext = {
        'k': 1 / 1024,
        'm': 1,
        'g': 1024,
        't': 1024**2,
        'p': 1024**3,
    }[size[-1].lower()]
    return int(float(size[:-1]) * ext)


def parse_opnsense_disk(string_table: StringTable) -> list:
    section = parse_json(string_table) or {}

    return [
        DfBlock(
            device=d['device'],
            fs_type=d['type'],
            size_mb=_parse_size_to_mb(d['blocks']),
            avail_mb=_parse_size_to_mb(d['blocks']) - _parse_size_to_mb(d['used']),
            reserved_mb=0.0,
            mountpoint=d['mountpoint'],
            uuid=None,
        )
        for d in section.get('devices', [])
    ], []


agent_section_opnsense_snapshot = AgentSection(
    name='opnsense_disk',
    parse_function=parse_opnsense_disk,
    parsed_section_name='df',
)
