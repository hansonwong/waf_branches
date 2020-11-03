#!/usr/bin/env python
# coding=utf-8

import os
import sys
import json
from operator import itemgetter
from collections import defaultdict
from netaddr import IPAddress, IPRange, IPNetwork
from config import fetchall_sql as select

reload(sys)
sys.setdefaultencoding('utf-8')

CONF_TB = 'm_tburl_filter_ips'
SQL_BY_ID = 'SELECT * FROM {tb} WHERE id={idx};'

ONLINE_USER = '/usr/local/bluedon/conf/online_users'

TIME_PLAN_TB = {1: 'm_tbtimeplan_single', 2: 'm_tbtimeplan_loop'}
ADDRESS_TB = {3: 'm_tbaddress_list', 4: 'm_tbaddressgroup'}
USER_TB = {1: 'm_tbusers', 2: 'm_tbgroup'}
IP_TYPE = {1: 'mask', 2: 'range'}
URL_LIST_TB = 'm_tburlgroup'

def get_ipaddress(type_, idx):
    ret = list()
    if type_ not in ADDRESS_TB: return ret
    if 'm_tbaddressgroup' == ADDRESS_TB[type_]:
        for r in select(SQL_BY_ID.format(tb=ADDRESS_TB[type_], idx=idx)):
            for ridx in r['sIP'].split(','):
                r_ = select(SQL_BY_ID.format(tb=ADDRESS_TB[3], idx=ridx))
                [ ret.append(r__) for r__ in r_ ]
    else:
        [ ret.append(r) for r in
          select(SQL_BY_ID.format(tb=ADDRESS_TB[type_], idx=idx))]

    # get ip network
    ip_ret = set()
    for r in ret:
        ip_str = '/'.join((r['sAddress'], r['sNetmask']))
        ip_type = IP_TYPE[int(r['sAddtype'])]
        net = get_ip_network(ip_str, ip_type)
        ip_ret.add(net)

    return ip_ret

def get_ip_network(ip_str, ip_type=None, ip_split='/'):
    """
        ip_type: range/mask
    """
    support_types = ('range', 'mask')
    if ip_type not in support_types:
        return ip_str

    ret_lst = list()
    ip_count = 0
    if ip_type == 'mask':
        ips = IPNetwork(ip_str)

    elif ip_type == 'range':
        ips = IPRange(*ip_str.split(ip_split))

    return ips

def get_user_name(type_, idx):
    # return all user id
    ret = list()
    if int(type_) == 1:
        ret.append(int(idx))
    elif int(type_) == 2:
        tb = 'm_tbusers'
        for r in select("SELECT id FROM {tb} WHERE iGroupID={idx}".format(tb=tb, idx=int(idx))):
            ret.append(int(r['id']))
    return ret
    pass


def parser_user_ip_map(p=ONLINE_USER):
    # check if user-ip mapping file exists
    if not os.path.exists(p):
        print '[audit_traffic_statistics] %s dose not exists' % p
        return None, None

    with open(ONLINE_USER, 'r') as fp:
        # TODO: if ONLINE_USER file is VERY BIG
        lines = fp.readlines()

    try:
        if len(lines) > 0:
            user_group_map = json.loads(''.join(lines))
        else:
            return None, None
    except ValueError:
        return None, None

    # _uname = itemgetter(0)
    # _gname = itemgetter(2)
    # online_user contain lines like:
    # {"172.16.3.145": ["aaa", 4, "group1", 110662, 8]}
    # {ip: [username, int, groupname, group_id, user_id]}

    _uid = itemgetter(4)
    _gid = itemgetter(3)

    ret_g = defaultdict(set)
    ret_u = defaultdict(set)
    # get ip user mapping
    for ip, info in user_group_map.items():
        ret_g[_gid(info)].add(ip)
        ret_u[_uid(info)].add(ip)

    return ret_g, ret_u



def get_user_ip(xid, xip_map=None):

    xid = int(xid)

    if not isinstance(xip_map, dict): return set()
    else:
        return xip_map.get(xid, set())

# 1: user | 2: user_group | 3: ip | 4: ip_group
def get_ip_mapping(type_id, type_val, gip_map, uip_map):
    if type_id == 1:
        return get_user_ip(type_val, uip_map)
    elif type_id == 2:
        return get_user_ip(type_val, gip_map)
    elif type_id == 3 or type_id == 4:
        return get_ipaddress(type_id, type_val)
    else:
        return set()


if __name__ == '__main__':
    # print get_ipaddress(4, 1)
    # print get_ipaddress(3, 1)
    # get_user_name(2, 4)
    # get_user_name(1, 1)
    g, u = parser_user_ip_map()
    print get_ip_mapping(4,1, g, u)
    pass
