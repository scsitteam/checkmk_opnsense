#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_opnsense - Checkmk Extension for monitoring OpnSense.
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

from typing import Optional, Sequence
import logging
import requests
from functools import cached_property

from cmk.special_agents.v0_unstable.agent_common import (
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import Args, create_default_argument_parser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGING = logging.getLogger('agent_opnsense')


class OSAPI:
    def __init__(self, url, key, secret, verify_cert=True):
        self._url = url.rstrip('/')
        self._key = key
        self._secret = secret
        self._verify_cert = verify_cert

    @cached_property
    def _cli(self):
        sess = requests.Session()
        sess.auth = (self._key, self._secret)
        return sess

    def request(self, method, module, controller, command, **kwargs):
        url = f"{self._url}/{module}/{controller}/{command}"
        LOGGING.debug(f">> {method} {url}")
        resp = self._cli.request(method, url, verify=self._verify_cert, **kwargs)
        return resp.json()

    def get(self, module, controller, command, **kwargs):
        return self.request('GET', module, controller, command, **kwargs)

    def post(self, module, controller, command, **kwargs):
        return self.request('POST', module, controller, command, **kwargs)

    @cached_property
    def getVipStatus(self):
        vips = []
        carp = None
        current = 1
        while True:
            page = self.post('diagnostics', 'interface', 'get_vip_status', json=dict(current=current))
            vips.extend(page['rows'])
            carp = page['carp']
            if page['total'] <= (page['rowCount'] * (page['current'] + 1)):
                break
            current = current + 1
        return dict(vips=vips, carp=carp)


class AgentOpnSense:
    '''Checkmk special Agent for OpnSense'''

    def run(self, args=None):
        return special_agent_main(self.parse_arguments, self.main, args)

    def parse_arguments(self, argv: Optional[Sequence[str]]) -> Args:
        parser = create_default_argument_parser(description=self.__doc__)

        parser.add_argument('-U', '--url',
                            dest='url',
                            required=True,
                            help='Base-URL of the SmartZone Public API. (ex: https://opnsense.local/api/)')
        parser.add_argument('-k', '--key',
                            dest='key',
                            required=True,
                            help='OpnSense API key.')
        parser.add_argument('-s', '--secret',
                            dest='secret',
                            required=True,
                            help='OpnSense API secret.')
        parser.add_argument('-t', '--timeout',
                            dest='timeout',
                            required=False,
                            default=10,
                            help='HTTP connection timeout. (Default: 10)')
        parser.add_argument('--ignore-cert',
                            dest='verify_cert',
                            action='store_false',
                            help='Do not verify the SSL cert from the REST andpoint.')

        return parser.parse_args(argv)

    @cached_property
    def api(self):
        return OSAPI(self.args.url, self.args.key, self.args.secret, self.args.verify_cert)

    def main(self, args: Args):
        self.args = args

        with SectionWriter('opnsense_firmware') as section:
            section.append_json(self.api.get('core', 'firmware', 'status'))

        with SectionWriter('opnsense_carp') as section:
            section.append_json(self.api.getVipStatus['carp'])
        with SectionWriter('opnsense_vip') as section:
            section.append_json(r for r in self.api.getVipStatus['vips'])
        with SectionWriter('opnsense_gateway') as section:
            section.append_json(r for r in self.api.get('routes', 'gateway', 'status')['items'])
