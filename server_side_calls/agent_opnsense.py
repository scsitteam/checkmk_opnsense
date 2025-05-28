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


from collections.abc import Iterator

from pydantic import BaseModel

from cmk.server_side_calls.v1 import HostConfig, Secret, SpecialAgentCommand, SpecialAgentConfig, replace_macros


class Params(BaseModel):
    url: str
    key: str
    secret: Secret | None = None
    ignore_cert: str = 'check_cert'
    firewall: bool
    firmware: bool
    vip: bool
    gateway: bool
    ipsec: bool
    unbound: bool = False
    snapshot: bool = False
    ssl: bool = False


def commands_function(
    params: Params,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    command_arguments: list[str | Secret] = [
        '-U', replace_macros(params.url, host_config.macros),
        '-k', params.key,
        '-s', params.secret.unsafe(),
    ]
    if params.ignore_cert != 'check_cert':
        command_arguments += ['--ignore-cert']

    for part in ['firewall', 'firmware', 'vip', 'gateway', 'ipsec', 'unbound', 'snapshot', 'ssl']:
        if getattr(params, part, False):
            command_arguments += [f"--{part}"]

    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_opnsense = SpecialAgentConfig(
    name='opnsense',
    parameter_parser=Params.model_validate,
    commands_function=commands_function,
)
