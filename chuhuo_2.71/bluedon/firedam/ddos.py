#!/usr/bin/env python
# coding=utf-8

"""
防火墙: DDOS设置

modify log
    2016-4-6:
        1、增加恢复系统默认设置选项
    2016-5-24：
        2、重构代码(pylint 5.86/befor 9.31/after)
        3、ddos开关切换到系统配置中
    2016-7-11:
        1、系统命令路径统一从 core.setting 中导入
        2、修复ddos总开关为False时报错bug
    2016-9-22:
        1、修复初始化时表[m_tbconfig]字段值为空时无法配置的bug
    2016-9-27:
        1、当用户修改ddos表单数据时, php发送指令(之前没有), 实时前后台统一
"""

import os
import sys
import json
import commands
from logging import getLogger

from db.config import search_data
from utils.logger_init import logger_init
from core.setting import LOG_BASE_PATH


CMD_DDOS = '/home/ng_platform/bd_dpdk_warper/clients/ddos_flag %s'
CMD_STR = '/home/ng_platform/bd_dpdk_warper/clients/ddos-ctl -dir source \
        -type %s -limit %s -state %s -log %s'

LOG_PATH = os.path.join(LOG_BASE_PATH, 'ddos.log')
LOG_NAME = 'DDOS'

logger_init(LOG_NAME, LOG_PATH, 'DEBUG')


def set_ddos(data):
    """
    ddos设置
    args:
        data: 配置文件数据
    return:
        True: 配置成功
        False: 配置失败
    """

    off_on = {'0': 'off', '1': 'on'}

    ddos_type = {
        'iArpAttack': 'arp_flood',
        'iUDPAttack': 'udp_flood',
        'iDNSAttack': 'dns_flood',
        'iSYNAttack': 'syn_flood',
        'iICMPAttack': 'icmp_flood',
        'iWinNuke': 'winnuke',
        'iTearDrop': 'teardrop',
        'iSmurf': 'smurf',
        'iLAND': 'land',
        'iICMP': 'jubo_icmp'
    }

    # 确保data中为ddos_type键的值都不为空，默认为'0'
    data['iLog'] = data.get('iLog', '0') or '0'
    for key in ddos_type:
        data[key] = data.get(key, '0') or '0'

    cmd_list = []
    log_type = off_on[str(data['iLog'])]
    # ARP洪水攻击防护
    cmd = CMD_STR %(ddos_type['iArpAttack'], data['iThreshold'],
                    off_on[data['iArpAttack']], log_type)
    cmd_list.append(cmd)
    # UDP洪水攻击防护
    cmd = CMD_STR %(ddos_type['iUDPAttack'], data['iUDPThreshold'],
                    off_on[data['iUDPAttack']], log_type)
    cmd_list.append(cmd)
    # DNS洪水攻击防护
    cmd = CMD_STR %(ddos_type['iDNSAttack'], data['iDNSThreshold'],
                    off_on[data['iDNSAttack']], log_type)
    cmd_list.append(cmd)
    # SYN洪水攻击防护
    cmd = CMD_STR %(ddos_type['iSYNAttack'], data['iSYNThreshold'],
                    off_on[data['iSYNAttack']], log_type)
    cmd_list.append(cmd)
    # ICMP洪水攻击防护
    cmd = CMD_STR %(ddos_type['iICMPAttack'], data['iICMPThreshold'],
                    off_on[data['iICMPAttack']], log_type)
    cmd_list.append(cmd)
    # WinNuke攻击防护
    cmd = CMD_STR %(ddos_type['iWinNuke'], '0', off_on[data['iWinNuke']], log_type)
    cmd_list.append(cmd)
    # TearDrop攻击防护
    cmd = CMD_STR %(ddos_type['iTearDrop'], '0', off_on[data['iTearDrop']], log_type)
    cmd_list.append(cmd)
    # LAND攻击防护
    cmd = CMD_STR %(ddos_type['iLAND'], '0', off_on[data['iLAND']], log_type)
    cmd_list.append(cmd)
    # 超大ICMP数据攻击防护
    cmd = CMD_STR %(ddos_type['iICMP'], '0', off_on[data['iICMP']], log_type)
    cmd_list.append(cmd)
    # Smurf攻击防护
    cmd = CMD_STR %(ddos_type['iSmurf'], '0', off_on[data['iSmurf']], log_type)
    cmd_list.append(cmd)


    # 是否启用DOS/DDOS防护服务
    (status, output) = commands.getstatusoutput(CMD_DDOS %('enable'))
    getLogger(LOG_NAME).debug(CMD_DDOS %('enable'))
    getLogger(LOG_NAME).debug(output)

    for item in cmd_list:
        (status, output) = commands.getstatusoutput(item)
        getLogger(LOG_NAME).debug(item)
        getLogger(LOG_NAME).debug(output)

    text = os.popen(CMD_DDOS %('status')).read()
    getLogger(LOG_NAME).debug(text)


def main(args):
    """ 主函数 """
    if args == 'reboot':
        c_sql = 'select sValue from m_tbconfig where sName="%s";'
        result = search_data(c_sql %('TimeSet'))
        if not result:
            getLogger(LOG_NAME).debug('m_tbconfig table not sName="%s"' %('TimeSet'))
            return
        result = result[0]['sValue']
        result = json.loads(result)
        iddos = result.get('iDDOS', 0) or 0
        if int(iddos) != 1:
            getLogger(LOG_NAME).debug('not start ddos!')
            return
        datas = search_data(c_sql %('DDosSetting'))
        if not datas:
            getLogger(LOG_NAME).debug('m_tbconfig table not sName="%s"' %('DDosSetting'))
            return
        datas = datas[0]['sValue']
        datas = json.loads(datas)
        set_ddos(datas)
    elif args == 'init':
        os.system(CMD_DDOS %('disable'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        getLogger(LOG_NAME).debug('more args eg: python ddos init/reboot')
    else:
        main(sys.argv[1])
    #print "ddos well done"
