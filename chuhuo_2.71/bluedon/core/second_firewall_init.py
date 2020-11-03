#! /usr/bin/env python
# -*- coding:utf-8 -*-

import commands
import os
import sys
import time
from logging import  getLogger

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

while 1:

    (status, output_mp) = commands.getstatusoutput('ps -ef |grep mp_server |grep -v grep |wc -l')
    (status, output_kni) = commands.getstatusoutput('ps -ef |grep kni |grep -v grep | wc -l')
    (status, output_mpsql) = commands.getstatusoutput('ps -ef|grep mysqld|grep -v grep|wc -l')
    (status, output_init) = commands.getstatusoutput('ps -ef |grep second_firewall_init.py |grep -v grep | wc -l')

    if int(output_init) > 1 :
       exit(0)

    if (int(output_mp) and int(output_kni) and int(output_mpsql) >= 4 and
        os.path.exists('/tmp/mysql3306.sock') and os.path.exists('/tmp/mysql3307.sock')):
        print "mp_server  mysql"
        break
    else:
        time.sleep(1)

from core.iptables_init import iptables_init
from networking.fwdb import insert_interfaces
from db.mysqlconnect import mysql_connect_dict
from utils.logger_init import logger_init
from utils.app_mark_count import default_scount_field
from collections import OrderedDict
MANAGE_NIC_PATH = '/etc/network_config/mgt_nic.txt'


def firewall_init():

    logger_init('main','/usr/local/bluedon/log/main.log','INFO')

    getLogger('main').info('second firewall init begine.........')


    # disable and stop sshd
    # os.system('systemctl disable sshd.service')
    # getLogger('main').info('disable sshd...........')
    # os.system('systemctl stop sshd.service')
    # getLogger('main').info('stop sshd...........')

    #with open(MANAGE_NIC_PATH,'r') as f:
    #     manage_ip = eval(f.read().strip('\n'))
    #     for key,value in manage_ip.items():
    #         os.system('ifconfig %s %s'%(key,value))

    os.system('/usr/sbin/iptables -t mangle -F APPMARK')
    default_scount_field()

    iptables_init('iptables')
    iptables_init('ip6tables')
    #insert_interfaces()

    init_function = OrderedDict()

    #网络设置
    init_function['nic']               = 'python -m networking.config_iface init'
    init_function['port_mirror']       = 'python -m networking.reply_mirror'
    init_function['virtual_line']      = 'python -m networking.virtual_line boot_recover'
    init_function['bridge']            = 'python -m networking.config_bridge boot_recover'
    init_function['ppoe']              = 'python -m networking.pppoe boot_recover'
    init_function['port_aggregation']  = 'python -m networking.iface_aggregation boot_recover'
    init_function['VLAN']              = 'python -m networking.config_vlan boot_recover'
    init_function['static_route']      = 'python -m networking.route boot_recover'
    init_function['sslvpn']            = 'python /usr/local/bluedon/sslvpn/sslvpn.py boot_recover'
    #init_function['strategy_route']    = 'python -m networking.config_strategy_route reboot'    # 策略路由
    init_function['strategy_route']    = 'python -m networking.tactics_route reboot'    # 精简版策略路由
    init_function['isp_route']         = 'python -m networking.isp_route reboot'
    init_function['dynamic_route']     = 'python -m networking.backup_dynamicroute'
    init_function['dhcp']              = 'python -m networking.dhcp'
    init_function['dns']               = 'python -m networking.dns'
    init_function['nginx']             = 'python -m networking.set_nginx'
    init_function['best_routing']      = 'python -m networking.best_routing boot_recover'

    #IP组
    init_function['IP_group']          = 'python -m objectdefine.set_ipgroup reboot'

    #系统配置
    init_function['snmp']              = 'python -m system.config_snmp'
    init_function['nets_within_nets']  = 'python -m system.nets_within_nets boot_recover'
    init_function['multicast_route']   = 'python -m system.multicast_route boot_recover'

    #防火墙
    init_function['nat']               = 'python -m firedam.nat reboot'
    init_function['safetactics']       = 'python -m firedam.safe_tactics reboot'
    init_function['scm']               = 'python -m scm.scm_strategy_load'
    init_function['ddos']              = 'python -m firedam.ddos reboot'
    init_function['connect_limit']     = 'python -m firedam.connlimit'
    init_function['ipmac']             = 'python -m firedam.ipmac'
    init_function['virtualfw']         = 'python -m firedam.virtual_fw boot_recover'

    #安全防护
    init_function['IPS']               = 'python -m safetydefend.IPS_defined'
    init_function['WEB']               = 'python -m safetydefend.web'
    # init_function['url_filter']        = 'python -m safetydefend.url_filter reboot'
    init_function['url_group']         = 'python -m objectdefine.url_group reboot'
    init_function['eml_virus']         = 'python -m safetydefend.filter'
    init_function['file_filter']       = 'python -m safetydefend.file_filter'
    init_function['keyword_filter']    = 'python -m safetydefend.keyword_filter'
    init_function['web_keyword']       = 'python -m safetydefend.web_content_keyword'
    init_function['url_filter_strategy'] = 'python -m safetydefend.url_filter_strategy'
    init_function['url_filter_list'] = 'python -m safetydefend.url_list_filter'

    # 防病毒配置
    init_function['antivirus_config'] = 'python -m antivirus.antivirus_config'
    init_function['antivirus_strategy'] = 'python -m antivirus.antivirus_strategy'

    #用户管理
    init_function['usergroup']        = 'python -m usermanage.user_group reboot'
    #init_function['tactics']        = 'python -m usermanage.tactics reboot'

    #流量管理
    init_function['flowmanage']        = 'python -m flowmanage.flow_manage reboot'
    init_function['system_config']     = 'python -m system.system_config'
    init_function['system_reboot_log'] = 'python -m reportlog.system_reboot_log'
    #SSLVPN
    #init_function['sslvpn']            = 'python /usr/local/bluedon/sslvpn/vpn.py boot_recover'

    #ipv6隧道
    init_function['ipv6']              = 'python -m networking.ipv6tunnel boot_recover'

    #ipsecvpn
    init_function['ipsecvpn']          ='python -m ipsecvpn.branch_docking boot_recover'
    init_function['n2n-vpn']           ='python ipsecvpn.n_to_n boot_recover'

    #nat64
    init_function['nat64']             = 'python -m networking.nat64 boot_recover'
    init_function['vifaces']             = 'python -m networking.viface_recover'
    init_function['honypot']           = 'python -m smartdefend.honeypot'

    for k , v in  init_function.items():
        try:
            print k
            getLogger('main').info('%s'%k)
            (status,output) = commands.getstatusoutput(v)
        except Exception as e:
            print e
    os.system('python -m system.ha')
    os.system('/usr/sbin/hwclock -s')
    os.system('python -m usermanage.tactics onoff_reboot')
    os.system('python -m usermanage.tactics reboot')
    os.system('python -m networking.ip_monitor boot_recover')
    insert_interfaces()

    getLogger('main').info('second firewall init end.........')


if __name__=="__main__":
    firewall_init()
