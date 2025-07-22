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

from cmk.graphing.v1 import metrics, perfometers, Title, translations

translation_opnsense_snapshot = translations.Translation(
    name='opnsense_snapshot',
    check_commands=[translations.PassiveCheck('opnsense_snapshot')],
    translations={
        'oldest': translations.RenameTo('opnsense_snapshot_oldest'),
        'maxsize': translations.RenameTo('opnsense_snapshot_maxsize'),
    },
)

metric_snapshot_oldest = metrics.Metric(
    name='opnsense_snapshot_oldest',
    title=Title('Age of oldest Snapshot'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.GREEN,
)

metric_snapshot_maxsize = metrics.Metric(
    name='opnsense_snapshot_maxsize',
    title=Title('Size of bigest Snapshot'),
    unit=metrics.Unit(metrics.IECNotation("B")),
    color=metrics.Color.BLUE,
)

perfometer_opnsense_snapshot = perfometers.Stacked(
    name='opnsense_snapshot',
    lower=perfometers.Perfometer(
        name='opnsense_snapshot_oldest',
        focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(metrics.CriticalOf(metric_name='opnsense_snapshot_oldest'))),
        segments=['opnsense_snapshot_oldest'],
    ),
    upper=perfometers.Perfometer(
        name='opnsense_snapshot_maxsize',
        focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(metrics.CriticalOf(metric_name='opnsense_snapshot_maxsize'))),
        segments=['opnsense_snapshot_maxsize'],
    ),
)
