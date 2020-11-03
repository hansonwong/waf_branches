#!/usr/bin/env python
# coding=utf-8

from operator import itemgetter
from itertools import groupby
#from collections import defaultdict

from db.mysql_db import select
from system.ha import init_tenv
from safetydefend.IPS_defined import custom_ips_template
from system.system_config import ips_switch


def config_suricata():

    proto_timeout = {'tcp':{'new':60,'established':600},'udp':{'new':60,'established':600},\
                   'icmp':{'new':60,'established':600},'default':{'new':60,'established':600}}

    session_info = select('select sProtocal,iStatus,sOvertime from m_tbfwsessioncontrol')
    session_info.sort(key = itemgetter('sProtocal'))
    for proto,item in groupby(session_info,key = itemgetter('sProtocal')):
            for tmp in item:
                if tmp['iStatus']=='2':
                    proto_timeout[proto]['new'] = len(tmp['sOvertime']) and tmp['sOvertime'] or proto_timeout[proto]['new']
                if tmp['iStatus']=='6' or tmp['iStatus'] == '10':
                    proto_timeout[proto]['established'] = len(tmp['sOvertime']) and tmp['sOvertime'] or proto_timeout[proto]['established']
    #print proto_timeout
    tenv = init_tenv()
    ipsconf_info = custom_ips_template()
    tenv.get_template('ips').stream(ipsinfo=ipsconf_info,proto_timeout=proto_timeout).dump('/etc/suricata/suricata.yaml')
    ips_switch('0')
    ips_switch('1')


if __name__=='__main__':
    config_suricata()


