#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from logging import getLogger
from itertools import groupby
from ConfigParser import ConfigParser
from sqlalchemy import and_
from config import config
from jinja2 import Environment, FileSystemLoader
from db import (conn_scope, session_scope, 
    fw_session_scope, Website, Session,
    get_config,
)
from fwdb import NetPort, Bridgedevice, Virtualline
from nginx import NginxController, NginxConfGenerator
from config_iptables import (init_iptables,
    add_admin_port_iptables, init_bridge_iptables,
)


class DeployMode(object):

    def __init__(self):
        self.mode_name = ''
        self.ngxconf = None

    def judge_mode_start(self):
        pass

    def _gen_mode_conf(self):
        if self.ngxconf:
            with session_scope() as session:
                self.ngxconf.gen_mod_rule_template(session)

    def start_mode(self):
        NginxController().restart(self.mode_name)

    def switch_nginx_and_conf(self):
        '''write conf and start/stop nginx'''
        self._gen_mode_conf()  # 配置文件都重写
        self.switch_nginx()

    def switch_nginx(self):
        '''start/stop nginx'''
        if self.judge_mode_start():
            self.start_mode()
        else:
            NginxController().stop(self.mode_name)


class BridgeMode(DeployMode):
    '''部署透明桥'''

    def __init__(self):
        super(BridgeMode, self).__init__()
        self.mode_name = 'bridge'
        self.ngxconf = NginxConfGenerator(config[self.mode_name]['conf_path'])

    def judge_mode_start(self):
        with fw_session_scope() as fw_session:
            brs = fw_session.query(Bridgedevice).filter(and_(Bridgedevice.iStatus==1,
                                         Bridgedevice.bridgeType=="bridge")).all()
            vls = fw_session.query(Virtualline).filter(Virtualline.iStatus==1).all()
            return brs or vls

    def _gen_mode_conf(self):
        super(BridgeMode, self)._gen_mode_conf()
        self.ngxconf.gen_nginx_bridge_proxy_conf()
        with session_scope() as session:
            self.ngxconf.genSecConf(session)


class VirlineMode(BridgeMode):
    '''部署虚拟线'''

    def __init__(self):
        super(VirlineMode, self).__init__()

    def judge_mode_start(self):
        with fw_session_scope() as fw_session:
            vls = fw_session.query(Virtualline).filter(Virtualline.iStatus==1).all()
            return bool(vls)


class TproxyMode(DeployMode):

    def __init__(self):
        super(TproxyMode, self).__init__()
        self.mode_name = 'tproxy'


class ReverseproxyMode(DeployMode):
    '''部署反向代理'''

    def __init__(self):
        super(ReverseproxyMode, self).__init__()
        self.mode_name = 'reverseproxy'
        self.ngxconf = NginxConfGenerator(config[self.mode_name]['conf_path'])

    def judge_mode_start(self):
        '''judge: 有反向代理站点，有nat/route模式的网卡'''
        with session_scope() as session:
            website = session.query(Website).filter(Website.isproxy==1).all()
            with fw_session_scope() as fw_session:
                workmodes = fw_session.query(NetPort.sWorkMode).filter(
                                NetPort.sPortName.like('vEth%')).all()
                return set([x[0] for x in workmodes]) & set(('nat', 'route')) and website

    def _gen_mode_conf(self):
        super(ReverseproxyMode, self)._gen_mode_conf()
        with session_scope() as session:
            self.ngxconf.genSecConf(session, False)
        self.ngxconf.gen_nginx_reverseproxy_conf()

    def start_mode(self):
        nginx_controller = NginxController()
        if nginx_controller.is_active(self.mode_name):
            nginx_controller.reload(self.mode_name)
        else:
            nginx_controller.start(self.mode_name)


def write_bridgeconf():
    '''写waf_bridge配置文件,桥/虚拟线模式时配置'''
    with fw_session_scope() as fw_session:
        vls = fw_session.query(Virtualline.sVirtualPortOne, Virtualline.sVirtualPortTwo
                                ).filter(Virtualline.iStatus==1).all()
        brs = fw_session.query(Bridgedevice.sBindDevices).filter(and_(
                Bridgedevice.bridgeType=="bridge", Bridgedevice.iStatus==1)).all()
        br_port = map(lambda p: 'vl {},{} 7'.format(p[0], p[1]), vls)
        br_port.extend(map(lambda x: 'br {} 8'.format(x[0]), brs))
    with open('/usr/local/bdwaf/conf/waf_bridge.conf', 'w') as f:
        f.write('\n'.join(br_port))


def write_filter_port():
    '''
    filter_port: 过桥/虚拟线nginx的网口
    format: 0|1|3|7
    modify: 修改网口模式,建透明代理桥时
    '''
    with fw_session_scope() as fw_session:
        workmodes = fw_session.query(NetPort.sPortName, NetPort.sWorkMode).filter(
                                            NetPort.sPortName.like('vEth%')).all()
        port_num = [int(filter(str.isdigit, str(port))) for port, workmode in workmodes
                            if workmode not in config['reverseproxy']['workmode']]
    write_bridgeini('|'.join(map(lambda x: str(x), sorted(port_num))))


def get_format_filter_port(port_num):
    '''format: 0-1|3-5|7-7'''
    format_ports = []
    for k, l in groupby(enumerate(sorted(port_num)), lambda (i, v): v - i):
        lst = [v for _, v in l]
        format_ports.append('%s-%s' % (lst[0], lst[-1]))
    return '|'.join(format_ports)


def write_bridgeini(format_filter_port):
    bridge_ini = '/usr/local/bdwaf/conf/bridge.ini'
    cf = ConfigParser()
    cf.read(bridge_ini)
    if format_filter_port != cf.get('mp_server', 'filter_data').strip():  # modify
        getLogger('main').info('bridge.ini: {}'.format(format_filter_port))
        cf.set('mp_server', 'filter_data', format_filter_port)
        with open(bridge_ini, 'w') as f:
            cf.write(f)


def switch_bdwaf():
    '''开关所有bdwaf'''
    BridgeMode().switch_nginx_and_conf()
    ReverseproxyMode().switch_nginx_and_conf()


def config_bridge_waf():
    '''建桥'''
    init_bridge_iptables()
    write_bridgeconf()
    BridgeMode().switch_nginx()


def config_virline_waf():
    '''建虚拟线'''
    write_bridgeconf()
    BridgeMode().switch_nginx()
    # VirlineMode().switch_nginx()


def config_port_waf(args=None):
    '''修改网口模式'''
    write_filter_port()
    BridgeMode().switch_nginx()
    ReverseproxyMode().switch_nginx()
    # add_admin_port_iptables(args)


def restart_bdwaf():
    BridgeMode().switch_nginx()
    ReverseproxyMode().switch_nginx()


def config_bypass(is_bypass):
    '''bypass设置'''
    bypass_conf_path = os.path.join(config['bridge']['conf_path'], 'waf_bypass.conf')
    os.system('echo {} > {}'.format(is_bypass, bypass_conf_path))  # bridge

    tenv = Environment(loader=FileSystemLoader('/usr/local/bluedon/bdwafd/data/template/'))
    tenv.get_template('modsecurity_enable').stream({'enable': 'Off' if int(is_bypass) else 'On'}).dump(
            os.path.join(config['reverseproxy']['conf_path'], 'modsecurity_enable.conf'))  # reverse proxy
    getLogger('main').info('switch bypass {}'.format(is_bypass))


def write_port_conf(args=None):
    '''检测端口'''
    baseconfig = get_config("BaseConfig")
    ports = baseconfig["ports"]
    os.system('echo "{}" > /usr/local/bdwaf/conf/waf_port.conf'.format(ports))


def init_all_conf():
    '''初始化各种conf'''
    write_bridgeconf()
    write_filter_port()
    write_port_conf()
    bypass = get_config("ByPass")
    config_bypass(bypass["enable"])


if __name__ == '__main__':
    init_all_conf()
    # config_bypass(1)
    # switch_bdwaf()
    # write_filter_port()
    # config_bridge_waf()
    # config_virline_waf()
    # config_port_waf()
