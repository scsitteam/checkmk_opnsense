#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# checkmk_opnsense - Checkmk Extension for monitoring OpnSense.
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

from typing import Optional, Sequence
import logging
import requests
from functools import cached_property
from json import JSONDecodeError

from cmk.special_agents.v0_unstable.agent_common import (
    CannotRecover,
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import Args, create_default_argument_parser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGING = logging.getLogger('agent_opnsense')


class OSAPI:
    def __init__(self, url, key, secret, timeout=None, verify_cert=True):
        self._url = url.rstrip('/')
        self._key = key
        self._secret = secret
        self._verify_cert = verify_cert
        self.timeout = timeout

    @cached_property
    def _cli(self):
        sess = requests.Session()
        sess.auth = (self._key, self._secret)
        return sess

    def request(self, method, module, controller, command, **kwargs):
        url = f"{self._url}/{module}/{controller}/{command}"
        LOGGING.debug(f">> {method} {url}")
        try:
            resp = self._cli.request(method, url, verify=self._verify_cert, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise CannotRecover(f"Could not authenticate to {url}. Key or secret is incorrect.") from exc
            if exc.response.status_code == 403:
                raise CannotRecover(f"Not permited to access {url}.") from exc
            raise CannotRecover(f"Request error {exc.response.status_code} when trying to {method} {url}") from exc
        except requests.exceptions.ReadTimeout as exc:
            raise CannotRecover(f"Read timeout after {self.timeout}s when trying to {method} {url}") from exc
        except requests.exceptions.ConnectionError as exc:
            raise CannotRecover(f"Could not {method} {url} ({exc})") from exc
        except JSONDecodeError as exc:
            raise CannotRecover(f"Couldn't parse JSON at {url}") from exc

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
                            type=int,
                            required=False,
                            default=10,
                            help='HTTP connection timeout. (Default: 10)')
        parser.add_argument('--ignore-cert',
                            dest='verify_cert',
                            action='store_false',
                            help='Do not verify the SSL cert from the REST andpoint.')
        parser.add_argument('--firmware',
                            dest='firmware',
                            action='store_true',
                            help='Fetch Firmaware status')
        parser.add_argument('--vip',
                            dest='vip',
                            action='store_true',
                            help='Fetch VIP status')
        parser.add_argument('--gateway',
                            dest='gateway',
                            action='store_true',
                            help='Fetch Gateway status')
        parser.add_argument('--ipsec',
                            dest='ipsec',
                            action='store_true',
                            help='Fetch IPSec status')

        return parser.parse_args(argv)

    @cached_property
    def api(self):
        return OSAPI(self.args.url, self.args.key, self.args.secret, timeout=self.args.timeout, verify_cert=self.args.verify_cert)

    def main(self, args: Args):
        self.args = args

        if self.args.firmware:
            with SectionWriter('opnsense_firmware') as section:
                section.append_json(self.api.get('core', 'firmware', 'status'))

        if self.args.vip:
            with SectionWriter('opnsense_carp') as section:
                section.append_json(self.api.getVipStatus['carp'])
            with SectionWriter('opnsense_vip') as section:
                section.append_json(r for r in self.api.getVipStatus['vips'])

        if self.args.gateway:
            with SectionWriter('opnsense_gateway') as section:
                section.append_json(r for r in self.api.get('routes', 'gateway', 'status')['items'])

        if self.args.ipsec:
            ipsec_connections = [
                conn
                for conn in self.api.post('ipsec', 'connections', 'search_connection')['rows']
                if conn['enabled'] == "1"
            ]

            with SectionWriter('opnsense_ipsec') as section:
                section.append_json(r for r in ipsec_connections)
            with SectionWriter('opnsense_ipsec_phase1') as section:
                section.append_json(r for r in self.api.get('ipsec', 'sessions', 'search_phase1')['rows'])
            with SectionWriter('opnsense_ipsec_phase2') as section:
                for conn in ipsec_connections:
                    section.append_json(r for r in self.api.post('ipsec', 'sessions', 'search_phase2', json=dict(id=conn['uuid']))['rows'])
