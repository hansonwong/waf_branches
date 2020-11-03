#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import sys
from sysinfo_tables import WafSessionManager
from systeminfo import getFormattedNicSetInfo, SystemInfo
from MySQL import MySQL
from config import config
from db import WafNicSet, WafRoute, session_scope, Dns,get_config
from nicsetting import ConfigAllNic, ConfigNic, ConfigAllRoute, InitNicSetTable
from logging import getLogger
from bridgesetting import ConfigAllBridge
from nginx import NginxConfGenerator, NginxController, init_tenv
from task import proc_nginx, proc_bypass, modify_syslog, setucarp, proc_setvlan, proc_reflash_nic, proc_port, proc_use_sysconfig_restore


# 网络接口恢复
#ConfigAllNic()
# 管理口恢复
#ConfigNic(["eth0"])
# 虚拟网桥恢复
#ConfigAllBridge()
# 路由配置恢复
#ConfigAllRoute()
# 反向代理恢复
# proc_nginx()
# 反向代理管理口恢复
def reverse_proxy():
    baseconfig = get_config("BaseConfig")
    if baseconfig["deploy"] == "reverseproxy":
        ConfigNic(["eth3"])

# BYPASS 设置恢复
# proc_bypass()
# SYSLOG配置恢复
# modify_syslog()
# HA参数设置恢复
# os.system("python /usr/local/bluedon/bdwafd/bducarp.py")


# DNS恢复
def dns_recover():
    with session_scope() as session:
        dns = session.query(Dns).one()
        if not dns.first and not dns.second:
            getLogger('main').warning('dns not set.')
            return
        with open('/etc/resolv.conf', 'w') as fp:
            if dns.first:
                fp.write('nameserver %s\n' % dns.first)
            if dns.second:
                fp.write('nameserver %s\n' % dns.second)


# vlan
# proc_setvlan()
# proc_reflash_nic()


def recover_waf():
    modify_syslog()
    proc_bypass()
    reverse_proxy()
    proc_nginx()
    ConfigAllRoute()
    ConfigAllBridge()
    ConfigNic(["eth0"])
    ConfigAllNic()
    dns_recover()
    proc_setvlan()
    proc_reflash_nic()
    os.system("python /usr/local/bluedon/bdwafd/wafddos.py")
    os.system("python /usr/local/bluedon/bdwafd/bducarp.py")
    proc_port()
    init_tenv()
    proc_use_sysconfig_restore()


if __name__ == "__main__":
    recover_waf()
