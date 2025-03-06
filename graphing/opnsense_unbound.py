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

from cmk.graphing.v1 import metrics, graphs, perfometers, Title

metric_total_queries = metrics.Metric(
    name='total_queries',
    title=Title('Queries'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.BLACK,
)

metric_total_cachehits = metrics.Metric(
    name='total_cachehits',
    title=Title('Cache hits'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.GREEN,
)

metric_total_cachemiss = metrics.Metric(
    name='total_cachemiss',
    title=Title('Cache miss'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.BLUE,
)

metric_total_recursivereplies = metrics.Metric(
    name='total_recursivereplies',
    title=Title('Recursive replies'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.ORANGE,
)

metric_recursion_time_avg = metrics.Metric(
    name='recursion_time_avg',
    title=Title('Recursion Time Average'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.PURPLE,
)

metric_recursion_time_median = metrics.Metric(
    name='recursion_time_median',
    title=Title('Recursion Time Median'),
    unit=metrics.Unit(metrics.TimeNotation()),
    color=metrics.Color.BLUE,
)

metric_msg_cache_count = metrics.Metric(
    name='msg_cache_count',
    title=Title('Cached Messages'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.BLUE,
)

metric_rrset_cache_count = metrics.Metric(
    name='rrset_cache_count',
    title=Title('Cached RRsets'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.GREEN,
)

metric_infra_cache_count = metrics.Metric(
    name='infra_cache_count',
    title=Title('Cached Infra Items'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.ORANGE,
)

metric_key_cache_count = metrics.Metric(
    name='key_cache_count',
    title=Title('Cached Keys'),
    unit=metrics.Unit(metrics.DecimalNotation(""), metrics.StrictPrecision(0)),
    color=metrics.Color.YELLOW,
)

metric_query_type_a = metrics.Metric(
    name='query_type_a',
    title=Title('Query Type A'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.GREEN,
)

metric_query_type_aaaa = metrics.Metric(
    name='query_type_aaaa',
    title=Title('Query Type AAAA'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.LIGHT_GREEN,
)

metric_query_type_any = metrics.Metric(
    name='query_type_any',
    title=Title('Query Type ANY'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.GRAY,
)

metric_query_type_cname = metrics.Metric(
    name='query_type_cname',
    title=Title('Query Type CNAME'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_GRAY,
)

metric_query_type_dnskey = metrics.Metric(
    name='query_type_dnskey',
    title=Title('Query Type DNSKEY'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.ORANGE,
)

metric_query_type_ds = metrics.Metric(
    name='query_type_ds',
    title=Title('Query Type DS'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_ORANGE,
)

metric_query_type_hinfo = metrics.Metric(
    name='query_type_hinfo',
    title=Title('Query Type HINFO'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.LIGHT_PURPLE,
)

metric_query_type_https = metrics.Metric(
    name='query_type_https',
    title=Title('Query Type HTTPS'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_PINK,
)

metric_query_type_mx = metrics.Metric(
    name='query_type_mx',
    title=Title('Query Type MX'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_BROWN,
)

metric_query_type_ns = metrics.Metric(
    name='query_type_ns',
    title=Title('Query Type NS'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.BROWN,
)

metric_query_type_null = metrics.Metric(
    name='query_type_null',
    title=Title('Query Type NULL'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.GRAY,
)

metric_query_type_ptr = metrics.Metric(
    name='query_type_ptr',
    title=Title('Query Type PTR'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_GREEN,
)

metric_query_type_soa = metrics.Metric(
    name='query_type_soa',
    title=Title('Query Type SOA'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.LIGHT_BROWN,
)

metric_query_type_srv = metrics.Metric(
    name='query_type_srv',
    title=Title('Query Type SRV'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.LIGHT_PINK,
)

metric_query_type_svcb = metrics.Metric(
    name='query_type_svcb',
    title=Title('Query Type SVCB'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.PINK,
)

metric_query_type_txt = metrics.Metric(
    name='query_type_txt',
    title=Title('Query Type TXT'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.CYAN,
)

metric_rcode_nodata = metrics.Metric(
    name='rcode_nodata',
    title=Title('No Data'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_GRAY,
)

metric_rcode_noerror = metrics.Metric(
    name='rcode_noerror',
    title=Title('No Error'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.GREEN,
)

metric_rcode_formerr = metrics.Metric(
    name='rcode_formerr',
    title=Title('Format Error'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_RED,
)

metric_rcode_servfail = metrics.Metric(
    name='rcode_servfail',
    title=Title('Server Failure'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.RED,
)

metric_rcode_nxdomain = metrics.Metric(
    name='rcode_nxdomain',
    title=Title('Non-Existent Domain'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.LIGHT_RED,
)

metric_rcode_notimpl = metrics.Metric(
    name='rcode_notimpl',
    title=Title('Not Implemented'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_PINK,
)

metric_rcode_refused = metrics.Metric(
    name='rcode_refused',
    title=Title('Query Refused'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.PINK,
)

metric_rcode_yxdomain = metrics.Metric(
    name='rcode_yxdomain',
    title=Title('Name Exists when it should not'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.LIGHT_PINK,
)

metric_rcode_yxrrset = metrics.Metric(
    name='rcode_yxrrset',
    title=Title('RR Set Exists when it should not'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_PURPLE,
)

metric_rcode_nxrrset = metrics.Metric(
    name='rcode_nxrrset',
    title=Title('RR Set that should exist does not'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.PURPLE,
)

metric_rcode_notauth = metrics.Metric(
    name='rcode_notauth',
    title=Title('Not Authorized'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.ORANGE,
)

metric_rcode_notzone = metrics.Metric(
    name='rcode_notzone',
    title=Title('Name not contained in zone'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.DARK_ORANGE,
)

metric_rcode_nodata = metrics.Metric(
    name='rcode_nodata',
    title=Title('No Data'),
    unit=metrics.Unit(metrics.DecimalNotation("Q/s"), metrics.StrictPrecision(2)),
    color=metrics.Color.GRAY,
)

perfometer_opnsense_unbound = perfometers.Perfometer(
    name='opnsense_unbound',
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(1),
    ),
    segments=['total_cachehits', 'total_cachemiss'],
)

graph_opnsense_unbound = graphs.Graph(
    name='opnsense_unbound',
    title=Title('Queries'),
    compound_lines=['total_cachehits', 'total_cachemiss'],
    simple_lines=['total_queries', 'total_recursivereplies'],
)

graph_opnsense_unbound_recursion_time = graphs.Graph(
    name='opnsense_unbound_recursion_time',
    title=Title('Recursion Time'),
    compound_lines=['recursion_time_avg'],
    simple_lines=['recursion_time_median'],
)

graph_opnsense_unbound_cached = graphs.Graph(
    name='opnsense_unbound_cached',
    title=Title('Caches'),
    simple_lines=['msg_cache_count', 'rrset_cache_count', 'infra_cache_count', 'key_cache_count'],
)

graph_opnsense_unbound_query_type = graphs.Graph(
    name='opnsense_unbound_query_type',
    title=Title('Query Types'),
    compound_lines=[
        'query_type_a',
        'query_type_aaaa',
        'query_type_any',
        'query_type_cname',
        'query_type_dnskey',
        'query_type_ds',
        'query_type_hinfo',
        'query_type_https',
        'query_type_mx',
        'query_type_ns',
        'query_type_null',
        'query_type_ptr',
        'query_type_soa',
        'query_type_srv',
        'query_type_svcb',
        'query_type_txt',
    ],
    optional=[
        'query_type_a',
        'query_type_aaaa',
        'query_type_any',
        'query_type_cname',
        'query_type_dnskey',
        'query_type_ds',
        'query_type_hinfo',
        'query_type_https',
        'query_type_mx',
        'query_type_ns',
        'query_type_null',
        'query_type_ptr',
        'query_type_soa',
        'query_type_srv',
        'query_type_svcb',
        'query_type_txt',
    ],
)

graph_opnsense_unbound_rcode = graphs.Graph(
    name='opnsense_unbound_rcode',
    title=Title('Return Codes'),
    compound_lines=[
        'rcode_noerror',
        'rcode_formerr',
        'rcode_servfail',
        'rcode_nxdomain',
        'rcode_notimpl',
        'rcode_refused',
        'rcode_yxdomain',
        'rcode_yxrrset',
        'rcode_nxrrset',
        'rcode_notauth',
        'rcode_notzone',
        'rcode_nodata',
    ],
    optional=[
        'rcode_noerror',
        'rcode_formerr',
        'rcode_servfail',
        'rcode_nxdomain',
        'rcode_notimpl',
        'rcode_refused',
        'rcode_yxdomain',
        'rcode_yxrrset',
        'rcode_nxrrset',
        'rcode_notauth',
        'rcode_notzone',
        'rcode_nodata',
    ],
)
