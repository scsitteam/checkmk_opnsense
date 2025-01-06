#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_opnsense - Checkmk extension for OPNsense
#
# Copyright (C) 2024-2025  Marius Rieder <marius.rieder@scs.ch>
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
    List,
    SimpleLevels,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition, DiscoveryParameters


def _parameter_form_opnsense_carp():
    return Dictionary(
        elements={
            'master_levels_lower': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Master lower'),
                    help_text=Help('Lower Thresholds for Master states.'),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Integer(),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
                required=False,
            ),
            'master_levels_upper': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Master upper'),
                    help_text=Help('Upper Thresholds for Master states.'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
                required=False,
            ),
            'backup_levels_lower': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Backup lower'),
                    help_text=Help('Lower Thresholds for Backup states.'),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Integer(),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
                required=False,
            ),
            'backup_levels_upper': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Backup upper'),
                    help_text=Help('Upper Thresholds for Backup states.'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(),
                    prefill_levels_type=DefaultValue(LevelsType.NONE),
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_carp = CheckParameters(
    name='opnsense_carp',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_carp,
    title=Title('OPNsense CARP Status'),
    help_text=Help('This rule configures thresholds for OPNsense CARP status.'),
    condition=HostCondition(),
)


def _parameter_form_opnsense_vip():
    return Dictionary(
        elements={
            'expected_status': DictElement(
                parameter_form=SingleChoice(
                    title=Title('VirtualIP Status'),
                    help_text=Help('Expect the status of the VirtualIP to be in this state.'),
                    elements=[
                        SingleChoiceElement(name='MASTER', title=Title('MASTER')),
                        SingleChoiceElement(name='BACKUP', title=Title('BACKUP')),
                    ],
                    prefill=DefaultValue('MASTER'),
                ),
                required=False,
            ),
            'interface': DictElement(
                parameter_form=String(
                    title=Title('Interface'),
                ),
                required=False,
                render_only=True,
            ),
            'vhid': DictElement(
                parameter_form=String(
                    title=Title('VHID'),
                ),
                required=False,
                render_only=True,
            ),
            'discovery_status': DictElement(
                parameter_form=List(
                    element_template=Dictionary(
                        elements={
                            'vhid': DictElement(parameter_form=String(title=Title('VHID'))),
                            'status': DictElement(parameter_form=String(title=Title('Status'))),
                        },
                    ),
                ),
                required=False,
                render_only=True,
            ),
        }
    )


rule_spec_opnsense_vip = CheckParameters(
    name='opnsense_vip',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_vip,
    title=Title('OPNsense VirtualIP Status'),
    help_text=Help('This rule configures check OPNsense VirtualIP status.'),
    condition=HostCondition(),
)


def _parameter_form_discovery_opnsense_carp():
    return Dictionary(
        elements={
            'discover': DictElement(
                parameter_form=SingleChoice(
                    title=Title('Discover VirtualIP'),
                    help_text=Help('Which VirtualIPs to discover'),
                    elements=[
                        SingleChoiceElement(name='none', title=Title('Discover None')),
                        SingleChoiceElement(name='master', title=Title('Discover MASTER')),
                        SingleChoiceElement(name='all', title=Title('Discover all')),
                    ],
                    prefill=DefaultValue('none'),
                ),
                required=False,
            ),
            'groupby': DictElement(
                parameter_form=SingleChoice(
                    title=Title('VirtualIP grouping'),
                    help_text=Help('How to group VirtualIPs'),
                    elements=[
                        SingleChoiceElement(name='none', title=Title('Do not group')),
                        SingleChoiceElement(name='interface', title=Title('Group by interface')),
                    ],
                    prefill=DefaultValue('none'),
                ),
                required=False,
            ),
        }
    )


rule_spec_inventory_discovery_opnsense_carp = DiscoveryParameters(
    name='discovery_opnsense_carp',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_discovery_opnsense_carp,
    title=Title('OPNsense VirtualIP Discovery'),
)
