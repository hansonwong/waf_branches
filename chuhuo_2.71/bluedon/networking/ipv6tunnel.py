#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
from commands import getstatusoutput
from abc import ABCMeta, abstractmethod
from logging import getLogger
from jinja2 import Template

from db.mysql_db import select, select_one
from networking.nat64 import exec_cmd


# pylint: disable=E1101

__author__ = 'ruan.lj@foxmail.com'

def _ip_tunnel(name, mode, remote, local, version=4):
    tunnel = 'ip -{version} tunnel add {name} mode {mode} ttl 255 local {local} remote {remote}'.format(
        name=name, mode=mode, remote=remote, local=local, version=version)
    up_tunnel = 'ip link set dev %s up' % name
    for cmd in [tunnel, up_tunnel]:
        getLogger('main').info(cmd)
        status, output = getstatusoutput(cmd)
        if status:
            getLogger('main').error(output)


def _ip_route(network, gateway='', device='', version=6):
    _cmd_tmp = Template('ip -{{version}} route add {{network}} '
                        '{% if gateway %} via {{gateway}} {% endif %} '
                        '{% if device %} dev {{device}} {% endif %} ')
    route_cmd = _cmd_tmp.render(network=network,
                                gateway=gateway,
                                version=version,
                                device=device)
    getLogger('main').info('add route for tunnel: %s', route_cmd)
    status, output = getstatusoutput(route_cmd)
    if status:
        getLogger('main').warning(output)


def _ip_addr(addr, dev, version=6):
    ip_cmd = 'ip -{version} addr add {addr} dev {dev}'.format(
        addr=addr, dev=dev, version=version)
    status, output = getstatusoutput(ip_cmd)
    if status:
        getLogger('main').error('add ip for tunnel faild: %s', output)
    getLogger('main').info(ip_cmd)


class TunnelBase(object):
    """IPV6隧道基类，抽象类，子类必须实现相关抽象方法"""

    __metaclass__ = ABCMeta

    def __init__(self, tunnel):
        for key, val in tunnel.iteritems():
            if isinstance(val, int):
                val = str(val)
            elif isinstance(val, basestring):
                val = val.strip()
            setattr(self, key, val)
        getLogger('main').info(self)

    def config(self):
        getLogger('main').info('config %s begin...', self.__class__.__name__)
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()

    def enable(self):
        self._add_tunnel()
        self._add_ip()
        self._add_route()
        self._add_iptables()

    def disable(self):
        self._add_iptables(is_add=False)
        _cmds = ('ip -6 route flush dev {dev}'.format(dev=self.sTunnalName),
                 'ip link set dev {dev} down'.format(dev=self.sTunnalName),
                 'ip tunnel del {dev}'.format(dev=self.sTunnalName))
        for cmd in _cmds:
            status, output = getstatusoutput(cmd)
            getLogger('main').info(cmd)
            if status:
                getLogger('main').error('error in disable tunnel: %s', output)

    @abstractmethod
    def _add_tunnel(self): pass

    @abstractmethod
    def _add_ip(self): pass

    @abstractmethod
    def _add_route(self): pass

    @abstractmethod
    def _add_iptables(self, is_add=True): pass


class GreTunnel(TunnelBase):
    """GRE隧道"""

    def _add_tunnel(self):
        _ip_tunnel(self.sTunnalName, 'gre',
                   self.sDuiduanPublicIP or 'any',
                   self.sBenduanPublicIP or 'any')

    def _add_ip(self):
        _ip_addr(addr=self.sLocalPointToPointIP,
                 dev=self.sTunnalName)

    def _add_route(self):
        for net in self.sTargetNetIP.split(','):
            # _ip_route(net, self.sDuiduanPointToPointIp, self.sTunnalName)
            _ip_route(net, '', self.sTunnalName)

    def _add_iptables(self, is_add=True):
        rules = ('iptables  -{is_add} FWINPUT -s {remote} -d {local} -p 47 -j ACCEPT;'
                 'ip6tables -{is_add} FWFORWARD -i {device} -j ACCEPT;'
                 'ip6tables -{is_add} FWFORWARD -o {device} -j ACCEPT')
        getstatusoutput(rules.format(is_add={True:'I', False:'D'}[is_add],
                                     remote=self.sDuiduanPublicIP,
                                     local=self.sBenduanPublicIP,
                                     device=self.sTunnalName))

        for local_net in self.sLocalNet.split(','):
            getstatusoutput('ip6tables -{is_add} FWINPUT -s {local_net} -j ACCEPT'.format(
                is_add={True:'I', False:'D'}[is_add],
                local_net=local_net))


class SixToFourTunnel(TunnelBase):
    """6to4隧道"""

    def _add_tunnel(self):
        _ip_tunnel(name=self.sTunnalName,
                   mode='sit',
                   remote=self.sDuiduanIP or 'any',
                   local=self.sBenduanPublicIP)

    def _add_ip(self):
        _ip_addr(addr=self.sTunnalIP,
                 dev=self.sTunnalName)

    def _add_route(self):
        _ip_route(network='2002::/16',
                  device=self.sTunnalName)

    def _add_iptables(self, is_add=True):
        rules = ('iptables  -{is_add} FWINPUT -d {local} -p 41 -j ACCEPT;'
                 'ip6tables -{is_add} FWINPUT -s {local_net} -j ACCEPT;'
                 'ip6tables -{is_add} FWFORWARD -i {device} -j ACCEPT;'
                 'ip6tables -{is_add} FWFORWARD -o {device} -j ACCEPT')
        getstatusoutput(rules.format(is_add={True:'I', False:'D'}[is_add],
                                     local=self.sBenduanPublicIP,
                                     local_net='2002::/16',
                                     device=self.sTunnalName))


class IsatapTunnel(TunnelBase):
    """isstap隧道"""

    def enable(self):
        super(IsatapTunnel, self).enable()
        self._conf_radvd()

    def disable(self):
        super(IsatapTunnel, self).disable()
        with open('/etc/radvd.conf', 'r+') as f:
            result = re.sub(r'interface\s+%s*?\n\{.*?\{.*?\};.*?\n\};.*?\n?' % self.sTunnalName, '', f.read(), flags=re.DOTALL)
            f.seek(0)
            f.write(result)
            f.truncate()
        _, output = getstatusoutput('service radvd restart')
        getLogger('main').info('restart service radvd: %s', output)

    def _add_tunnel(self):
        _ip_tunnel(name=self.sTunnalName,
                   mode='isatap',
                   remote=self.sDuiduanIP or 'any',
                   local=self.sLocalIP or 'any')

    def _add_ip(self):
        _ip_addr(addr=self.sTunnalIP,
                 dev=self.sTunnalName)

    def _add_route(self):
        _ip_route(network=self.sIsatapIpv6Prefix.strip(':')+'::/64',
                  device=self.sTunnalName)

    def _conf_radvd(self):
        with open('template/radvd', 'r') as fp:
            conf = Template(fp.read())
        with open('/etc/radvd.conf', 'a') as fp:
            fp.write(conf.render(name=self.sTunnalName,
                                 prefix=self.sIsatapIpv6Prefix.strip(':')))
        _, output = getstatusoutput('service radvd restart')
        getLogger('main').info('restart service radvd: %s', output)

    def _add_iptables(self, is_add=True):
        _sql = "SELECT sPortName FROM m_tbnetport WHERE sIPV4Address LIKE '%%{}/%%'".format(self.sLocalIP)
        iface = select_one(_sql)
        iface = iface.get('sPortName', '') if iface else ''
        rules = ('ip6tables -{is_add} FWINPUT -j ACCEPT;'
                 'ip6tables -{is_add} FWFORWARD -i {device} -j ACCEPT;'
                 'ip6tables -{is_add} FWFORWARD -o {device} -j ACCEPT;'
                 'iptables  -{is_add} FWINPUT -i {iface}  -j ACCEPT;'
                 'ip6tables -{is_add} FWINPUT -s fe80::/16 -j ACCEPT')
        getstatusoutput(rules.format(is_add={True:'I', False:'D'}[is_add],
                                     device=self.sTunnalName,
                                     iface=iface))


class FourOverSixTunnel(TunnelBase):
    """4over6隧道"""

    def disable(self):
        self._add_iptables(is_add=False)
        _cmds = ('ip route flush dev {dev}'.format(dev=self.sTunnalName),
                 'ip link set dev {dev} down'.format(dev=self.sTunnalName),
                 'ip -6 tunnel del {dev}'.format(dev=self.sTunnalName))
        for cmd in _cmds:
            status, output = getstatusoutput(cmd)
            getLogger('main').info(cmd)
            if status:
                getLogger('main').error('error in disable tunnel: %s', output)

    def _add_tunnel(self):
        _ip_tunnel(name=self.sTunnalName,
                   mode='ipip6',
                   remote=self.sDuiduanPublicIP or 'any',
                   local=self.sBenduanPublicIP or 'any',
                   version=6)

    def _add_ip(self):
        _ip_addr(addr=self.sLocalPointToPointIP,
                 dev=self.sTunnalName,
                 version=4)

    def _add_route(self):
        for net in self.sTargetNetIP.split(','):
            _ip_route(net, '', self.sTunnalName, version=4)

    def _add_iptables(self, is_add=True):
        rules = ('ip6tables  -{is_add} FWINPUT -s {remote} -d {local} -j ACCEPT;'
                 'iptables -{is_add} FWFORWARD -i {device} -j ACCEPT;'
                 'iptables -{is_add} FWFORWARD -o {device} -j ACCEPT')
        getstatusoutput(rules.format(is_add={True:'I', False:'D'}[is_add],
                                     remote=self.sDuiduanPublicIP,
                                     local=self.sBenduanPublicIP,
                                     device=self.sTunnalName))
        for local_net in self.sLocalNet.split(','):
            getstatusoutput('iptables -{is_add} FWINPUT -s {local_net} -j ACCEPT'.format(
                is_add={True:'I', False:'D'}[is_add],
                local_net=local_net))


class GreTunnelIPv4(TunnelBase):
    """IPv4 Gre 隧道"""

    def _add_tunnel(self):
        tunnel_cmd = ('ip tunnel add {name} mode gre remote {remote} {key} local {local} ttl 255 &&'
                      'ip link set dev {name} up')
        tunnel_cmd = tunnel_cmd.format(name=self.sTunnalName,
                                       remote=self.sDuiduanPublicIP,
                                       local=self.sBenduanPublicIP,
                                       key='key {}'.format(self.sKey) if self.sKey else '')
        exec_cmd(tunnel_cmd, msg='GreTunnelIPv4')

    def _add_ip(self):
        _ip_addr(addr=self.sLocalPointToPointIP,
                 dev=self.sTunnalName,
                 version=4)

    def _add_route(self):
        _ip_route(self.sDuiduanPointToPointIp, '', self.sTunnalName, version=4)
        for net in self.sTargetNetIP.split(','):
            _ip_route(net, '', self.sTunnalName, version=4)

    def _add_iptables(self, is_add=True):
        rules = 'iptables  -{is_add} FWINPUT -s {remote} -d {local} -p 47 -j ACCEPT'
        exec_cmd(rules.format(is_add={True:'I', False:'D'}[is_add],
                              remote=self.sDuiduanPublicIP,
                              local=self.sBenduanPublicIP))

    def disable(self):
        self._add_iptables(is_add=False)
        _cmds = 'ip link set dev {dev} down && ip tunnel del {dev}'.format(dev=self.sTunnalName)
        exec_cmd(_cmds, msg='GreTunnelIPv4')


def recover():
    """开机恢复与恢复出厂设置"""

    if len(sys.argv) == 1:
        return

    trans_map = {
        GreTunnel: select('select * from m_tbmannualset where iStatus=1'),
        SixToFourTunnel: select('select * from m_tbipv6toipv4 where iStatus=1'),
        IsatapTunnel: select('select * from m_tbisatap where iStatus=1'),
        FourOverSixTunnel: select('select * from m_tbipv4over6 where iStatus=1'),
        GreTunnelIPv4: select('select * from m_tbgreipv4 where iStatus=1'),
    }

    for ProcClass, datas in trans_map.items():
        for data in datas:
            if sys.argv[1] == 'factory_recover':
                data.iStatus = 0
                ProcClass(data).config()
            elif sys.argv[1] == 'boot_recover':
                ProcClass(data).config()


if __name__ == '__main__':
    # from utils.logger_init import get_logger
    # get_logger('main', 'log/for_test.log')
    recover()
