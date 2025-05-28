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

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DataSize,
    DefaultValue,
    DictElement,
    Dictionary,
    IECMagnitude,
    InputHint,
    LevelDirection,
    LevelsType,
    SimpleLevels,
    String,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_form_opnsense_snapshot():
    return Dictionary(
        elements={
            'running': DictElement(
                parameter_form=String(
                    title=Title('Name of the active snapshot'),
                ),
                required=False,
            ),
            'oldest': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Age of the oldest (inactive) snapshot'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[TimeMagnitude.DAY, TimeMagnitude.HOUR, TimeMagnitude.MINUTE],
                    ),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(86400 * 7, 86400 * 14)),
                ),
                required=False,
            ),
            'maxsize': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Size of the biggest (inactive) snapshot'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=DataSize(
                        displayed_magnitudes=IECMagnitude,
                    ),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(0.5 * 1024**3, 1024**3)),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_snapshot = CheckParameters(
    name='opnsense_snapshot',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_snapshot,
    title=Title('OPNsense Snapshot Status'),
    help_text=Help('This rule configures thresholds for OPNsense Snapshot status.'),
    condition=HostCondition(),
)
