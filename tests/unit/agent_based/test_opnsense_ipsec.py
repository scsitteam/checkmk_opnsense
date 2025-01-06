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

import pytest  # type: ignore[import]
from cmk.agent_based.v2 import (
    Result,
    Service,
    State,
    Metric,
)
from cmk_addons.plugins.opnsense.agent_based import opnsense_ipsec


def get_value_store():
    return {}


EXAMPLE_IPSEC_SECTION = [
    {"description": "IPSec1", "enabled": "1", "local_addrs": "1.2.3.4", "local_ts": "192.168.100.0/24", "remote_addrs": "5.6.7.8", "remote_ts": "192.168.200.0/24", "uuid": "01234567-89ab-cdef-0123-456789abcdef"}
]

EXAMPLE_IPSEC_PHASE1_SECTION = [
    {
        "phase1desc": "IPSec1", "connected": True, "ikeid": "01234567-89ab-cdef-0123-456789abcdef", "install-time": "42", "name": "01234567-89ab-cdef-0123-456789abcdef",
        "local-addrs": "1.2.3.4", "local-class": "pre-shared key", "local-id": "1.2.3.4",
        "remote-addrs": "5.6.7.8", "remote-class": "pre-shared key", "remote-id": "5.6.7.8",
        "bytes-in": 0, "bytes-out": 0, "packets-in": 0, "packets-out": 0, "routed": True, "version": "IKEv1"
    },
]

EXAMPLE_IPSEC_PHASE2_SECTION = [
    {
        "bytes-in": "0", "bytes-out": "0", "dh-group": "MODP_2048", "encr-alg": "AES_CBC", "encr-keysize": "256", "ikeid": "01234567-89ab-cdef-0123-456789abcdef", "install-time": "42",
        "integ-alg": "HMAC_SHA2_256_128", "life-time": "15767", "local-ts": "192.168.100.0/24", "mode": "TUNNEL", "name": "01234567-89ab-cdef-0123-456789abcdef",
        "packets-in": "0", "packets-out": "0", "phase2desc": "IPSec1 Child", "protocol": "ESP", "rekey-time": "13261",
        "remote-host": "5.6.7.8", "remote-ts": "192.168.200.0/24", "reqid": "1000", "spi-in": "01234567", "spi-out": "89abcdef", "state": "INSTALLED", "uniqueid": "1234"
    }
]


@pytest.mark.parametrize('section_opnsense_ipsec, section_opnsense_ipsec_phase1, section_opnsense_ipsec_phase2, result', [
    (None, None, None, []),
    (
        EXAMPLE_IPSEC_SECTION, EXAMPLE_IPSEC_PHASE1_SECTION, EXAMPLE_IPSEC_PHASE2_SECTION,
        [Service(item='IPSec1', parameters={'discovered': {'version': 'IKEv1', 'phase2': [{'name': 'IPSec1 Child', 'encr_alg': 'AES_CBC', 'integ_alg': 'HMAC_SHA2_256_128', 'protocol': 'ESP'}]}})]
    ),
])
def test_discovery_opnsense_ipsec(section_opnsense_ipsec, section_opnsense_ipsec_phase1, section_opnsense_ipsec_phase2, result):
    assert list(opnsense_ipsec.discovery_opnsense_ipsec(section_opnsense_ipsec, section_opnsense_ipsec_phase1, section_opnsense_ipsec_phase2)) == result


@pytest.mark.parametrize('item, params, section_opnsense_ipsec, section_opnsense_ipsec_phase1, section_opnsense_ipsec_phase2, result', [
    ('IPSec1', {}, [], [], [], []),
    (
        'IPSec1', {'discovered': {'version': 'IKEv1', 'phase2': [{'name': 'IPSec1 Child', 'encr_alg': 'AES_CBC', 'integ_alg': 'HMAC_SHA2_256_128', 'protocol': 'ESP'}]}},
        EXAMPLE_IPSEC_SECTION, EXAMPLE_IPSEC_PHASE1_SECTION, EXAMPLE_IPSEC_PHASE2_SECTION,
        [
            Result(state=State.OK, summary='Phase1: IKEv1'),
            Result(state=State.OK, notice='Install Time: 42 seconds'),
            Metric('install_time', 42.0),
            Result(state=State.OK, notice='IPSec1 Child: ESP HMAC_SHA2_256_128 AES_CBC'),
        ]
    ),
    (
        'IPSec1', {'discovered': {'version': 'IKEv2', 'phase2': [{'name': 'IPSec1 Child', 'encr_alg': 'AES_BCB', 'integ_alg': 'HMAC_SHA2_2_128', 'protocol': 'ESP'}]}},
        EXAMPLE_IPSEC_SECTION, EXAMPLE_IPSEC_PHASE1_SECTION, EXAMPLE_IPSEC_PHASE2_SECTION,
        [
            Result(state=State.WARN, summary='Phase1: IKEv1 (expected: IKEv2)'),
            Result(state=State.OK, notice='Install Time: 42 seconds'),
            Metric('install_time', 42.0),
            Result(state=State.WARN, summary='IPSec1 Child: ESP HMAC_SHA2_256_128 (expected: HMAC_SHA2_2_128) AES_CBC (expected: AES_BCB)'),
        ]
    ),
    (
        'IPSec1', {'discovered': {'version': 'IKEv1', 'phase2': [{'name': 'IPSec1 Child', 'encr_alg': 'AES_CBC', 'integ_alg': 'HMAC_SHA2_256_128', 'protocol': 'ESP'}]}},
        EXAMPLE_IPSEC_SECTION, EXAMPLE_IPSEC_PHASE1_SECTION, [],
        [
            Result(state=State.OK, summary='Phase1: IKEv1'),
            Result(state=State.OK, notice='Install Time: 42 seconds'),
            Metric('install_time', 42.0),
            Result(state=State.WARN, summary='IPSec1 Child: not found'),
        ]
    ),
])
def test_check_opnsense_ipsec(monkeypatch, item, params, section_opnsense_ipsec, section_opnsense_ipsec_phase1, section_opnsense_ipsec_phase2, result):
    monkeypatch.setattr(opnsense_ipsec, 'get_value_store', get_value_store)
    assert list(opnsense_ipsec.check_opnsense_ipsec(item, params, section_opnsense_ipsec, section_opnsense_ipsec_phase1, section_opnsense_ipsec_phase2)) == result
