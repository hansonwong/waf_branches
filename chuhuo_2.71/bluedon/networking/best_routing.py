#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""策略路由自动选路
1. 使用此功能时，会配置多条相同源地址且相同目的地址的策略路由，这些路由归为同一组，可以有多组。
2. 每组策略路由，实质上只有优先级最小的那条生效，此处称为首条路由。当开启此功能时，
   每组有一条为主路由，其他为备用路由，且主路由的优先级值最小，此时主路由也就是首条路由。
3. 每次遍历，判断主路由是否生效，若生效，确保主路由为首条路由；若失效，判断当前首条路由是否生效，生效则跳过这组；
   如果首条路由也失效，从备用路由中选择一条有效的路由，与之交换；
"""
import sys
import time
import json
import psutil
from commands import getstatusoutput
from itertools import groupby
from logging import getLogger
from copy import deepcopy

from netaddr import IPNetwork, IPAddress

from db.mysql_db import select, select_one, update
from networking.tactics_route import TacticsRoute
from networking.nat64 import exec_cmd
from firedam.nat import set_nat
from utils.logger_init import get_logger


get_logger('main', '/usr/local/bluedon/log/best_routing.log')
get_logger('best_routing', '/usr/local/bluedon/log/best_routing.log')


def proc_snat(route):
    """根据策略路由的下一跳，找到对应的snat，修改snat的目标地址为，与下一跳同网段的ip（次ip在网口上）"""
    iface = route.get('sIfaceName', '')
    jump_id = route['iSourceIPID']
    if iface.startswith('ppp'):
        conver_value = iface
    else:
        next_jump = IPAddress(route['sJumpName'])
        all_networks = []
        for addrs in psutil.net_if_addrs().values():
            all_networks.extend([IPNetwork('{}/{}'.format(i.address, i.netmask))
                                 for i in addrs if i.family == 2])
        for i in all_networks:
            if next_jump in i.cidr:
                conver_value = i.ip.format()
                break
    update('UPDATE m_tbSnat SET sConverTypeValue=? WHERE sSourceIP=?',
           conver_value, jump_id)
    getLogger('main').info('change snat sSourceIP: %s, sConverTypeValue to %s', jump_id, conver_value)
    set_nat('SNAT', active='reboot')


def get_routes_from_db():
    """从数据库获取策略路由
    return:
        raw_routes: 路由数据 {id: data_dict, id: data_dict}
        group_routes: {(目的地址, 源地址): [路由id列表]}
        main_routes： {(目的地址, 源地址): 主路由ID}
    """

    all_routes = select('SELECT * FROM m_tbstrategyroute WHERE iStatus=1;')
    if not all_routes: return ({}, {}, {})
    raw_routes = {i['id']: i for i in all_routes if i}
    all_routes.sort(key=lambda i: (i['sTargetIPAddr'], i['sSourceIPAddr']))
    group_routes = {}
    main_routes = {}
    for k, v in groupby(all_routes, key=lambda i: (i['sTargetIPAddr'], i['sSourceIPAddr'])):
        v = list(v)  # 原始的v是生成器，只能进行一次迭代
        main_routes[k] = sorted(v, key=lambda i: i['RouteModel'], reverse=True)[0]['id']  # RouteModel, 1 为主路由
        group_routes[k] = [i['id'] for i in sorted(v, key=lambda i: i['sPriority']) if i]  # 按优先级排序
    return raw_routes, group_routes, main_routes


def check_route_status(route):
    """判断当前路由是否有效
    args:
        route: 数据库中一条路由记录
    return:
        1 --> 有效
        0 --> 无效
    """

    iface = route.get('sIfaceName', '')
    addr = route.get('sJumpName', '')
    if iface.startswith('ppp'):  # 拨号口的策略路由
        all_ifaces = psutil.net_if_addrs()
        # 拨号口存在，并且获取到了ip，则判定这条路由有效
        if (iface in all_ifaces and
                len([i for i in all_ifaces[iface] if i.family == 2]) >= 1):
            return 1
        return 0

    for i in range(1, 4):
        status = getstatusoutput('ping -i 0.2 -I %s -W 1 -c %s %s' % (iface, i, addr))[0]
        if status == 0: break
    getLogger('main').info('ping %s via %s : %s', addr, iface, status)
    return 1 if status == 0 else 0


def swap_route(routes, first, tomove):
    """将一条策略路由与首条交换
    args:
        routes: 含有所有路由的一个字典，以路由的id为key
        first: 当前首条路由的id
        tomove: 替换当前首条路由的路由id
    """
    # 保存修改优先级之前的数据
    old_first = deepcopy(routes[first])
    old_tomove = deepcopy(routes[tomove])
    # 交换raw_routes中两条策略的优先级
    routes[tomove]['sPriority'], routes[first]['sPriority'] = \
    routes[first]['sPriority'], routes[tomove]['sPriority']
    # 修改数据库中两条策略的优先级
    update('update m_tbstrategyroute set sPriority=? where id=?',
           routes[first]['sPriority'], routes[first]['id'])
    update('update m_tbstrategyroute set sPriority=? where id=?',
           routes[tomove]['sPriority'], routes[tomove]['id'])
    # 删除旧路由，添加新路由
    TacticsRoute(old_first, 'del').modify()
    TacticsRoute(routes[tomove], 'add').modify()
    TacticsRoute(old_tomove, 'del').modify()
    TacticsRoute(routes[first], 'add').modify()
    proc_snat(routes[tomove])  # 切换snat
    getLogger('main').info('swap route: %s <--> %s', first, tomove)


def best_routing():
    """策略路由自动切换主备，主函数"""

    getLogger('main').info('Best Routing start.')
    raw_routes, group_routes, main_routes = get_routes_from_db()
    if len(raw_routes) < 1:
        getLogger('main').info('no routes!!')
        return

    while True:
        for source, routes in group_routes.iteritems():
            if len(routes) == 1: continue
            main = main_routes[source]
            if check_route_status(raw_routes[main]) == 1:  # 主路由通
                if group_routes[source][0] == main: continue
                swap_route(raw_routes, group_routes[source][0], main)  # 将主路由切回首条
                _index = routes.index(main)
                group_routes[source][0], group_routes[source][_index] = \
                group_routes[source][_index], group_routes[source][0]
            elif check_route_status(raw_routes[routes[0]]) == 1:  # 首条通
                continue
            else:
                for i in range(1, len(routes)):
                    if check_route_status(raw_routes[routes[i]]) == 1:  # 从备选里选一条通的，替换首条
                        swap_route(raw_routes, group_routes[source][0], routes[i])
                        group_routes[source][0], group_routes[source][i] = \
                        group_routes[source][i], group_routes[source][0]
                        break
        time.sleep(5)


def start_best_routing(action):
    status, output = exec_cmd('systemctl status best-routing')
    if status and 'not-found' in output:
        exec_cmd('/usr/bin/cp /usr/local/bluedon/conf/systemctl/best-routing.service /usr/lib/systemd/system')
    exec_cmd('systemctl disable best-routing')
    if str(action) == '1':
        exec_cmd('systemctl start best-routing')
    else:
        exec_cmd('systemctl stop best-routing')


def recover(_type):
    data = select_one('SELECT sValue FROM m_tbconfig WHERE sName="AutoSelect"')
    action = json.loads(data['sValue'])['iTurnOn'] if data else 0
    if _type != 'boot_recover':
        action = 0
    start_best_routing(action)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        best_routing()
    elif len(sys.argv) == 2:
        recover(_type=sys.argv[1])
