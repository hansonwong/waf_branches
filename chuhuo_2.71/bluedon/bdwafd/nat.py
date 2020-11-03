#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import sys
import commands
import logging
from logging import getLogger, handlers

from IPy import IP
from MySQL import MySQL
from config import config

LOG_BASE_PATH = '/usr/local/bluedon/bdwafd/log/'
CMD_IPTABLES = "iptables"

SDNAT_CHAIN = {
            'SNAT': 'FWSNAT',
            'DNAT': 'FWDNAT',
            }

SDNAT_TABLE = {
            'SNAT': 't_snat',
            'DNAT': 't_dnat',
            }


LOG_PATH = os.path.join(LOG_BASE_PATH, 'nat.log')

COMMANDS = commands.getstatusoutput


def logger_init(name, filepath, level=logging.DEBUG):
    LOG_LEVEL = logging.NOTSET
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL or level)
    ch = logging.FileHandler(filepath)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

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
    db = MySQL(config['db'])

    logger_init(nat_type, LOG_PATH, 'DEBUG')

    def ip_ipgroup(sdtype, data):
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
                'ipgroup': ' -m set --match-set %s dst ',
                'port':' --dport %s',
                'protocol': ' -p %s'
                }
            }

        istr = u' '
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
        if data.get('tProtocol'):                           # 加入端口支持必须的协议 10/16/17
            prostr = type_dict[sdtype]['protocol'] % data['tProtocol']
            istr += prostr
        if data.get('sPort'):                           # 加入端口支持 9/19/17
            portstr = type_dict[sdtype]['port'] % data['sPort']
            istr += portstr
        return istr

    # 源ip
    sip_str = u' '
    if result['sourceAddress']:
        sip_str = ip_ipgroup('s', 
            {"sAddress": result["sourceAddress"],
             "sNetmask": result["sourceNetmask"],
             "sAddtype": result["sourceAddresstype"]
             })

    # 目的ip
    dip_str = u' '
    if result['targetAddress']:
        dip_str = ip_ipgroup('d', 
            {"sAddress": result["targetAddress"],
             "sNetmask": result["targetNetmask"],
             "sAddtype": result["targetAddresstype"],
             'sPort':result.get("targetPort"),          # 加入端口支持 9/19/17
             'tProtocol':result.get('targetProtocol')   # 加入端口必须带协议 10/16/17
            })

    # 流出网口
    netport_str = u' '

    # 协议和源端口
    service_str = u' '

    if nat_type == 'SNAT':
        # 转换的类型
        turntype_str = u' '
        flag = True
        if str(result['converType']).strip() == '1':        # 地址
            turntype_str = ' -j SNAT --to-source %s' \
                    %(result['converTypeValue'].strip())
        elif str(result['converType']).strip() == '3':        # 流出网口
            turntype_str = ' -o %s -j MASQUERADE ' %(result['converTypeValue'])
            flag = False

        # 源端口转换
        conver_to = u' '
        '''
        if (result['sSourcePortConverTo'] and
            str(result['sSourcePortConverTo']).strip()):
            if flag:
                conver_to = ':%s' %(str(result['sSourcePortConverTo']).strip())
            else:
                conver_to = ' --to-ports %s' \
                        %(str(result['sSourcePortConverTo']).strip())
        '''
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
        if result['nicName'] and str(result['nicName']).strip():
            netport_str = ' -i %s ' %(str(result['nicName']))

        # 注: 后台不支持192.168.1.0/24 掩码形式 必须单独ip
        dipto_str = ' -j DNAT --to-destination %s' \
                %(str(result['targetIpConverTo']).strip())

        jstr = dipto_str

        # 加入端口支持  9/19/17
        if result['targetPortConverTo'].strip():
            jstr += ':%s' % result['targetPortConverTo']

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
    getLogger('main').info('nat cmd: %s' % cmd_nat)
    cmd = '%s -t nat -A %s %s'
    if str(data['isLog']).strip() == '1':
        iptables_log = cmd %(CMD_IPTABLES, SDNAT_CHAIN[nat_type], cmd_log)
        print iptables_log
        (status_log, output_log) = COMMANDS(iptables_log)
        getLogger(nat_type).debug('%s  %s' % (iptables_log, output_log))

    iptables_cmd = cmd %(CMD_IPTABLES, SDNAT_CHAIN[nat_type], cmd_nat)
    print iptables_cmd
    (status_cmd, output_cmd) = COMMANDS(iptables_cmd)
    getLogger(nat_type).debug('%s  %s' %(iptables_cmd, output_cmd))

    #os.system('/sbin/service iptables save')


def delete_nat(nat_type=None):
    if not nat_type:
        os.system('%s -t nat -F' %(CMD_IPTABLES))
    else:
        os.system('%s -t nat -F %s' %(CMD_IPTABLES, SDNAT_CHAIN[nat_type]))

def set_nat(nat_type="DNAT", active='reboot'):
    """ 主函数 """
    db = MySQL(config['db'])

    #os.system('%s -t nat -F %s' %(CMD_IPTABLES, SDNAT_CHAIN[nat_type]))
    delete_nat(nat_type)
    if active == 'reboot':
        d_sql = 'SELECT * FROM %s WHERE status=1 ORDER BY sort;' \
                %(SDNAT_TABLE[nat_type])
        db.query(d_sql)
        for data in db.fetchAllRows():
            addnat(nat_type, data)
    db.close()


def set_all_nat():
    for item in SDNAT_CHAIN:
        set_nat(item)


def write_nat_conf(switch):
    '''
    write nat config /etc/sysctl.conf
    '''
    os.system('sed -i "/net.ipv4.ip_forward/d" /etc/sysctl.conf')
    os.system('sed -i "/net.ipv4.conf.all.proxy_arp/d" /etc/sysctl.conf')
    is_use = 1 if switch else 0
    os.system('echo "net.ipv4.ip_forward = %s" >> /etc/sysctl.conf' % is_use)
    os.system('echo "net.ipv4.conf.all.proxy_arp = %s" >> /etc/sysctl.conf' % is_use)
    os.system('sysctl -p')


def main(active):
    for item in SDNAT_CHAIN:
        set_nat(item, active)

if __name__ == '__main__':
    set_nat()
    set_nat("SNAT")
    '''
    if len(sys.argv) < 2:
        #getLogger(LOG_NAME).debug('more args (eg: python -m firedam.nat init/reboot)')
        pass
    else:
        main(sys.argv[1])
    #print "nat well done"
    '''
