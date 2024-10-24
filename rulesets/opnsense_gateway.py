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
    Dictionary,
    DictElement,
    SimpleLevels,
    LevelDirection,
    InputHint,
    DefaultValue,
    LevelsType,
    TimeSpan,
    TimeMagnitude,
    Percentage,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_form_opnsense_gateway():
    return Dictionary(
        elements={
            'rtt': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Round trip time'),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[TimeMagnitude.MILLISECOND],
                    ),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(0.1, 0.2)),
                ),
                required=False,
            ),
            'lost': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Packet loss'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Percentage(),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(10, 20)),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_gateway = CheckParameters(
    name='opnsense_gateway',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_gateway,
    title=Title('OPNsense Gateway Status'),
    help_text=Help('This rule configures thresholds for OPNsense Gateway status.'),
    condition=HostCondition(),
)
