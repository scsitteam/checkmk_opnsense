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
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    LevelsType,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_form_opnsense_firmware():
    return Dictionary(
        elements={
            'last_check': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Last check age'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=TimeSpan(displayed_magnitudes=[TimeMagnitude.DAY, TimeMagnitude.HOUR]),
                    prefill_levels_type=DefaultValue(LevelsType.FIXED),
                    prefill_fixed_levels=InputHint(value=(7 * 24 * 3600, 10 * 24 * 3600)),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_firmware = CheckParameters(
    name='opnsense_firmware',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_firmware,
    title=Title('OPNsense Firmware Update check'),
    help_text=Help('This rule configures thresholds for OPNsense Firmware check.'),
    condition=HostCondition(),
)


def _parameter_form_opnsense_business():
    return Dictionary(
        elements={
            'expiredays': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Expiry in days'),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Integer(
                        unit_symbol='days'
                    ),
                    prefill_levels_type=DefaultValue(LevelsType.FIXED),
                    prefill_fixed_levels=InputHint(value=(60, 30)),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_business = CheckParameters(
    name='opnsense_business',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_business,
    title=Title('OPNsense Businiess License'),
    help_text=Help('This rule configures thresholds for OPNsense license validity.'),
    condition=HostCondition(),
)
