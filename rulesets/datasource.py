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

from cmk.rulesets.v1 import Title, Help, Label
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    migrate_to_password,
    Password,
    SingleChoice,
    SingleChoiceElement,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def migrate_bool_to_choice(model: object) -> str:
    if isinstance(model, bool):
        return 'ignore_cert' if model else 'check_cert'
    return model


def migrate_special_agents_opnsense(model: dict) -> dict:
    defaults = dict(
        firewall=True,
        firmware=True,
        vip=True,
        gateway=True,
        ipsec=True,
    )
    for key in defaults:
        if key in model:
            continue
        model[key] = defaults[key]
    return model


def _form_special_agents_opnsense() -> Dictionary:
    return Dictionary(
        title=Title('Dell Storage via Dell Storage API'),
        elements={
            'url': DictElement(
                parameter_form=String(
                    title=Title('URL of the OPNsense API, e.g. https://firewall/api/'),
                    custom_validate=(
                        validators.Url(
                            [validators.UrlProtocol.HTTP, validators.UrlProtocol.HTTPS],
                        ),
                    ),
                    macro_support=True,
                ),
                required=True,
            ),
            'key': DictElement(
                parameter_form=String(
                    title=Title('OPNsense API Key.'),
                ),
                required=True,
            ),
            'secret': DictElement(
                parameter_form=Password(
                    title=Title('OPNsense API secret'),
                    migrate=migrate_to_password
                ),
                required=True,
            ),
            'ignore_cert': DictElement(
                parameter_form=SingleChoice(
                    title=Title('SSL certificate checking'),
                    elements=[
                        SingleChoiceElement(name='ignore_cert', title=Title('Ignore Cert')),
                        SingleChoiceElement(name='check_cert', title=Title('Check Cert')),
                    ],
                    prefill=DefaultValue('check_cert'),
                    migrate=migrate_bool_to_choice,
                ),
                required=True,
            ),
            'firewall': DictElement(
                parameter_form=BooleanChoice(
                    label=Label('Fetch Firewall status'),
                    prefill=DefaultValue('true'),
                ),
                required=True,
            ),
            'firmware': DictElement(
                parameter_form=BooleanChoice(
                    label=Label('Fetch Firmware status'),
                    prefill=DefaultValue('true'),
                ),
                required=True,
            ),
            'vip': DictElement(
                parameter_form=BooleanChoice(
                    label=Label('Fetch VIP status'),
                    prefill=DefaultValue('true'),
                ),
                required=True,
            ),
            'gateway': DictElement(
                parameter_form=BooleanChoice(
                    label=Label('Fetch Gateway status'),
                    prefill=DefaultValue('true'),
                ),
                required=True,
            ),
            'ipsec': DictElement(
                parameter_form=BooleanChoice(
                    label=Label('Fetch IPSec status'),
                    prefill=DefaultValue('true'),
                ),
                required=True,
            ),
        },
        migrate=migrate_special_agents_opnsense,
    )


rule_spec_opnsense_datasource = SpecialAgent(
    name="opnsense",
    title=Title('OPNsense RestAPI Agent'),
    help_text=Help(
        'This rule selects the OPNsense RestAPI agent instead of '
        'the normal Check_MK Agent and allows monitoring of '
        'OPNsense systems and volumes by REST. '
        'You can configure your connection settings here.'
    ),
    topic=Topic.NETWORKING,
    parameter_form=_form_special_agents_opnsense,
)
