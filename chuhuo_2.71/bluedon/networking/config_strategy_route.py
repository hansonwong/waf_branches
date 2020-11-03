#! /usr/bin/env python
# -*- coding:utf-8 -*-

"""
modify log:
    2016-7-18:
        1、重写策略路由
    2016-8-12:
        1、新增ipv6功能
    2016-10-22:
        1、修复开机恢复bug
"""


import os
import json
import sys
import subprocess
from logging import getLogger

from utils.logger_init import logger_init
from utils.app_mark_count import set_app_mark
from db.config import search_data

from IPy import IP


LOG_NAME = 'TACTICS_ROUTE'
LOG_PATH = '/usr/local/bluedon/log/tactics_route.log'

logger_init(LOG_NAME, LOG_PATH)


class TacticsRoute(object):
    """ 策略路由配置 """

    def __init__(self, data, iptables, ip_4_6, action):
        """ 初始化 """
        self.data = data
        self.iptables = iptables
        self.ip_4_6 = ip_4_6
        self.action = action
        self.move = {'add': 'A', 'del': 'D'}
        self.left_mark = int(self.data['sPriority']) << 12
        self.iptables_cmd = '{iptablepath} -t mangle -{move} POLICY_ROUTE_MARK\
            {sip} {dip} {port_mark} {jstr}'
        self.table_cmd = '/usr/sbin/ip {ip_4_6} rule {action} fwmark\
            {lm}/0x000FF000 pref {level} table {tablename}'
        self.via_cmd = '/usr/sbin/ip {ip_4_6} route {action} default {string}\
            table {tbname}'

    def set_iptables(self):
        """ 设置iptables """

        def ip_ipgroup(vid, sdtype):
            """
            args:
                vid: 相关连ip/ip组表的id
                sdtype: 源地址(s), 目的地址(d)
            return:
                istr: 拼接后的字符串
            """

            type_dict = {
                's': {
                    'onlyip': ' -s %s ',
                    'iprange': ' -m iprange --src-range %s-%s ',
                    },
                'd': {
                    'onlyip': ' -d %s ',
                    'iprange': ' -m iprange --dst-range %s-%s ',
                    }
                }

            istr = u' '
            ip_sql = 'select sAddress, sNetmask, sAddtype, sIPV from \
                    m_tbaddress_list where id=%d;' %(vid)
            data = search_data(ip_sql)
            if not data:
                getLogger(LOG_NAME).debug('m_tbaddress_list table not id %d' %(vid))
                #raise ArgumentError
            data = data[0]
            if str(data['sAddtype']).strip() == '1':        # ip和掩码形式
                if data['sIPV'] == 'ipv6':    # ipv6
                    if (data['sAddress'].endswith('::') or
                        data['sAddress'].endswith(':0')):
                        addr = '%s/%s' %(data['sAddress'], data['sNetmask'])
                    else:
                        addr = data['sAddress']
                else:
                    if data['sAddress'].endswith('.0'):
                        if '.' not in data['sNetmask']:
                            addr = '%s/%s' %(data['sAddress'], data['sNetmask'])
                        else:
                            addr = IP('%s/%s' %(data['sAddress'], data['sNetmask']),
                                    make_net=True).strNormal(1)
                    else:
                        addr = data['sAddress']
                istr = type_dict[sdtype]['onlyip'] %(addr)
            elif str(data['sAddtype']).strip() == '2':        # ip段
                istr = type_dict[sdtype]['iprange']
                istr = istr %(data['sAddress'], data['sNetmask'])
            return istr

        sip_str = u' '
        if self.data['iSourceIPID']:
            sip_str = ip_ipgroup(int(self.data['iSourceIPID']), 's')

        dip_str = u' '
        if self.data['iTargetIPID']:
            dip_str = ip_ipgroup(int(self.data['iTargetIPID']), 'd')

        # 基于协议或应用打标记
        pm_str = u' '
        if int(self.data['iProtocolApp']) == 1:
            port_str = u' '
            if self.data['sProtocol']:
                port_str = ' -p {port} '.format(port=self.data['sProtocol'])
            sport_str = u' '
            if self.data['iSourcePort']:
                sport_str = ' --sport {sport} '.format(sport=self.data['iSourcePort'])
            dport_str = u' '
            if self.data['iTargetPort']:
                dport_str = ' --dport {dport}'.format(dport=self.data['iTargetPort'])
            pm_str = port_str + sport_str + dport_str
        else:
            pm_str = ' -m mark --mark {markid}/0xFFF '.format(markid=self.data['iApplicationID'])
            set_app_mark(int(self.data['iApplicationID']), self.action)

        j_str = u' '
        if self.data['sPriority']:
            j_str = ' -j MARK --or-mark {l_mark} '.format(l_mark=self.left_mark)

        iptables_cmd = self.iptables_cmd.format(iptablepath=self.iptables,
                                                sip=sip_str,
                                                move=self.move[self.action],
                                                dip=dip_str,
                                                port_mark=pm_str,
                                                jstr=j_str)
        print iptables_cmd
        os.system(iptables_cmd)
        getLogger(LOG_NAME).debug(iptables_cmd)

    def set_table(self):
        """ 设置表 """
        table_cmd = self.table_cmd.format(ip_4_6=self.ip_4_6,
                                          action=self.action,
                                          lm=self.left_mark,
                                          level=self.data['sPriority'],
                                          tablename=self.data['sPriority'])
        print table_cmd
        os.system(table_cmd)
        getLogger(LOG_NAME).debug(table_cmd)

    def set_via(self):
        """ 设置下一跳 """
        ip_network = ''
        if self.data.get('iIfaceJump2', ''):
            if int(self.data['iIfaceJump2']) == 1:
                ip_network = ' via {viaip} '.format(viaip=self.data['sJumpName'])
        if self.data.get('iIfaceJump1', ''):
            if int(self.data['iIfaceJump1']) == 1:
                ip_network += ' dev {nwname} '.format(nwname=self.data['sIfaceName'])

        if not ip_network :
            getLogger(LOG_NAME).debug('via ip and network is null!')
            return

        via_cmd = self.via_cmd.format(ip_4_6=self.ip_4_6,
                                      action=self.action,
                                      string=ip_network,
                                      tbname=self.data['sPriority'])
        print via_cmd
        os.system(via_cmd)
        getLogger(LOG_NAME).debug(via_cmd)

    def flush(self):
        """ 刷新并使策略路由生效 """
        # 刷新
        fluch_cmd = 'ip {ip_4_6} route flush cache'.format(ip_4_6=self.ip_4_6)
        os.system(fluch_cmd)
        getLogger(LOG_NAME).debug(fluch_cmd)

        # 使策略路由生效
        if self.ip_4_6 == 'ipv4':
            path = '/proc/sys/net/ipv4/conf'
        else:
            path = '/proc/sys/net/ipv6/conf'
        files = os.listdir(path)
        for item in files:
            filepath = os.path.join(path, item + '/rp_filter')
            if os.path.isfile(filepath):
                cmd = '/usr/bin/echo 0 > %s' %(filepath)
                os.system(cmd)
                getLogger(LOG_NAME).debug(cmd)
            else:
                getLogger(LOG_NAME).debug('not file {0}'.format(filepath))

    def run(self):
        if self.action == 'enable':
            if int(self.data['iStatus']) == 1:
                self.action = 'add'
            else:
                self.data['iStatus'] = 1
                self.action = 'del'

        if int(self.data['iStatus']) == 1:
            if self.action == 'add':
                self.set_iptables()
                self.set_table()
                self.set_via()
                self.flush()
            if self.action == 'del':
                self.set_via()
                self.set_table()
                self.set_iptables()

def main(action):
    if not action in ['reboot', 'init']:
        getLogger(LOG_NAME).debug('args must user reboot or init (eg: python url_filter init/reboot)')
        return

    def run(action):
        sql = 'select * from m_tbstrategyroute;'
        datas = search_data(sql)
        ip_4_6_dict = {'ipv4': ' ', 'ipv6': ' -6 '}
        for data in datas:
            iptype = data.get('sIPV', 'ipv4')
            ip_4_6 = ip_4_6_dict[iptype]
            if iptype == 'ipv4':
                iptables = '/usr/sbin/iptables'
            else:
                iptables = '/usr/sbin/ip6tables'
            tr = TacticsRoute(data, iptables, ip_4_6, action)
            tr.run()

    run('del')
    if action == 'reboot':
        run('add')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        getLogger(LOG_NAME).debug('more args (eg: python url_filter init/reboot)')
    else:
        main(sys.argv[1])
