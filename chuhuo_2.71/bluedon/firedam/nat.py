#!/usr/bin/env python
# coding=utf-8

"""
            2、修复关联服务源/目的端口区间或单个都表示为: -m multiport --sports/--dports %s
            1、无论增删改都先清空链再读表数据重新配置, 用-A不再用-I方式新增nat, 防止
               中途某一规则配置失败后, 后面的规则都配置失败
"""

import os
import sys
import commands
from logging import getLogger

from db.config import search_data
from utils.logger_init import logger_init
from core.exceptions import ArgumentError
from core.setting import CMD_IPTABLES, LOG_BASE_PATH
from db.mysql_db import select_one
from objectdefine.ip_range import deal_ip


del_log_dnat = []
SDNAT_CHAIN = {
    'SNAT': 'FWSNAT',
    'DNAT': 'FWDNAT'
}
SDNAT_TABLE = {
    'SNAT': 'm_tbSnat',
    'DNAT': 'm_tbDnat'
}

LOG_PATH = os.path.join(LOG_BASE_PATH, 'nat.log')
COMMANDS = commands.getstatusoutput
logger_init('SNAT', LOG_PATH, 'DEBUG')
logger_init('DNAT', LOG_PATH, 'DEBUG')


def ip_ipgroup(vtype, vid, sdtype, nat_type):
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
        data = select_one('select sAddress, sNetmask, sAddtype from \
                m_tbaddress_list where id=%d;' % (vid,))
        if not data:
            getLogger(nat_type).debug('m_tbaddress_list table not id {}'.format(vid))
            raise ArgumentError
        if str(data['sAddtype']).strip() == '1':        # ip和掩码形式
            addr, _ = deal_ip(data['sAddress'], data['sNetmask'])
            istr = type_dict[sdtype]['onlyip'] % addr
        elif str(data['sAddtype']).strip() == '2':        # ip段
            istr = type_dict[sdtype]['iprange'] % (data['sAddress'], data['sNetmask'])

    elif vtype == '2':     # ip组
        data = select_one('select HideID from m_tbaddressgroup where id=%d;' % (vid,))
        if not data:
            getLogger(nat_type).debug('m_tbaddressgroup table not id %d' % (vid,))
            raise ArgumentError
        istr = type_dict[sdtype]['ipgroup'] % (data['HideID'],)
    return istr


def get_service(result, nat_type):
    if result['sService'] is None or result['sService'] == '':
        data = {'sProtocol': '', 'sSourcePort': '', 'sTargetPort': ''}
        return data
    data = select_one('select * from m_tbservices_list where id=%d;' \
                % (int(result['sService'])))
    if not data:
         getLogger(nat_type).debug('m_tbservices_list table not id %d'
                % (int(result['sService'])))
         return
    return data


def source_destination(type_, ip_, s_d, nat_type):
    """
    根据传入的ip，ip类型，nat类型来构建对应的iptabes规则字符串
    """
    ip_str = ip_ipgroup(str(type_), int(ip_), s_d, nat_type) if ip_ else u''
    return ip_str


# 端口
def sdport(nat_type, port):
    """
    当选择了端口时，构造的iptables字符串
    把页面传过来类似'11-22'这种网口格式，转换为'11:22'这种格式
    """
    s_or_d = {
        'SNAT': 's',
        'DNAT': 'd'
    }
    port_iptables = ''
    if port and str(port).strip():
        port_iptables = ' -m multiport --{}port {}'.format(
            s_or_d[nat_type],
            str(port).replace('-', ':')
        )
    return port_iptables


def port_convert(pro, port, flag):
    """
    args:
        pro: 协议
        port: 需要转换的端口
        flag: 标志位
    """
    conver_to = u''
    if port and str(port).strip():
        if pro in ['tcp', 'udp']:
            fmts = ':{}' if flag else ' --to-ports {}'
            conver_to = fmts.format(str(port).strip())
    return conver_to


def type_convert(type_, value):
    """
    args:
        type_和Value的类型都是字符串
    """
    turn = netport = u''
    flag = True
    if type_ and str(type_).strip() == '1':
        turn = ' -j SNAT --to-source {}'.format(value.strip())
    elif str(type_).strip() == '3':
        flag = False
        turn = ' -o {} -j MASQUERADE '.format(value)
        netport = ' -o {}'.format(value)
    return flag, turn, netport


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

    # 源ip/目的ip
    sip_str = source_destination(
        result['iSourceIPType'], result['sSourceIP'], 's', nat_type)
    dip_str = source_destination(
        result['iTargetIPType'], result['sTargetIP'], 'd', nat_type)

    # 源端口或目的端口
    sport_str = sdport(nat_type, result['sSourcePort'])
    dport_str = sdport(nat_type, result['sTargetPort'])

    # 协议,当协议为icmp, ospf和gre时,nat规则没有端口
    service_str = u''
    if result['sService']:
        if result['sProtocol'] and str(result['sProtocol']).strip(','):
            service_str = ' -p {} '.format(result['sProtocol'].lower())
        pro = result.get('sProtocol', '').strip().lower()
        if pro not in ['icmp', '89', 'gre']:
            service_str = service_str + sport_str + dport_str

    # 流出网口
    netport_str = u''
    if nat_type == 'SNAT':
        # 标志位, 转换的类型为地址或流出网口, 不选日志时的流出网口
        flag, turntype_str, netport = type_convert(
                            result['iConverType'], result['sConverTypeValue'])

        # 源端口转换
        conver_to = port_convert(result['sProtocol'], result['sSourcePortConverTo'], flag)
        jstr = turntype_str + conver_to

        # 日志
        if flag:
            log_str = sip_str + dip_str + service_str + \
                ' -j LOG --log-prefix "ipt_log=SNAT "'
        else:
            log_str = sip_str + dip_str + service_str + netport + \
                ' -j LOG --log-prefix "ipt_log=MASQUERADE "'
        log_str = [log_str]
    elif nat_type == 'DNAT':
        # 流出网口
        netport_str = ' -i {} '.format(str(result['sNetport'])) if result.get(
                'sNetport', '').strip() else u''

        dipto_str = ' -j DNAT --to-destination {}'.format(
                str(result['sTargetIPConverTo']).strip())
        # 目的端口转换
        conver_to = port_convert(result['sProtocol'], result['sTargetPortConverTo'], True)
        jstr = dipto_str + conver_to

        log_str = sip_str + dip_str + service_str + netport_str + \
                ' -j LOG --log-prefix "ipt_log=DNAT "'


        log_forward = 'iptables -A FWFORWARD {sip} {dip} {pro_port} -m conntrack --ctstate DNAT -j LOG --log-prefix "ipt_log=DNAT "'\
                    .format(sip = sip_str,
                            dip = '-m iprange --dst-range %s'%result['sTargetIPConverTo'] if '-'in result['sTargetIPConverTo']
                                 else'-d %s' % str(result['sTargetIPConverTo']).strip(),
                            pro_port = service_str if not result['sTargetPortConverTo'] or 'icmp' in service_str
                                       else service_str.replace(dport_str,'-m multiport --dports %s'% str(result['sTargetPortConverTo'])))
        global del_log_dnat
        del_log_dnat.append(log_forward.replace('-A', '-D'))
        log_str = [log_str,log_forward]

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
    print 'log', cmd_log
    cmd = '%s -t nat -A %s %s'
    pro = data['sProtocol'].lower()
    if str(data['iLog']).strip() == '1':
        iptables_log = cmd %(CMD_IPTABLES, SDNAT_CHAIN[nat_type], cmd_log[0])
        (status_log, output_log) = COMMANDS(iptables_log)
        if nat_type=='DNAT':
            COMMANDS(cmd_log[1])
        getLogger(nat_type).debug('%s  %s' % (iptables_log, output_log))

    iptables_cmd = cmd % (CMD_IPTABLES, SDNAT_CHAIN[nat_type], cmd_nat)
    (status_cmd, output_cmd) = COMMANDS(iptables_cmd)
    getLogger(nat_type).debug('%s  %s' %(iptables_cmd, output_cmd))


def set_nat(nat_type, active='reboot'):
    """ 主函数 """

    global del_log_dnat
    for i in del_log_dnat:
        COMMANDS(i)

    os.system('%s -t nat -F %s' % (CMD_IPTABLES, SDNAT_CHAIN[nat_type]))
    if active == 'reboot':
        d_sql = 'select * from %s where iStatus=1 ORDER BY iSort;' \
                %(SDNAT_TABLE[nat_type])
        datas = search_data(d_sql)

        for data in datas:
            pro_s_d = get_service(data, nat_type)
            protocol = pro_s_d['sProtocol'].lower().split(',')
            data['sSourcePort'] = pro_s_d['sSourcePort']
            data['sTargetPort'] = pro_s_d['sTargetPort']
            for item in protocol:
                data['sProtocol'] = item.lower().strip()
                if data['sProtocol'] not in ['89', 'gre']:
                    if data['sProtocol'] == 'icmp':
                        data['sSourcePort'] = ''
                        data['sTargetPort'] = ''
                    addnat(nat_type, data)


def main(active):
    for item in SDNAT_CHAIN:
        set_nat(item, active)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        pass
    else:
        main(sys.argv[1])