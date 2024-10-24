#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json

from cmk.agent_based.v2 import AgentSection, StringTable
from cmk.plugins.lib import interfaces


def parse_opnsense_interfaces_statistics(statistics: dict) -> interfaces.Counters:
    return interfaces.Counters(
        in_octets=statistics.get('bytes received', None),
        in_ucast=statistics.get('packets received', None),
        in_err=statistics.get('input errors', None),
        out_octets=statistics.get('bytes transmitted', None),
        out_ucast=statistics.get('packets transmitted', None),
        out_err=statistics.get('output errors', None),
    )


def parse_opnsense_interfaces_type(type: str) -> str:
    types = [
    	"reserved",
        "other",
        "BBN 1822",
        "HDH 1822",
        "X.25 DDN",
        "X.25",
        "Ethernet",
        "ISO 8802-3 CSMA/CD",
        "ISO 8802-4 Token Bus",
        "ISO 8802-5 Token Ring",
        "ISO 8802-6 DQDB MAN",
        "StarLAN",
        "Proteon proNET-10",
        "Proteon proNET-80",
        "HyperChannel",
        "FDDI",
        "LAP-B",
        "SDLC",
        "T-1",
        "CEPT",
        "Basic rate ISDN",
        "Primary rate ISDN",
        "Proprietary P2P",
        "PPP",
        "Loopback",
        "ISO CLNP over IP",
        "Experimental Ethernet",
        "XNS over IP",
        "SLIP",
        "Ultra Technologies",
        "DS-3",
        "SMDS",
        "Frame Relay",
        "RS-232 serial",
        "Parallel printer port",
        "ARCNET",
        "ARCNET+",
        "ATM",
        "MIOX25",
        "SONET/SDH",
        "X25PLE",
        "ISO 8802-2 LLC",
        "LocalTalk",
        "SMDSDXI",
        "Frame Relay DCE",
        "V.35",
        "HSSI",
        "HIPPI",
        "Generic Modem",
        "ATM AAL5",
        "SONETPATH",
        "SONETVT",
        "SMDS InterCarrier Interface",
        "Proprietary virtual interface",
        "Proprietary multiplexing",
        "Generic tunnel interface",
        "IPv6-to-IPv4 TCP relay capturing interface",
        "6to4 tunnel interface"
    ]
    if type in types:
        return str(types.index(type))
    elif type.startswith('unknown type'):
        return type[13:]
    else:
        return "1"


def parse_opnsense_interfaces(
    string_table: StringTable,
) -> interfaces.Section[interfaces.InterfaceWithCounters]:
    ifaces = {}
    index = 0

    for line in string_table:
        line = json.loads(line[0])
        nic = line['description']
        index += 1


        ifaces[nic] = interfaces.InterfaceWithCounters(
            interfaces.Attributes(
                index=str(line['statistics']['index']),
                descr=nic,
                alias=nic,
                speed=int(line['statistics']['line rate'].split(' ')[0]),
                type=parse_opnsense_interfaces_type(line['statistics']['type'])
            ),
            parse_opnsense_interfaces_statistics(line['statistics'])
        )

    return ifaces


agent_section_opnsense_interfaces = AgentSection(
    name="opnsense_interfaces",
    parse_function=parse_opnsense_interfaces,
    parsed_section_name="interfaces",
)
