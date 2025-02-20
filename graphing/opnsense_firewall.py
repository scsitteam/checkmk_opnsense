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

from cmk.graphing.v1 import metrics, perfometers, Title

metric_pf_states = metrics.Metric(
    name='pf_states',
    title=Title('PF States'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.GREEN,
)

metric_aliases = metrics.Metric(
    name='aliases',
    title=Title('Aliases'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.ORANGE,
)

perfometer_firewall = perfometers.Stacked(
    name='opnsense_firewall',
    upper=perfometers.Perfometer(
        name='pf_states',
        focus_range=perfometers.FocusRange(
            perfometers.Closed(0),
            perfometers.Open(metrics.MaximumOf('pf_states', color=metrics.Color.GREEN)),
        ),
        segments=['pf_states'],
    ),
    lower=perfometers.Perfometer(
        name='aliases',
        focus_range=perfometers.FocusRange(
            perfometers.Closed(0),
            perfometers.Open(metrics.MaximumOf('aliases', color=metrics.Color.ORANGE)),
        ),
        segments=['aliases'],
    ),
)
