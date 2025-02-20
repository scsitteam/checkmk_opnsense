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
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition


def _parameter_form_opnsense_firewall():
    return Dictionary(
        elements={
            'pf_states': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('PF States'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    prefill_levels_type=DefaultValue(LevelsType.FIXED),
                    prefill_fixed_levels=InputHint(value=(1000, 2000)),
                ),
                required=False,
            ),
            'aliases': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Aliases'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    prefill_levels_type=DefaultValue(LevelsType.FIXED),
                    prefill_fixed_levels=InputHint(value=(10000, 20000)),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_firewall = CheckParameters(
    name='opnsense_firewall',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_firewall,
    title=Title('OPNsense Firewall check'),
    help_text=Help('This rule configures thresholds for OPNsense Firewall check.'),
    condition=HostCondition(),
)
