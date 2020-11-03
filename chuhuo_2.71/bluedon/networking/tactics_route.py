#!/usr/bin/env python
# coding=utf-8


"""
    2016-7-14:
    网口配置--> 策略路由精简配置（仅供测试用）
"""

import os
import sys
import copy
from logging import getLogger
from netaddr import IPRange
from db.config import search_data
from objectdefine.ip_range import deal_ip, get_ip
from utils.logger_init import get_logger, log_cmd, log_debug

LOG_NAME = 'TacticsRoute'
get_logger('TacticsRoute', '/usr/local/bluedon/log/tacticsroute.log')


class TacticsRoute(object):
    """ 简易版策略路由，供测试用 """

    def __init__(self, data, action):
        self.data = data
        self.iptype = data.get('sIPV', 'ipv4')
        ip_4_6_dict = {'ipv4': '', 'ipv6': '-6'}
        self.ipv4_6 = ip_4_6_dict[self.iptype]
        self.action = action
        self.ctb_cmd = 'ip {ipv4_6} rule {action} from {sip} to {dip} pref {level} table {tbname}'
        self.via_cmd = 'ip {ipv4_6} route {action} default {string} table {tbname}'

    def modify(self):
        """ 修改策略路由 """

        # 源ip
        if not self.data['iSourceIPID']:
            getLogger('TacticsRoute').debug('iSourceIPID is null!')
            return
        sips = self.ip_ipgroup(int(self.data['iSourceIPID']))

        # 目的ip
        if not self.data['iTargetIPID']:
            getLogger('TacticsRoute').debug('iTargetIPID is null!')
            return
        if self.data['iSourceIPID'] == self.data['iTargetIPID']:
            dips = copy.deepcopy(sips)
        else:
            dips = self.ip_ipgroup(int(self.data['iTargetIPID']))

        if not (sips and dips):
            getLogger('TacticsRoute').debug('源或目的ip不能为空')
            return

        if self.action == 'add':
            if str(self.data['iStatus']) == '1':
                self.table(sips, dips)
                self.via_ip()
        elif self.action == 'del':
            if str(self.data['iStatus']) == '1':
                self.via_ip()
                self.table(sips, dips)
        elif self.action == 'enable':
            if str(self.data['iStatus']) == '1':
                self.action = 'add'
                self.table(sips, dips)
                self.via_ip()
            elif str(self.data['iStatus']) == '0':
                self.action = 'del'
                self.via_ip()
                self.table(sips, dips)
        self.flush()

    def table(self, sips, dips):
        # 根据源和目的ip建表
        for sitem in sips:
            for ditem in dips:
                ctb_cmd = self.ctb_cmd.format(
                    action=self.action,
                    ipv4_6=self.ipv4_6,
                    sip=sitem,
                    dip=ditem,
                    level=self.data['sPriority'],
                    tbname=self.data['sPriority']
                )
                os.system(ctb_cmd)
                log_cmd(__file__, ctb_cmd)
                getLogger('TacticsRoute').debug(ctb_cmd)

    def via_ip(self):
        # 设置下一跳
        ip_network = ''
        if str(self.data['iIfaceJump2']) == '1':
            ip_network = ' via {viaip} '.format(viaip=self.data['sJumpName'])
        if str(self.data['iIfaceJump1']) == '1':
            ip_network += ' dev {nwname} '.format(nwname=self.data['sIfaceName'])

        if not ip_network:
            getLogger('TacticsRoute').debug('via ip and network is null!')
            return

        via_cmd = self.via_cmd.format(
            ipv4_6=self.ipv4_6,
            action=self.action,
            string=ip_network,
            tbname=self.data['sPriority']
        )
        os.system(via_cmd)
        log_cmd(__file__, via_cmd)
        getLogger('TacticsRoute').debug(via_cmd)

    def flush(self):
        """ 刷新并使策略路由生效 """
        # 刷新
        fluch_cmd = 'ip {ipv4_6} route flush cache'.format(ipv4_6=self.ipv4_6)
        os.system(fluch_cmd)
        log_cmd(__file__, fluch_cmd)
        getLogger('TacticsRoute').debug(fluch_cmd)

        # 使策略路由生效

        # ipv6下不存在rp_filter文件
        if self.iptype == 'ipv6':
            return
        path = '/proc/sys/net/{iptype}/conf'.format(iptype=self.iptype)
        files = os.listdir(path)
        for item in files:
            cmd = '/usr/bin/echo 0 > %s' % (os.path.join(path, item + '/rp_filter'))
            os.system(cmd)
            log_cmd(__file__, cmd)
            getLogger('TacticsRoute').debug(cmd)

    def ip_ipgroup(self, sid):
        """
        args:
            sid: 地址表的id号
        返回所有ip
        """

        ip_sql = 'select sAddress, sNetmask, sAddtype from \
                m_tbaddress_list where id=%d;' % (sid)
        result = search_data(ip_sql)
        if not result:
            getLogger('TacticsRoute').debug('m_tbaddress_list not id=%d' % (sid))
            return []
        result = result[0]
        if str(result['sAddtype']).strip() == '1':    # ip和掩码形式
            if self.iptype == 'ipv4':
                ip_str, _type = deal_ip(result['sAddress'], result['sNetmask'])
                addrs = [ip_str]
            else:
                if (result['sAddress'].endswith('::') or
                    result['sAddress'].endswith(':0') and result['sNetmask']):
                    addr = '%s/%s' % (result['sAddress'], result['sNetmask'])
                else:
                    addr = result['sAddress']
                addrs = [addr]
        elif str(result['sAddtype']).strip() == '2':  # ip段
            if self.iptype == 'ipv4':
                iprange = '%s-%s' % (result['sAddress'], result['sNetmask'])
                addrs = get_ip(iprange)
            else:
                addrs = IPRange(result['sAddress'], result['sNetmask'])
        return addrs


def main(action):
    if action not in ['reboot', 'init']:
        getLogger(LOG_NAME).debug('args must user reboot or init (eg: python url_filter init/reboot)')
        return

    sql = 'select * from m_tbstrategyroute'
    datas = search_data(sql)
    for data in datas:
        tr = TacticsRoute(data, 'del')
        tr.modify()

    if action == 'reboot':
        for data in datas:
            tr = TacticsRoute(data, 'add')
            tr.modify()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        getLogger(LOG_NAME).debug('more args (eg: python url_filter init/reboot)')
    else:
        main(sys.argv[1])
