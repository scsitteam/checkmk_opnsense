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
    Dictionary,
    DictElement,
    String,
    List,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostAndItemCondition


def _parameter_form_opnsense_ipsec():
    return Dictionary(
        elements={
            'discovered': DictElement(
                parameter_form=Dictionary(
                    title=Title('Discovered'),
                    elements={
                        'version': DictElement(
                            parameter_form=String(
                                title=Title('Phase 1 Version'),
                            ),
                            required=False,
                            render_only=True,
                        ),
                        'phase2': DictElement(
                            parameter_form=List(
                                title=Title('Phase 1 Version'),
                                element_template=Dictionary(
                                    elements={
                                        'name': DictElement(parameter_form=String()),
                                        'encr_alg': DictElement(parameter_form=String()),
                                        'integ_alg': DictElement(parameter_form=String()),
                                        'protocol': DictElement(parameter_form=String()),
                                    },
                                ),
                            ),
                            required=False,
                            render_only=True,
                        ),
                    },
                ),
                required=False,
                render_only=True,
            ),
        }
    )


rule_spec_opnsense_ipsec = CheckParameters(
    name='opnsense_ipsec',
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_opnsense_ipsec,
    title=Title('OPNsense IPSec Status'),
    help_text=Help('This rule configures thresholds for OPNsense IPSec status.'),
    condition=HostAndItemCondition(),
)
