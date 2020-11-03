#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import json
import commands
import subprocess
import time
from logging import getLogger

from utils.logger_init import get_logger
from db.mysql_db import select_one

get_logger('main', '/usr/local/bluedon/log/main.log', 'INFO')

# STD_OUT = None
STD_OUT = open(os.devnull, 'wb')  # the same as "> /dev/null"
STD_ERR = STD_OUT


def get_process_id(p_name):
    """get pid by process name"""
    processes = commands.getoutput(r"ps -aux |grep -v 'grep\|/bin/sh'|grep '%s'" % p_name)
    if processes:
        return [int(line.split()[1]) for line in processes.split('\n')]


def _switch_action(action, turn_on, turn_off):
    cmd = turn_on if action == '1' else turn_off
    try:
        subprocess.call(cmd, shell=True, stdout=STD_OUT, stderr=STD_ERR)
    except subprocess.CalledProcessError as e:
        getLogger('main').error('system_config: %s', e)


def smart_protect_switch(action):
    u"""智能防护引擎"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./use_kernel on'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./use_kernel off'
    _switch_action(action, turn_on, turn_off)


def waf_switch(action):
    """waf开关"""
    subprocess.call('killall -9 bdwaf', shell=True, stdout=STD_OUT, stderr=STD_ERR)
    os.system('echo 0 > /usr/local/bdwaf/conf/waf_on.conf')
    if action == '1':
        time.sleep(2)
        os.system('echo 1 > /usr/local/bdwaf/conf/waf_on.conf')
        subprocess.call('/usr/local/bdwaf/sbin/bdwaf', shell=True, stdout=STD_OUT,
                        stderr=STD_ERR)


def waf_webapp_detect(action):
    """waf-web应用检测引擎"""

    trans_map = {
        '1': 'SecRuleEngine On',
        '0': 'SecRuleEngine Off'
    }

    on_off = trans_map.get(action, '')
    if not on_off: return
    with open('/usr/local/bdwaf/conf/modsecurity.conf', 'r+') as f:
        result = re.sub(r'^SecRuleEngine\s+\w+', on_off, f.read(), flags=re.MULTILINE)
        f.seek(0)
        f.write(result)


def waf_url_filter(action):
    """waf-url过滤"""
    with open('/usr/local/bdwaf/conf/waf_url.conf', 'w') as conf:
        conf.write(action)


def ips_switch(action):
    """ips开关
    /home/suricata/bin/suricata -c /etc/suricata/suricata.yaml --dpdk  --pidfile /var/run/suricata.pid> /dev/null 2>&1
    """
    turn_on = 'systemctl start ips'
    turn_off = 'systemctl stop ips'
    _switch_action(action, turn_on, turn_off)


def flow_manage_switch(action):
    u"""流量管理"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./tcs -T on'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./tcs -T off'
    _switch_action(action, turn_on, turn_off)


def ddos_protect_switch(action):
    u"""DDOS 防御"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./ddos_flag enable'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./ddos_flag disable'
    if action == '1':
        subprocess.call('python -m firedam.ddos reboot', shell=True,
                        stdout=STD_OUT, stderr=STD_ERR)
    else:
        _switch_action(action, turn_on, turn_off)


def dpi_switch(action):
    u"""深度检测报文内容就检测引擎（DPI）"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./dpi_mgr enable'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./dpi_mgr disable'
    _switch_action(action, turn_on, turn_off)


def traffic_count(action):
    """流量统计"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/traffic_count_flag enable'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/traffic_count_flag disable'
    if action == '1':
        os.system('touch /etc/ts_flag')
    else:
        os.system('rm -f /etc/ts_flag')
    _switch_action(action, turn_on, turn_off)


def info_leak_switch(action):
    u"""信息泄露防护"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./key_word_filter on'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./key_word_filter off'
    _switch_action(action, turn_on, turn_off)


def anti_virus_switch(action):
    u"""病毒防护"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./virus on'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./virus off'
    _switch_action(action, turn_on, turn_off)

def audit_switch(action):
    u"""上网行为审计"""
    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./fwaudit on'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./fwaudit off'
    _switch_action(action, turn_on, turn_off)


def net_share_detect_switch(action):
    """共享上网检测"""
    with open('/usr/local/bdwaf/conf/waf_wifi_audit.conf', 'w') as conf:
        conf.write(action)  # 写入waf配置


def anti_virus_fast_scan(action):
    u"""病毒防护 - 快速扫描（不属于系统配置）"""

    turn_on = '/home/ng_platform/bd_dpdk_warper/clients/./virus_fast on'
    turn_off = '/home/ng_platform/bd_dpdk_warper/clients/./virus_fast off'
    _switch_action(action, turn_on, turn_off)


def brige_brocast_snat(action):
    """
    桥模式下，组播不走snat
    """
    CMD = 'iptables -t nat {} FWPOSTROUTING {} 225.0.0.0/8 -j ACCEPT'
    os.system(CMD.format('-D', '-s'))
    os.system(CMD.format('-D', '-d'))
    if action == '1':
        os.system(CMD.format('-A', '-s'))
        os.system(CMD.format('-A', '-d'))


def set_time(data):
    os.system(r'/usr/bin/sed -i "/# sync system time\>/"d %s' %('/etc/crontab'))  # 删除旧的crontab
    os.system('/usr/bin/ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')  # 默认时区为cst
    hw = '/usr/sbin/hwclock -w'
    hws = '/usr/sbin/hwclock -s'

    os.system("iptables -D FWINPUT -p tcp -m tcp --sport 53 -j ACCEPT;"
              "iptables -D FWINPUT -p udp -m udp --sport 53 -j ACCEPT;"
              "iptables -D FWINPUT -p tcp -m tcp --sport 123 -j ACCEPT;"
              "iptables -D FWINPUT -p udp -m udp --sport 123 -j ACCEPT;")

    if str(data['setType']) == '1':  # 手动设定系统时间
        # if '-' in data['sTimeZone']:
        #     Etc_timezone = data['sTimeZone'].replace('-', '+')
        # else:
        #     Etc_timezone = data['sTimeZone'].replace('+', '-')
        # time_path = '/usr/share/zoneinfo/Etc/%s' %(Etc_timezone)
        # os.system('/usr/bin/ln -sf %s /etc/localtime' %(time_path))  # 设置时区
        os.system('date -s "%s"' %data['sDateTime'])  # 设置系统时间

    elif str(data['setType']) == '2':  # NTP时间设定
        if str(data['iGetBy']) == '1':
            cmd = '/usr/sbin/ntpdate -u %s' %(data['sTimeServerIP'])
            os.system("iptables -A FWINPUT -p tcp -m tcp --sport 123 -j ACCEPT;"
                      "iptables -A FWINPUT -p udp -m udp --sport 123 -j ACCEPT;")
        elif str(data['iGetBy']) == '2':
            cmd = '/usr/sbin/ntpdate -u %s' %(data['sDomainName'])
            os.system("iptables -A FWINPUT -p tcp -m tcp --sport 53 -j ACCEPT;"
                      "iptables -A FWINPUT -p udp -m udp --sport 53 -j ACCEPT;"
                      "iptables -A FWINPUT -p tcp -m tcp --sport 123 -j ACCEPT;"
                      "iptables -A FWINPUT -p udp -m udp --sport 123 -j ACCEPT;")
        else:
            return

        try:
            subprocess.check_call(cmd, shell=True, stdout=STD_OUT, stderr=STD_ERR)
        except subprocess.CalledProcessError as e:
            getLogger('main').error('set_time: %s| error: %s', cmd, e)

        # 定期同步时间
        with open('/etc/crontab', 'a') as fp:
            sync_minute = int(data['iTimeDiff'])
            h, m = divmod(sync_minute, 60)
            if h == 0:
                line = '*/%s * * * * root %s && %s && %s        # sync system time\n' % (m or '', cmd, hw, hws)
            elif h >= 1:
                line = '*/%s */%s * * * root %s && %s && %s      # sync system time\n' % (m or '', h, cmd, hw, hws)
            else:
                line = ''
            fp.write(line)
    else:
        return
    os.system(hw)
    os.system(hws)
    os.system('systemctl restart crond.service')


def sys_config_processer(data):
    switch_map = [
        ("iWeburl", waf_url_filter),  # waf配置
        ("iWebeng", waf_webapp_detect),  # waf配置
        ("iShare", net_share_detect_switch),  # waf网中网检测
        ("iWAF", waf_switch),  # 启动waf在更改配置之后
        ("iDeepEngine", smart_protect_switch),
        ("iFLOW", flow_manage_switch),
        ("iDDOS", ddos_protect_switch),
        ("iDPI", dpi_switch),
        ("iFlowAccount", traffic_count),
        ("iIPS", ips_switch),
        ("iLEAK", info_leak_switch),
        ("iVIRUES", anti_virus_switch),
        ("iAudit", audit_switch),
        ("iNSNAT", brige_brocast_snat),
    ]

    if str(data.get('iIPS', '')) == '0':
        data['iLEAK'] = '0'
        data['iVIRUES'] = '0'
    for s_type, switcher in switch_map:
        if s_type in data:
            action = str(data[s_type])
            switcher(action)
            getLogger('main').info('system_config: %s | args: %s',
                                   switcher.__name__, action)


def restore_sys_config():
    sql = 'SELECT sValue FROM m_tbconfig WHERE sName="TimeSet";'
    config_data = select_one(sql)
    if config_data:
        config = json.loads(config_data['sValue'])
        sys_config_processer(config)


if __name__ == '__main__':
    restore_sys_config()
