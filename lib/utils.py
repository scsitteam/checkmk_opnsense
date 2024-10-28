# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_opnsense - Checkmk Extension for monitoring OpnSense.
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
from typing import Any

from cmk.agent_based.v2 import StringTable

JSONSection = dict[str, Any] | None
JSONLSection = list[dict[str, Any]] | None


def parse_json(string_table: StringTable) -> JSONSection:
    if string_table:
        return json.loads(string_table[0][0])
    return None


def parse_jsonl(string_table: StringTable) -> JSONLSection:
    if string_table:
        return [
            json.loads(line[0])
            for line in string_table
        ]
    return None
