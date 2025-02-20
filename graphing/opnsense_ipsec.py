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

from cmk.graphing.v1 import graphs, metrics, perfometers, Title

metric_install_time = metrics.Metric(
    name='install_time',
    title=Title('Install Time'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.BLUE,
)

metric_life_time = metrics.Metric(
    name='life_time',
    title=Title('Life Time'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.LIGHT_YELLOW,
)

metric_rekey_time = metrics.Metric(
    name='rekey_time',
    title=Title('Rekey Time'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.LIGHT_GREEN,
)

quantity_rekey_time = metrics.Sum(Title("Reykey Time"), metrics.Color.GREEN, ['install_time', 'rekey_time'])
quantity_life_time = metrics.Sum(Title("Max Lifetime"), metrics.Color.RED, ['install_time', 'life_time'])

graph_ipsec_child = graphs.Graph(
    name='opnsense_ipsec_child',
    title=Title('Times'),
    compound_lines=['install_time'],
    simple_lines=[
        quantity_rekey_time,
        quantity_life_time,
    ],
)

perfometer_ipsec_child = perfometers.Perfometer(
    name='opnsense_ipsec_child',
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Closed(quantity_life_time),
    ),
    segments=[
        'install_time',
        'rekey_time',
        metrics.Difference(Title("Max Lifetime"), metrics.Color.YELLOW, minuend='life_time', subtrahend='rekey_time'),
    ],
)
