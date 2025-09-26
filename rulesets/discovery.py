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

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    Dictionary, DictElement,
    SingleChoice, SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import DiscoveryParameters
from cmk_addons.plugins.opnsense.lib.rulesets import TOPIC


def _parameter_form_opnsense_discovery():
    return Dictionary(
        elements={
            'gateway': DictElement(
                parameter_form=SingleChoice(
                    title=Title('Gateway discovery'),
                    help_text=Help('Configures how gateways are discoverd.'),
                    elements=[
                        SingleChoiceElement(name='all', title=Title('Discover all gateways.')),
                        SingleChoiceElement(name='online', title=Title('Discover online gateways.')),
                        SingleChoiceElement(name='monitored', title=Title('Discover monitored gateways.')),
                        SingleChoiceElement(name='none', title=Title('Do not discover gateways.')),
                    ],
                    prefill=DefaultValue('online'),
                ),
                required=False,
            ),
        }
    )


rule_spec_opnsense_discovery = DiscoveryParameters(
    title=Title('OPNsense Discovery'),
    topic=TOPIC,
    parameter_form=_parameter_form_opnsense_discovery,
    name='opnsense_discovery',
    help_text=Help('This rule configures how checks for OPNsense are discoverd.'),
)
