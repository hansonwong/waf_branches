#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import sys
from logging import getLogger
from itertools import chain

import psutil
from IPy import IP

from networking import net_cmd
from networking.route import recover as static_route_recover
from networking.devices import get_physical_ifaces
from utils.mask_transition import exchange_mask, strmask_to_intv6
from utils.file_handling import get_lines
from db.mysql_db import select, select_one
from utils.log_logger import rLog_dbg
LOG_NAME = 'config_iface'
DBG = lambda x: rLog_dbg('config_iface', x)
EXECUTE_CMD = lambda cmd: net_cmd.execute_cmd(cmd, LOG_NAME)
MANAGE_NIC_PATH = '/etc/network_config/mgt_nic.txt'


# pylint: disable=E1101

__author__ = 'ruan.lj@foxmail.com'

NIC_WORKMODE = {
    "route":      "10",  # 路由模式
    "redundancy": "10",  # 冗余模式
    "virtual":    "10",  # 虚拟线
    "mirror":     "9",  # 镜像模式
    "bridge":     "8",  # 桥模式
    "nat":        "11",  # nat模式
    "bypass":     "5",  # 旁路模式
}

IPTABLES = '/usr/sbin/iptables'
IP6TABLES = '/usr/sbin/ip6tables'
NGINX_FILE = '/Data/apps/nginx/conf/ssl.conf'


def allow_manage(device, allow, version=4, ports='22', log=False):
    """配置用于管理
    args：
        device: portname
        allow: True or False
        version: 4 or 6, 代表ipv4还是ipv6
        ports： 端口号
    """
    if version == 4:
        cmd = (IPTABLES + ' -{add_or_del} FWINPUT -i {device} -p tcp -m multiport --dports {ports} -j {jump};' +
               IPTABLES + ' -{add_or_del} FWINPUT -i {device} -p tcp --dport {nginx_port} -j {jump}')
    else:
        cmd = (IP6TABLES + ' -{add_or_del} FWINPUT -i {device} -p tc'
                           'p -m multiport --dports {ports} -j {jump};' +
               IP6TABLES + ' -{add_or_del} FWINPUT -i {device} -p tcp --dport {nginx_port} -j {jump}')
    # 从nginx配置文件中获取webserver监听的端口，默认应该是444
    tmp = r"cat %s|grep '^\s*listen\s*[0-9]\{1,5\}\;$'" % NGINX_FILE
    status, output = EXECUTE_CMD(tmp)
    if status:
        getLogger('main').error('can not find /Data/apps/nginx/conf/ssl.conf')
        return
    try:
        nginx_port = output.split()[1].strip(';')
    except IndexError as e:
        getLogger('main').warning('config nginx port failed')
        return
    tmp = cmd.format(add_or_del='D', device=device, ports=ports, nginx_port=nginx_port, jump='ACCEPT')
    EXECUTE_CMD(tmp)
    tmp = cmd.format(add_or_del='D', device=device, ports=ports, nginx_port=nginx_port,
                     jump='LOG --log-prefix "ipt_log=ACCEPT "')
    EXECUTE_CMD(tmp)
    if allow:
        tmp = cmd.format(add_or_del='I', device=device,
                         ports=ports, nginx_port=nginx_port, jump='ACCEPT')
        EXECUTE_CMD(tmp)
        if log:
            tmp = cmd.format(add_or_del='I', device=device, ports=ports, nginx_port=nginx_port,
                             jump='LOG --log-prefix "ipt_log=ACCEPT "')
            EXECUTE_CMD(tmp)


def allow_ping(device, allow, version=4, log=False):
    """配置用于ping
    args：
        device: 网口名称
        allow: True or False
        version: 4 or 6, 代表ipv4还是ipv6
    """
    if version == 4:
        cmd = IPTABLES + ' -{add_or_del} FWINPUT -i {device} -p icmp --icmp-type echo-request -j {jump}'
    else:
        cmd = IP6TABLES + ' -{add_or_del} FWINPUT -i {device} -p icmpv6 -j {jump}'
    # tmp = cmd.format(add_or_del='D', device=device, jump='ACCEPT')
    # EXECUTE_CMD(tmp)
    # tmp = cmd.format(add_or_del='D', device=device, jump='LOG --log-prefix "ipt_log=ACCEPT "')
    # EXECUTE_CMD(tmp)
    add_or_del = {True: 'I', False: 'D'}[allow]
    tmp = cmd.format(add_or_del=add_or_del, device=device, jump='ACCEPT')
    EXECUTE_CMD(tmp)
    add_or_del = {True: 'I', False: 'D'}[allow and log]
    tmp = cmd.format(add_or_del=add_or_del, device=device, jump='LOG --log-prefix "ipt_log=ACCEPT "')
    EXECUTE_CMD(tmp)


def allow_web(device, allow, log=False):
    # get nginx port from nginx file
    tmp = r"cat %s|grep '^\s*listen\s*[0-9]\{1,5\}\;$'" % NGINX_FILE
    status, output = EXECUTE_CMD(tmp)
    if status:
        getLogger('main').error('can not find /Data/apps/nginx/conf/ssl.conf')
        return
    try:
        nginx_port = output.split()[1].strip(';')
    except IndexError as e:
        getLogger('main').warning('config nginx port failed')
        return
    cmd = (IPTABLES + ' -{add_or_del} FWINPUT -i {device} -p tcp -m multiport --dport {nginx_port},80 -j {jump}')
    # handle web iptables rules
    add_or_del = {True: 'I', False: 'D'}[allow]
    tmp = cmd.format(add_or_del=add_or_del, device=device,
                     nginx_port=nginx_port, jump='ACCEPT')
    EXECUTE_CMD(tmp)
    # handle log iptables rules
    add_or_del = {True: 'I', False: 'D'}[log and allow]
    tmp = cmd.format(add_or_del=add_or_del, device=device,
                     nginx_port=nginx_port, jump='LOG --log-prefix "ipt_log=ACCEPT "',)
    EXECUTE_CMD(tmp)


def allow_ssh(device, allow, log=False):
    # delete old iptables rule
    cmd = IPTABLES + ' -{add_or_del} FWINPUT -i {device} -p tcp -m multiport --dports 22 -j {jump}'
    # handle ssh iptables rule
    add_or_del = {True: 'I', False: 'D'}[allow]
    tmp = cmd.format(add_or_del=add_or_del, device=device, jump='ACCEPT')
    EXECUTE_CMD(tmp)
    # handle log iptables rule
    add_or_del = {True: 'I', False: 'D'}[log and allow]
    tmp = cmd.format(add_or_del=add_or_del, device=device, jump='LOG --log-prefix "ipt_log=ACCEPT "')
    EXECUTE_CMD(tmp)


def ip_addr(ip_obj, device, is_add=True):
    """add or del ipaddress
    args:
        ip_obj: MyIP类的实例
        device： 网口名称
        is_add： True or False
    """
    _map = {True: 'add', False: 'del'}
    ip_cmd = 'ip -{version:} addr {action:} {addr:} dev {device:}'
    status, output = EXECUTE_CMD(ip_cmd.format(version=ip_obj.version(),
                                                            action=_map[is_add],
                                                            addr=ip_obj.string,
                                                            device=device))
    if status:
        getLogger('main').warning('device `%s` ip config `%s` failed| %s', device, ip_obj.string, output)


class MyIP(IP):
    """自定义ip对象，用于储存ip地址和掩码"""
    def __init__(self, data, netmask):
        super(MyIP, self).__init__(data)
        self.addr = data
        self.int_mask = str(exchange_mask(netmask)) if self.version() == 4 else str(strmask_to_intv6(netmask))

    def __eq__(self, other):
        return super(MyIP, self).__eq__(other) and self.int_mask == other.int_mask

    def __repr__(self):
        return "MyIP('%s', '%s')" % (self.addr, self.int_mask)

    def __str__(self):
        return self.string

    @property
    def string(self):
        """输出192.168.1.1/24这种形式的的ip"""
        return '%s/%s' % (self.strNormal(1), self.int_mask)


class IfaceAddress(object):
    def __init__(self, data):
        for key, val in data.iteritems():
            setattr(self, key, val)
        self.sIPV4Address = self.sIPV4Address or ''
        self.sIPV6Address = self.sIPV6Address or ''
        self.all_ifaces = psutil.net_if_stats().keys()
        self.mode_num = NIC_WORKMODE.get(self.sWorkMode, '')
        self.manager_iface = json.loads(list(get_lines(MANAGE_NIC_PATH))[0])

    def config(self):
        """配置"""
        if self.sPortName not in self.all_ifaces:
            getLogger('main').warning('iface no found in devices')
            return
        if self.sPortName in self.manager_iface.keys():
            self.iStatus = '1'
            self.iWeb = '1'
            # self.iSSH = '1'
            # self.iByManagement = 1
            # self.iAllowPing = 1
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()
        static_route_recover(_type='boot_recover')  # 重配静态路由，防止ip变更时路由失效

    def disable(self):
        """禁用"""
        self._proc_ipset()
        net_cmd.device_down(self.sPortName)
        self._clean_up()
        self._proc_ping_manage()
        self._prepare_data()
        self._proc_workmode()
        self._proc_addresses()
        getLogger('main').info('iface `%s` down', self.sPortName)

    def enable(self):
        """启用"""
        self._proc_ipset()
        net_cmd.device_up(self.sPortName)
        self._clean_up()
        self._prepare_data()
        self._proc_flow()
        self._proc_workmode()
        self._proc_ping_manage()
        self._proc_addresses()

    def _prepare_data(self):
        """预处理一些数据，获得旧ip、待配置ip、保护管理口ip"""
        new_ips = set()
        for i in chain(self.sIPV4Address.split(','), self.sIPV6Address.split(',')):
            if i and i.strip():
                i = i.strip().split('/')
                new_ips.add(MyIP(i[0], i[1]))
        old_ips = psutil.net_if_addrs().get(self.sPortName, [])
        old_ips = {MyIP(i.address, i.netmask) for i in old_ips
                   if i.family in (2, 10) and '%' not in i.address}
        _same = new_ips & old_ips
        old_ips = old_ips - _same
        #if self.sPortName in self.manager_iface:
        #    manager_ip = self.manager_iface[self.sPortName].split('/')
        #    manager_ip = MyIP(manager_ip[0], manager_ip[1])
        #    new_ips.add(manager_ip)
        #    if manager_ip in old_ips: old_ips.remove(manager_ip)
        self.new_ips = new_ips
        self.old_ips = old_ips

    def _proc_ipset(self):
        """将启用网口的ip添加到一个ipset
        先将上次的所有网口的ip从ipset中删除，添加这次ip的到ipset中，更新nat_ip.txt文件
        """
        NAT_IP_PATH = '/usr/local/bluedon/tmp/nat_ip.txt'
        if not os.path.exists(NAT_IP_PATH):
            open(NAT_IP_PATH, 'w').close()

        for nat_ip in get_lines(NAT_IP_PATH, with_empty_line=False, is_strip=True):
            EXECUTE_CMD('/usr/local/sbin/ipset -D auth_local_mode %s'%nat_ip)

        # TODO(ruan.lj@foxmail.com): ipset ipv6.
        natip_data = select('select sIPV4Address from m_tbnetport where iStatus=1')
        with open(NAT_IP_PATH, 'w') as f_natip:
            nat_ip_string = ','.join([i['sIPV4Address'] for i in natip_data])
            nat_ip = [i.split('/')[0] for i in nat_ip_string.split(',') if '/' in i]
            for ip in nat_ip:
                EXECUTE_CMD('/usr/local/sbin/ipset -A auth_local_mode %s'%ip)
                print >> f_natip, ip

    def _proc_addresses(self):
        """删除旧ip，添加新ip"""
        if self.sPortName not in get_physical_ifaces():
            return
        for i in self.old_ips:
            ip_addr(i, self.sPortName, is_add=False)
        for i in self.new_ips:
            ip_addr(i, self.sPortName, is_add=True)
        getLogger('main').info('iface `%s` del_ip: %s ===> add_ip: %s',
                               self.sPortName, self.old_ips, self.new_ips)

    def _clean_up(self):
        """清除允许ping和用于管理的iptable规则"""
        # allow_manage(device=self.sPortName, allow=False, version=4, log=False)
        # allow_manage(device=self.sPortName, allow=False, version=6, log=False)
        allow_web(device=self.sPortName, allow=False, log=False)
        allow_ssh(device=self.sPortName, allow=False, log=False)
        allow_ping(device=self.sPortName, allow=False, version=4, log=False)
        allow_ping(device=self.sPortName, allow=False, version=6, log=False)
        getLogger('main').info('del_allow_manage and del_allow_ping')

    def _proc_flow(self):
        """允许流控配置"""
        if str(self.iAllowFlow) == '1':
            flow_cmd = '/home/ng_platform/bd_dpdk_warper/clients/tcs -I %s UP'
            status, output = EXECUTE_CMD(flow_cmd % self.sPortName)
            getLogger('main').info(flow_cmd, self.sPortName)
            if status:
                getLogger('main').error(output)

    def _proc_workmode(self):
        """工作模式配置"""
        if not self.sPortName.startswith('vEth'):
            return  # 只有vEth网卡支持工作模式
        mode_cmd = '/home/ng_platform/bd_dpdk_warper/clients/port_config %s %s'
        status, output = EXECUTE_CMD(mode_cmd % (self.sPortName, self.mode_num))
        getLogger('main').info(mode_cmd, self.sPortName, self.mode_num)
        if status:
            getLogger('main').error(output)

    def _proc_ping_manage(self):
        """允许ping和用于管理配置"""
        # mange = True if str(self.iByManagement) == '1' else False
        issh = True if str(self.iSSH) == '1' and str(self.iStatus) == '1' else False
        iweb = True if str(self.iWeb) == '1' and str(self.iStatus) == '1' else False
        ping = True if str(self.iAllowPing) == '1' and str(self.iStatus) == '1' else False
        log = True if str(self.iAllowLog) == '1' and str(self.iStatus) == '1' else False
        # allow_manage(self.sPortName, allow=mange, log=log)
        allow_ssh(self.sPortName, allow=issh, log=log)
        allow_web(self.sPortName, allow=iweb, log=log)
        allow_ping(self.sPortName, allow=ping, log=log)
        getLogger('main').info('config_iface: allow_ping `%s` allow_ssh `%s` allow_iweb `%s`',
                               self.iAllowPing, self.iSSH, self.iWeb)
        if self.sIPV6Address.split(','):
            # allow_manage(self.sPortName, allow=mange, version=6, log=log)
            allow_ping(self.sPortName, allow=ping, version=6, log=log)
            getLogger('main').info('config_iface: ipv6 allow_ping `%s` allow_ssh `%s` allow_iweb `%s`',
                                   self.iAllowPing, self.iSSH, self.iWeb)


def recover():
    """恢复网口配置"""

    with open(MANAGE_NIC_PATH, 'r') as f:
        manage_nic_info = f.read().strip()
        manage_nic_ip = json.loads(manage_nic_info)
        manage_nic = [ str(k) for k in json.loads(manage_nic_info).keys()]

    if sys.argv[1] == 'init':  # 开机恢复
        nic_config_info = select('select * from m_tbnetport')
    elif sys.argv[1] == 'reset':  # 恢复出厂设置
        manage_nic_format = str(manage_nic).replace('[','(').replace(']',')')
        nic_config_info = select("select * from m_tbnetport where sPortName in {}".format(manage_nic_format))
        nic_del = select("select sPortName from m_tbnetport where sPortName not in {}".format(manage_nic_format))
        for nic in nic_del:
            os.system('ip addr flush dev  %s'%nic['sPortName'])
            os.system('ifconfig %s down'%nic['sPortName'])
    else:
        return

    # 获得ha自动生成的ip，转换成MyIP对象
    ha_status = select_one('SELECT sValue FROM m_tbconfig WHERE sName="HaSetting"')
    ha_status = ha_status and json.loads(ha_status['sValue']).get('iTurn', 'stop') or 'stop'
    ha_infos = select('SELECT sNetCardName, sOutIP FROM m_tbdoublehot WHERE iStatus=1')
    ha_infos = {i['sNetCardName']: i['sOutIP'] for i in ha_infos}
    for iface, addrs in ha_infos.iteritems():
        addrs = addrs or ''
        ha_infos[iface] = set()
        for addr in addrs.split(','):
            if not addrs: continue
            try:
                ha_infos[iface].add(MyIP(addr.split('/')[0], addr.split('/')[1]))
            except ValueError as e:
                getLogger('main').error('wrong ha args | %s', e)
                print e

    # 如果网口表没有数据的情况下，只从管理口文件中获取ip
    if not nic_config_info:
        [os.system('ip addr flush dev %s' % k) for k in manage_nic]
        [os.system('ifconfig %s %s' % (key, value)) for key, value in manage_nic_ip.items()]
        # [allow_manage(device, allow=True) for device in manage_nic]
        # [allow_ssh(device, allow=True) for device in manage_nic]
        # [allow_ping(device, allow=True) for device in manage_nic]
        [allow_web(device, allow=True) for device in manage_nic]
        return

    for info in nic_config_info:
        try:
            iface = IfaceAddress(info)
            # 如果该网口做了ha的配置，从中排除ha相关ip
            if ha_status == 'start' and iface.sPortName in ha_infos:
                _tmp_set = {MyIP(addr.split('/')[0], addr.split('/')[1])
                            for addr in iface.sIPV4Address.split(',') if addr}
                _tmp_set = _tmp_set - ha_infos[iface.sPortName]
                iface.sIPV4Address = ','.join([i.string for i in _tmp_set])
            iface.config()
        except Exception as e:
            print e

if __name__ == '__main__':
    recover()
