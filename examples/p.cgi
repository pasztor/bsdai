#!/usr/bin/env -S -P ${PATH}:/usr/local/bin python
#
# Copyright 2022 PASZTOR Gyorgy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# $FreeBSD$

import sys
import os
import string
import random
import json

# Generate random string for debug dumping
myrnd = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(32))

# Whatever happens, the output will be a plain text
print('Content-type: text/plain\n')

_debug = os.environ.get('DEBUG','') == 'y'
_fttrace = os.environ.get('FTTRACE','') == 'y'

def process_query_string(qs):
    ret = dict()
    for k, v in [ (x.split('=', 1)+ [''])[0:2] for x in qs.split('&')]:
        if k == '':
            continue
        elif k == 'mac':
            v = ''.join(v.split(':')).upper()
        ret.setdefault(k,v)
    return ret

def find_setup_file( mac = '', ip = '', host = ''):
    setupdir = os.path.realpath(os.path.join(os.environ.get('DOCUMENT_ROOT','/home/pasztor/cgi'),'../setup'))
    _debug and print(f'debug: home -> {setupdir}')
    ips = ip.split('.')
    try:
        iphex = ''.join([ '{:02X}'.format(int(i)) for i in ips ])
    except ValueError:
        iphex = '00000000'
    _debug and print(f'debug: iphex -> {iphex}')
    for _host in [ host, '_']:
        _debug and print(f'debug: _host {_host}')
        for _ip in ([ '.'.join(ips[:i]) for i in range(len(ips), 0, -1) ] + [ iphex[:i] for i in range(len(iphex), -1, -1)]):
            _debug and print(f'debug: _ip {_ip}')
            for _mac in [ mac[:i] for i in range(len(mac), -1, -1) ]:
                _debug and print(f'debug: _mac {_mac}')
                tfname = os.path.join(setupdir, f'{_host}-{_ip}-{_mac}')
                _fttrace and print(f'testing: {tfname}')
                if os.path.isfile(tfname):
                    return tfname
    return None

q_params = process_query_string(os.environ.get('QUERY_STRING', ''))

setup_file = find_setup_file(mac = q_params.get('mac', ''), ip=q_params.get('ip', '0.0.0.0'), host=q_params.get('host', ''))

if setup_file is None:
    print('#!/bin/sh')
    print('cat <<\'END%s\'' % myrnd)
    print(json.dumps(dict(os.environ), indent=4))
    print('stdin:')
    print(sys.stdin.read())

    print('Query params processed:')
    print(json.dumps(q_params, indent=4))

    print('END%s' % myrnd)
else:
    with open(setup_file, 'r') as f:
        print(f.read())
