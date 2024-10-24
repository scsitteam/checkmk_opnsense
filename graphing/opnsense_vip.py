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

from cmk.graphing.v1 import graphs, metrics, perfometers, translations, Title

metric_carp_master = metrics.Metric(
    name='carp_master',
    title=Title('Master'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.GREEN,
)
metric_carp_backup = metrics.Metric(
    name='carp_backup',
    title=Title('Backup'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.ORANGE,
)

graph_carp = graphs.Graph(
    name='opnsense_carp',
    title=Title('CARP States'),
    compound_lines=['carp_master', 'carp_backup'],
)

perfometer_carp = perfometers.Perfometer(
    name='opnsense_carp',
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open('carp_master'),
    ),
    segments=['carp_master', 'carp_backup'],
)
