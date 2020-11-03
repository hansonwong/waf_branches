#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import sys
import commands
from logging import getLogger

from db.config import search_data
from utils.logger_init import logger_init

from IPy import IP

LOG_BASE_PATH = '/usr/local/bluedon/log/'
CMD_IPTABLES = "iptables"

SDNAT_CHAIN = {
            'SNAT': 'FWSNAT',
            'DNAT': 'FWDNAT',
            }

SDNAT_TABLE = {
            'SNAT': 'm_tbSnat',
            'DNAT': 'm_tbDnat',
            }


LOG_PATH = os.path.join(LOG_BASE_PATH, 'nat.log')

COMMANDS = commands.getstatusoutput

class ArgumentError(Exception):
    "The needed arg does not exist or not right"

def nat_str(nat_type, result):
    """
    NAT设置参数选项
    args:
        nat_type: 设置的nat类型[SNAT, DNAT]
        result: 表中记录
    return:
        log_str: 日记模式的拼接字符串
        cmd_str: 必须的拼接字符串
    """

    logger_init(nat_type, LOG_PATH, 'DEBUG')

    def ip_ipgroup(vtype, vid, sdtype):
        """
        args:
            vtype: ip(1)或ip组(2)
            vid: 相关连ip/ip组表的id
            sdtype: 源地址(s), 目的地址(d)
        return:
            istr: 拼接后的字符串
        """

        type_dict = {
            's': {
                'onlyip': ' -s %s ',
                'iprange': ' -m iprange --src-range %s-%s ',
                'ipgroup': ' -m set --match-set %s src '
                },
            'd': {
                'onlyip': ' -d %s ',
                'iprange': ' -m iprange --dst-range %s-%s ',
                'ipgroup': ' -m set --match-set %s dst '
                }
            }

        istr = u' '
        if vtype == '1':        # ip
            ip_sql = 'select sAddress, sNetmask, sAddtype from \
                    m_tbaddress_list where id=%d;' %(vid)
            data = search_data(ip_sql)
            if not data:
                getLogger(nat_type).debug('m_tbaddress_list table not id %d' %(vid))
                raise ArgumentError
            data = data[0]
            if str(data['sAddtype']).strip() == '1':        # ip和掩码形式
                if data['sAddress'].endswith('.0'):
                    if '.' not in data['sNetmask']:
                        addr = '%s/%s' %(data['sAddress'], data['sNetmask'])
                    else:
                        addr = IP('%s/%s' %(data['sAddress'], data['sNetmask']),
                                make_net=True).strNormal(1)
                else:
                    addr = data['sAddress']
                istr = type_dict[sdtype]['onlyip'] %(addr)
            elif str(data['sAddtype']).strip() == '2':        # ip段
                istr = type_dict[sdtype]['iprange']
                istr = istr %(data['sAddress'], data['sNetmask'])
        elif vtype == '2':     # ip组
            ipg_sql = 'select HideID from m_tbaddressgroup where id=%d;' %(vid)
            data = search_data(ipg_sql)
            if not data:
                getLogger(nat_type).debug('m_tbaddressgroup table not id %d' %(vid))
                raise ArgumentError
            data = data[0]
            istr = type_dict[sdtype]['ipgroup'] %(data['HideID'])
        return istr

    # 源ip
    sip_str = u' '
    if result['sSourceIP']:
        sip_str = ip_ipgroup(str(result['iSourceIPType']),
                            int(result['sSourceIP']), 's')

    # 目的ip
    dip_str = u' '
    if result['sTargetIP']:
        dip_str = ip_ipgroup(str(result['iTargetIPType']),
                            int(result['sTargetIP']), 'd')

    # 流出网口
    netport_str = u' '

    # 协议和源端口
    service_str = u' '
    if result['sService']:
        s_sql = 'select * from m_tbservices_list where id=%d;' \
                %(int(result['sService']))
        data = search_data(s_sql)
        if not data:
            getLogger(nat_type).debug('m_tbservices_list table not id %d'
                                      %(int(result['sService'])))
            return
        data = data[0]
        if data['sProtocol'] and str(data['sProtocol']).strip():
            service_str = ' -p %s ' %(data['sProtocol'].lower())

        def sdport(pvalue):
            """ 来源/目的端口 """
            if '-' in pvalue:
                low_high = pvalue.split('-')
                sdstr = ' -m multiport --sports %s:%s ' \
                        %(low_high[0], low_high[1])
            else:
                sdstr = ' -m multiport --sports %s ' %(pvalue)
            return sdstr

        if data['sSourcePort'] and str(data['sSourcePort']).strip():
            service_str = service_str + sdport(data['sSourcePort'])
        if data['sTargetPort'] and str(data['sTargetPort']).strip():
            service_str = service_str + sdport(data['sTargetPort'])\
                    .replace(' --s', ' --d')

    if nat_type == 'SNAT':
        # 转换的类型
        turntype_str = u' '
        flag = True
        if str(result['iConverType']).strip() == '1':        # 地址
            turntype_str = ' -j SNAT --to-source %s' \
                    %(result['sConverTypeValue'].strip())
        elif str(result['iConverType']).strip() == '3':        # 流出网口
            turntype_str = ' -o %s -j MASQUERADE ' %(result['sConverTypeValue'])
            flag = False

        # 源端口转换
        conver_to = u' '
        if (result['sSourcePortConverTo'] and
            str(result['sSourcePortConverTo']).strip()):
            if flag:
                conver_to = ':%s' %(str(result['sSourcePortConverTo']).strip())
            else:
                conver_to = ' --to-ports %s' \
                        %(str(result['sSourcePortConverTo']).strip())
        jstr = turntype_str + conver_to

        # 日志
        if flag:
            log_str = sip_str + dip_str + service_str + netport_str + \
                ' -j LOG --log-prefix "ipt_log=SNAT "'
        else:
            log_str = sip_str + dip_str + service_str + netport_str + \
                ' -j LOG --log-prefix "ipt_log=MASQUERADE "'

    elif nat_type == 'DNAT':
        # 流出网口
        if result['sNetport'] and str(result['sNetport']).strip():
            netport_str = ' -i %s ' %(str(result['sNetport']))

        # 注: 后台不支持192.168.1.0/24 掩码形式 必须单独ip
        dipto_str = ' -j DNAT --to-destination %s' \
                %(str(result['sTargetIPConverTo']).strip())
        # 目的端口转换
        if result['sTargetPortConverTo'] and (
            str(result['sTargetPortConverTo']).strip()):
            conver_to = ':%s' %(str(result['sTargetPortConverTo']).strip())
            dipto_str = dipto_str + conver_to
        jstr = dipto_str

        log_str = sip_str + dip_str + service_str + netport_str + \
                ' -j LOG --log-prefix "ipt_log=DNAT "'

    cmd_str = sip_str + dip_str + service_str + netport_str + jstr

    return (log_str, cmd_str)

def addnat(nat_type, data):
    """
    增加一条iptables规则
    args:
        nat_type: nat类型[SNAT, DNAT]
        data: 增加iptables规则的数据
    return:
        None
    """

    cmd_log, cmd_nat = nat_str(nat_type, data)

    cmd = '%s -t nat -A %s %s'
    if str(data['iLog']).strip() == '1':
        iptables_log = cmd %(CMD_IPTABLES, SDNAT_CHAIN[nat_type], cmd_log)
        #print iptables_log
        (status_log, output_log) = COMMANDS(iptables_log)
        getLogger(nat_type).debug('%s  %s' % (iptables_log, output_log))

    iptables_cmd = cmd %(CMD_IPTABLES, SDNAT_CHAIN[nat_type], cmd_nat)
    #print iptables_cmd
    (status_cmd, output_cmd) = COMMANDS(iptables_cmd)
    getLogger(nat_type).debug('%s  %s' %(iptables_cmd, output_cmd))

    os.system('/sbin/service iptables save')


def set_nat(nat_type, active='reboot'):
    """ 主函数 """

    os.system('%s -t nat -F %s' %(CMD_IPTABLES, SDNAT_CHAIN[nat_type]))
    if active == 'reboot':
        d_sql = 'select * from %s where iStatus=1 ORDER BY iSort;' \
                %(SDNAT_TABLE[nat_type])
        datas = search_data(d_sql)
        for data in datas:
            addnat(nat_type, data)

def main(active):
    for item in SDNAT_CHAIN:
        set_nat(item, active)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        #getLogger(LOG_NAME).debug('more args (eg: python -m firedam.nat init/reboot)')
        pass
    else:
        main(sys.argv[1])
    #print "nat well done"
