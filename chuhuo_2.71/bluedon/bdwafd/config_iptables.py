#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from logging import getLogger
from sqlalchemy import not_, or_, and_, distinct
from config import config
from wafddos import config_ddos
from common import insert_iptables_rule, del_iptables_rule
from db import (conn_scope, fw_engine, session_scope,
    Website, Session, WebsiteServers, get_config
)
from fwdb import Searitystrate, AddressList, NetPort, Bridgedevice


def init_iptables(reboot=False):
    '''
    初始化iptables
    '''
    if reboot:
        os.system('iptables -N WAFDDOS')  # ddos
        # os.system('iptables -N BRIDGE')  # 透明桥
        os.system('iptables -N BLACK_WHITE')  # 接入控制黑白名单
        os.system('iptables -N WEB-OUT')  # 非法外联
        os.system('iptables -N FWINPUT_WAF')
        os.system('iptables -N RPROXY_PORT')  # 反向代理本地监听端口
        os.system('iptables -N ADMINPORT')  # 管理口
        os.system('ipset create backlist hash:ip timeout 60')  # 拦截ip
        os.system('ipset create sitecheck hash:ip')   # 可用性检测
        os.system('ipset create proxy_ip hash:ip')   # 反向代理ip

        os.system('iptables -I INPUT -j FWINPUT_WAF')
        os.system('iptables -I INPUT -j RPROXY_PORT')
        os.system('iptables -I INPUT -j WAFDDOS')
        os.system('iptables -I INPUT -j ADMINPORT')
        os.system('iptables -I INPUT -m set --match-set backlist src -j DROP')
        os.system('iptables -I INPUT -p tcp -m set --match-set sitecheck src -j ACCEPT')
        os.system('iptables -I INPUT -j BLACK_WHITE')
        os.system('iptables -I INPUT -m set --match-set proxy_ip src -j ACCEPT')

        # os.system('iptables -I FORWARD -j BRIDGE') 
        os.system('iptables -I FORWARD -j WAFDDOS') 
        os.system('iptables -I FORWARD -m set --match-set backlist src -j DROP')
        insert_iptables_rule('filter', 'FORWARD', '-j WEB-OUT', ('SECURITYPOLICY',), 'before')

        os.system('iptables -A FWINPUT_WAF -p tcp --sport 25 -j ACCEPT')  # 应急支持邮件端口
        
    config_ddos('iptables', reboot)
    init_bridge_iptables()
    init_reverseproxy_iptables()


def init_tproxy_iptables():
    '''
    初始化透明代理iptables
    '''
    with conn_scope(**config['db']) as (conn, cursor):
        # 端口
        conf = get_config("BaseConfig")
        ports = conf["ports"]
        ports = filter(lambda x: x.strip(), ports.split('|'))
        conf = get_config("ByPass")
        is_bypass = conf["enable"]
    os.system('python /usr/local/bluedon/bdwafd/tproxy.py del')
    os.system('python /usr/local/bluedon/bdwafd/tproxy.py add ' + ' '.join(ports))
    if is_bypass:
        os.system('ebtables -t broute -F')


def add_default_strate(session):
    '''
    建桥时默认配置一条全通策略
    '''
    address = AddressList(id=1,
                          sAddressname='0.0.0.0',
                          sAddress='0.0.0.0',
                          sIPV='ipv4',
                          sNetmask='0.0.0.0',
                          sAddtype='1',
                          sMark='',
                          sIPJson='{"ipmaskrange_str": "0.0.0.0/0.0.0.0", "ipmaskrange_int": "0.0.0.0/0"}',)
    session.merge(address)  # ip组数据
    searitystrate = Searitystrate(id=1, sStrategyName='0.0.0.0', sInputPort='', sOutPort='',
            sSourceValue='1', iSourceType=1, sTargetValue='1', iTargetIPType=1, sMark='',
            sAppName='', iAction=1, iLog=0, iSort=1, iStatus=1, iOneway=0, sIPV='ipv4',
            sService='',)
    session.merge(searitystrate)   # 安全策略
    os.system('echo CMD_SAFE_STRATEGY >> /Data/apps/wwwroot/firewall/fifo/second_firewall.fifo')


def init_bridge_iptables():
    '''
    桥模式
    '''
    try:
        fw_session = Session(bind=fw_engine)
        add_default_strate(fw_session)
        fw_session.commit()
    except Exception, e:
        fw_session.rollback()
        getLogger('main').exception(e)
    finally:
        fw_session.close()
    os.system('python /usr/local/bluedon/bdwafd/weboutlog.py')  # web out


def init_reverseproxy_iptables():
    os.system('iptables -F RPROXY_PORT')
    os.system('ipset flush proxy_ip')
    with session_scope() as session:
        # add_proxy_local_port
        proxy_port = session.query(distinct(Website.iWebSitePort)).filter(Website.isproxy==1)
        proxy_port = map(lambda x: str(x[0]), proxy_port)
        if not proxy_port:
            return
        for i in range(0, len(proxy_port), 15):
            os.system('iptables -A RPROXY_PORT -p tcp -m multiport --dport %s -j ACCEPT'
                        % ','.join(proxy_port[i: i+10]))
        # add_proxy_ip
        proxy_ip = session.query(distinct(WebsiteServers.ip)).filter(and_(Website.isproxy==1,
                            Website.id==WebsiteServers.webSiteId)).all()
        for ip in proxy_ip:
            os.system('ipset add proxy_ip %s' % ip[0])


def add_admin_port_iptables(args):
    if not args:
        return
    cmd_str = 'iptables -{} ADMINPORT -p tcp -m multiport --dport {} -j ACCEPT'
    port_data = json.loads(args[1])
    action = 'I' if port_data['iWeb'] == '1' or port_data['iWeb'] == 1 else 'D' 
    os.system(cmd_str.format(action, '80,444'))

    action = 'I' if port_data['iSSH'] == '1' or port_data['iSSH'] == 1 else 'D' 
    os.system(cmd_str.format(action, '22'))


if __name__ == '__main__':
    # init_reverseproxy_iptables()
    init_bridge_iptables()