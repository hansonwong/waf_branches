# !/usr/bin/env python
# -*- coding:utf8 -*-

from db import get_config
from config import config
from MySQL import MySQL


def ipfilter_set(args):
    with open('/usr/local/bdwaf/conf/server_ip.conf', 'w') as f:
        if not args:
            allip = get_config("IpFilterSet")["ip"]
            for ip in allip:
                if len(ip.split("-"))>1:
                    sip = ip.split("-")[0]
                    eip = ip.split("-")[1]
                else:
                    sip = ip
                    eip = ""
                if eip:
                    ipstr, _, sip_num = sip.rpartition('.')
                    _, _, eip_num = eip.rpartition('.')
                    for i in range(int(sip_num), int(eip_num)+1):
                        f.write('{}.{}\n'.format(ipstr, i))
                else:
                    f.write('{}\n'.format(sip))
        elif args[0] == 'EMPTY':
            pass
