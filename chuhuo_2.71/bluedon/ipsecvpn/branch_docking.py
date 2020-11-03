#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
IPSEC VPN --> 分支对接
modify:
    2017-03-15:
        新添加f_iAuthStatus， f_iRandom验证
"""

import os
import sys
import time
from logging import getLogger

from netaddr import IPNetwork

from core.exceptions import ArgumentError
from db.mysql_db import select, select_one, update
from networking.config_bridge import get_tbconfig
from system.ha import init_tenv
from system.system_config import get_process_id
from utils.file_handling import empty_files

__author__ = "ruan.lj@foxmail.com"


PSK_PATH = '/usr/local/ipsec-vpn/etc/psk.txt'
SETKEY_PATH = '/usr/local/ipsec-vpn/etc/setkey.conf'
RACCOON_PATH = '/usr/local/ipsec-vpn/etc/raccoon.conf'

NEGOT_MODE = {
    1: 'main',  # 主模式
    2: 'aggressive',  # 快速模式
}

NAT_THROUGH = {
    1: 'on',
    0: 'off',
}

AUTH_TYPE = {
    1: 'pre_shared_key',  # 预共享密钥
    2: 'eccenv',  # 数字证书(x509)
}

SESSION_MODE = {
    1: 'tunnel',  # 隧道模式
    2: 'transport',  # 传输模式
}


def get_local_subnet(id_):
    ips = []
    ids = id_.split(',')
    for id in ids:
        data = select_one("SELECT sLocalChildIp, sLocalChildMask FROM m_tblocalchildnet WHERE id=?", id)
        if not data:
            raise ArgumentError('id %s nofound in m_tblocalchildnet' % id_)
        ip_ = IPNetwork('{}/{}'.format(data.sLocalChildIp, data.sLocalChildMask)).__str__()
        ips.append(ip_)
    return ips


def get_duiduan_subnet(id_):
    ips = []
    ids = id_.split(',')
    for id in ids:
        data = select_one("SELECT sDuiduanChildIp, sDuiduanChildMask FROM m_tbduiduanchildnet WHERE id=?", id)
        if not data:
            raise ArgumentError('id %s nofound in m_tbduiduanchildnet' % id_)
        ip_ =  IPNetwork('{}/{}'.format(data.sDuiduanChildIp, data.sDuiduanChildMask)).__str__()
        ips.append(ip_)
    return ips


def get_local_ip(id_):
    data = select_one("SELECT sIpaddresss FROM m_tbipsecoutnetport WHERE id=?", id_)
    if not data:
        raise ArgumentError('id %s nofound in m_tbipsecoutnetport' % id_)
    return data.sIpaddresss


def proc_branch():
    os.system('iptables -t nat -F IPSECVPN')
    result = select("SELECT * FROM m_tbipsec_branch WHERE iStatus=1")
    data = []
    for i in result:
        try:
            i.f_iNegotMode = NEGOT_MODE[i.f_iNegotMode]
            i.f_iNatThrough = NAT_THROUGH[i.f_iNatThrough]
            i.f_iAuthType = AUTH_TYPE[i.f_iAuthType]
            i.s_iSessionMode = SESSION_MODE[i.s_iSessionMode]
            i.local_ip = get_local_ip(i.sIpsecOutNetport)

            # 新添加f_iAuthStatus， f_iRandom
            i.f_iAuthStatus = str(i.f_iAuthStatus)
            i.f_iRandom = str(i.f_iRandom)

            if i.s_iSessionMode == "tunnel":
                i.s_iLocal = get_local_subnet(i.s_iLocal)
                i.s_iTarget = get_duiduan_subnet(i.s_iTarget)
            elif i.s_iSessionMode == 'transport':
                i.s_iLocal = [i.local_ip]
                i.s_iTarget = [i.f_sAddress]

            i.pfs_group = str(i.pfs_group)
        except (KeyError, ArgumentError) as e:
            getLogger('main').warning("wrong args!: %s| %s", e, i)
        else:
            data.append(i)
    listen_addrs = {i.local_ip for i in data}
    pem_files = get_tbconfig('IpsecBranchUpload')
    len1 = len(pem_files)
    os.system('/usr/bin/sh /usr/local/ipsec-vpn/ipsec-vpn_stop.sh')
    empty_files(RACCOON_PATH, SETKEY_PATH, PSK_PATH)
    if data:
        tenv = init_tenv()
        tenv.get_template('ipsec_raccoon').stream(data=data,
                                                  listen_addrs=listen_addrs, len1=len1,
                                                  pem_files=pem_files).dump(RACCOON_PATH)
        tenv.get_template('ipsec_setkey').stream(data=data).dump(SETKEY_PATH)
        tenv.get_template('ipsec_psk').stream(data=data).dump(PSK_PATH)

        os.system('/usr/bin/sh /usr/local/ipsec-vpn/ipsec-vpn_start.sh')

        # 过滤重复的规则
        tar = []
        for info in data:
            for target in info.s_iTarget:
                if target not in tar:
                    os.system('iptables -t nat -A IPSECVPN -d {} -j ACCEPT'.format(target))
                tar.append(target)

    time.sleep(2)
    if result and not get_process_id("/usr/local/ipsec-vpn/sbin/racoon -f"):
        getLogger("main").warning('start ipsecvpn failed')


def recover():
    if len(sys.argv) == 1:
        return

    if sys.argv[1] == 'factory_recover':
        os.system('/usr/bin/sh /usr/local/ipsec-vpn/ipsec-vpn_stop.sh')
        empty_files(RACCOON_PATH, SETKEY_PATH, PSK_PATH)
    if sys.argv[1] == 'boot_recover':
        proc_branch()

if __name__ == '__main__':
    recover()