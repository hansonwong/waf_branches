#!/usr/bin/env python
# coding=utf-8

"""
    第二代防火墙 --> 安全策略
    author:
        Tanggu
    date:
        2015-12-16
    version:
        1.0.0

    modify:
        2015-1-20:
            1、根据界面的修改作相应的修改并从新测试脚本
        2016-3-21:
            1、不能删除安全策略bug以及关联表查询为空的处理
        2016-4-20:
            1、取消开机初始化所有应用的mark, 改为使用某个应用才设置该应用的mark标签
        2016-4-21:
            1、如果网口是桥模式: 入口: -m physdev --physdev-in  出口: -m physdev --physdev-out
        2016-4-29:
            1、勾选单向时需设两条iptables:
                iptables -A SECURITYPOLICY -i 入网口 -o 出网口 -s 10.10.10.24/32 -d 1.1.1.101/32 \
                    -p tcp --sport 12 --dport 34 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
                iptables -A SECURITYPOLICY -o 入网口 -i 出网口 -d 10.10.10.24/32 -s 1.1.1.101/32 \
                    -p tcp --dport 12 --sport 34 -m state --state ESTABLISHED,RELATED -j ACCEPT
        2016-5-12:
            1、新增ip掩码识别二进制(1.1.1.0/24)
            2、重构源和目的ip关联ip/ip组表的相关查询操作
        2016-5-24:
            1、重构代码(pylint 0.96/befor 9.5/after)
            2、动作为拒绝时, 单向变为: -m state --state NEW, 且少一条单向时源目的出入对换的iptables(如26行)
        2016-6-12:
            1、确认所执行的系统命令会不会自动退出，不会则加'&' 让其后台运行

"""

import os
import sys
import json
import commands
from logging import getLogger

from utils.logger_init import logger_init
from utils.app_mark_count import set_app_mark
from db.config import search_data

from IPy import IP


CMD_IPTABLES = '/usr/sbin/iptables'
CHAIN = 'SECURITYPOLICY'
LOG_NAME = 'SAFE_TACTICS'
LOG_PATH = '/usr/local/bluedon/log/safe_tactics.log'


logger_init(LOG_NAME, LOG_PATH, 'DEBUG')


def judge_data(msql):
    """ 判断查询的记录集是否为空 """

    key_word = ''
    tablename = ''
    condiction = ''
    words = msql.split()
    for word in words:
        if key_word == 'from':
            tablename = word
        elif key_word == 'where':
            condiction = word
        key_word = word.lower()
    results = search_data(msql)
    if not results:
        getLogger(LOG_NAME).debug('%s table not %s' %(tablename, condiction))
        from core.exceptions import ArgumentError
        raise ArgumentError
    return results

def seq_number(datas):
    """
    求iptables中序列号的增量(根据日记模式和生效时间判断)
    args:
        datas: 小于当前iptabs snum的记录集
    return:
        number: 增量
    """

    count = 0
    ioneway_count = 0
    log_count = 0
    number = 0

    for data in datas:
        if isinstance(data['iEffectiveTimeType'], (int, long, str, unicode)):
            if int(data['iEffectiveTimeType']) == 1:    # 单次时间
                count = 1
            elif int(data['iEffectiveTimeType']) == 2:  # 循环时间
                t_sql = 'select * from m_tbtimeplan_loop_scm where id=%d;'\
                        %(int(data['iEffectiveTime']))
                result = judge_data(t_sql)[0]
                # 根据表字段构建一个字典
                week_dict = {'iMondayOn':'sMonday', 'iTuesdayOn':'sTuesday',
                             'iWednesdayOn':'sWednesday',
                             'iThursdayOn':'sThursday', 'iFridayOn':'sFriday',
                             'iSaturdayOn':'sSaturday', 'iSundayOn':'sSunday'
                            }
                for key in week_dict:
                    if result[key]:
                        count += len(json.loads(result[week_dict[key]]))
        else:
            count = 1

        # 勾选单向
        if str(data['iAction']) == '1':       # 允许
            if data['iOneway'] and str(data['iOneway']) == '1':
                ioneway_count = count

        # 如果开启日记模式
        if int(data['iLog']) == 1:
            log_count = count
        number += count + ioneway_count + log_count

        count = 0
        ioneway_count = 0
        log_count = 0
    return number

def judge_null(data):
    """
    判断参数是否为空
    args:
    data: 需判断是否为空的数据
    return:
    flag
    """

    flag = False
    if isinstance(data, (int, long)):
        flag = True
    elif isinstance(data, (str, unicode)):
        if data.strip():
            flag = True
    return flag

class SafeTactics(object):
    """
    安全策略设置
    """

    def __init__(self, data):
        """
        初始化
        """
        self.data = data

    def cmd_str(self):
        """
        拼接命令行的字符串
        args:
            None
        return:
            log_cmd_list: 日记命令行列表
            s_cmd_list: 策略命令行列表
        """

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
            if vtype == '1':	# ip
                ip_sql = 'select sAddress, sNetmask, sAddtype from \
                        m_tbaddress_list_scm where id=%d;' %(vid)
                data = judge_data(ip_sql)[0]
                if str(data['sAddtype']).strip() == '1':    # ip和掩码形式
                    if data['sAddress'].endswith('.0'):
                        if '.' not in data['sNetmask']:
                            addr = '%s/%s' %(data['sAddress'], data['sNetmask'])
                        else:
                            addr = '%s/%s' %(data['sAddress'], data['sNetmask'])
                            addr = IP(addr, make_net=True).strNormal(1)
                    else:
                        addr = data['sAddress']
                    istr = type_dict[sdtype]['onlyip'] %(addr)
                elif str(data['sAddtype']).strip() == '2':	# ip段
                    istr = type_dict[sdtype]['iprange'] \
                            %(data['sAddress'], data['sNetmask'])
            elif vtype == '2':     # ip组
                # 需要从id组表读取相应的组名
                g_sql = 'select HideID from m_tbaddressgroup_scm where id=%d;' %(vid)
                print 'vid:',vid
                data = judge_data(g_sql)[0]
                istr = type_dict[sdtype]['ipgroup'] %(data['HideID'])
            return istr

        # 源ip
        sip_str = u' '
        if judge_null(self.data['sSourceValue']):
            sip_str = ip_ipgroup(str(self.data['iSourceType']),
                                 int(self.data['sSourceValue']), 's')

        # 目的ip
        dip_str = u' '
        if judge_null(self.data['sTargetValue']):
            dip_str = ip_ipgroup(str(self.data['iTargetIPType']),
                                 int(self.data['sTargetValue']), 'd')

        # 单向
        ioneway_str = u' '
        if self.data['iOneway'] and str(self.data['iOneway']) == '1':
            ioneway_str = ' -m state --state NEW,ESTABLISHED,RELATED '
            if str(self.data['iAction']) == '0':       # 拒接
                ioneway_str = ' -m state --state NEW '

        # 协议
        prot_str = u' '
        if judge_null(self.data['sProtocol']):
            prot_str = ' -p %s ' %(str(self.data['sProtocol']).lower())

        # 源端口
        sport_str = u' '
        if (judge_null(self.data['sSourcePort']) and
            self.data['sProtocol'].lower() != 'icmp'):
            sport_str = ' --sport %s ' %(str(self.data['sSourcePort']))

        # 目的端口
        dport_str = u' '
        if (judge_null(self.data['sTargetPort']) and
            self.data['sProtocol'].lower() != 'icmp'):
            dport_str = ' --dport %s ' %(str(self.data['sTargetPort']))

        # 应用
        app_str = u' '
        if judge_null(self.data['iAppID']):
            app_str = ' -m mark --mark %s/0XFFF ' %(str(self.data['iAppID']))

        def net_port_mode(port_name):
            ''' 根据网口名称, 查找该网口的的工作模式并返回 '''
            p_sql = 'select sWorkMode from m_tbnetport where sPortName="%s";'\
                    %(port_name)
            p_data = judge_data(p_sql)[0]
            return p_data['sWorkMode']

        # 入口
        inport_str = u' '
        if judge_null(self.data['sInputPort']):
            port_mode = net_port_mode(self.data['sInputPort'])
            if port_mode == 'bridge':
                inport_str = ' -m physdev --physdev-in %s '\
                        %(self.data['sInputPort'])
            else:
                inport_str = ' -i %s ' %(str(self.data['sInputPort']))

        # 出口
        outport_str = u' '
        if judge_null(self.data['sOutPort']):
            port_mode = net_port_mode(self.data['sOutPort'])
            if port_mode == 'bridge':
                outport_str = ' -m physdev --physdev-out %s '\
                        %(self.data['sOutPort'])
            else:
                outport_str = ' -o %s ' %(str(self.data['sOutPort']))

        # 生效时间
        time_str = u' '
        time_list = []
        if judge_null(self.data['iEffectiveTime']):
            if str(self.data['iEffectiveTimeType']) == '1':        # 单次时间
                t_sql = 'select dStartTime, dEndTime from m_tbtimeplan_single_scm \
                        where id=%d;' %(int(self.data['iEffectiveTime']))
                result = judge_data(t_sql)[0]

                fmt = '%Y-%m-%d %X'
                stime = result['dStartTime'].strftime(fmt).replace(' ', 'T')
                etime = result['dEndTime'].strftime(fmt).replace(' ', 'T')
                time_str = ' -m time --kerneltz --datestart %s --datestop %s '\
                        %(stime, etime)
                time_list.append(time_str)
            elif str(self.data['iEffectiveTimeType']) == '2':      # 循环时间
                tl_sql = 'select * from m_tbtimeplan_loop_scm where id=%d;'\
                        %(int(self.data['iEffectiveTime']))
                result = judge_data(tl_sql)[0]

                # 根据表字段构建一个字段
                week_dict = {'iMondayOn':['sMonday', 1],
                             'iTuesdayOn':['sTuesday', 2],
                             'iWednesdayOn':['sWednesday', 3],
                             'iThursdayOn':['sThursday', 4],
                             'iFridayOn':['sFriday', 5],
                             'iSaturdayOn':['sSaturday', 6],
                             'iSundayOn':['sSunday', 7]
                            }
                time_format = ' -m time --kerneltz --timestart %s \
                        --timestop %s --weekdays %d '
                for key in week_dict:
                    if result[key]:
                        print result
                        # items = json.loads(result[week_dict[key][0]])
                        items = result[week_dict[key][0]]
                        for item in items:
                            stime = item.split('-')[0]
                            etime = item.split('-')[1]
                            time_str = time_format %(stime, etime, week_dict[key][1])
                            time_list.append(time_str)

        # 动作
        j_str = u' '
        log_str = u' '
        if str(self.data['iAction']) == '1':       # 允许
            j_str = ' -j ACCEPT '
            log_str = ' -j LOG --log-prefix "ipt_log=ACCEPT "'
        elif str(self.data['iAction']) == '0':     # 拒接
            j_str = ' -j DROP '
            log_str = ' -j LOG --log-prefix "ipt_log=DROP "'

        b_cmd_str = sip_str + dip_str + prot_str + sport_str + dport_str + \
                    app_str + inport_str + outport_str + ioneway_str

        if time_list:
            b_cmd_list = [b_cmd_str + x for x in time_list]
        else:
            b_cmd_list = [b_cmd_str]

        s_cmd_list = []
        r_cmd_list = []
        log_cmd_list = []

        s_cmd_list = [x + j_str for x in b_cmd_list]

        # 如果勾选了单向
        if str(self.data['iAction']) == '1':     # 允许
            if self.data['iOneway'] and str(self.data['iOneway']) == '1':
                r_cmd_str = sip_str + dip_str + prot_str + sport_str + \
                        dport_str + inport_str + outport_str
                r_cmd_str = r_cmd_str.replace('-s ', '-# ').replace('-d ', '-s ')\
                        .replace('-# ', '-d ').replace('-i ', '-$ ')\
                        .replace('-o ', '-i ').replace('-$ ', '-o ')\
                        .replace('--src', '--@').replace('--dst', '--src')\
                        .replace('--@', '--dst').replace('--sport', '--&')\
                        .replace('--dport', '--sport').replace('--&', '--dport')
                r_cmd_str = r_cmd_str + app_str +\
                        ' -m state --state ESTABLISHED,RELATED '

                if time_list:
                    bb_cmd_list = [r_cmd_str + x for x in time_list]
                else:
                    bb_cmd_list = [r_cmd_str]

                r_cmd_list = [x + j_str for x in bb_cmd_list]

        log_cmd_list = [x + log_str for x in b_cmd_list]

        return (s_cmd_list, r_cmd_list, log_cmd_list)

    def get_cmd_list(self):
        """ 对待设置的iptables规则进行排序 """

        s_list, r_list, l_list = self.cmd_str()
        cmd_list = []
        num = len(s_list)
        if int(self.data['iLog']) == 1: # 日记模式
            if int(self.data['iOneway']) == 1:
                for i in xrange(num):
                    cmd_list.append(l_list[i])
                    cmd_list.append(s_list[i])
                    if r_list:
                        cmd_list.append(r_list[i])
            else:
                for i in xrange(num):
                    cmd_list.append(l_list[i])
                    cmd_list.append(s_list[i])
        else:
            if int(self.data['iOneway']) == 1:
                for i in xrange(num):
                    cmd_list.append(s_list[i])
                    if  r_list:
                        cmd_list.append(r_list[i])
            else:
                cmd_list = s_list
        return cmd_list

    def add(self):
        """
        增加安全策略
        args:
            None
        return:
            True: 增加成功
            False: 增加失败
        """

        if str(self.data['iStatus']) == '0':
            return False

        # 求iptables中真实的序列号
        if int(self.data['iSort']) > 1:
            service_sql = 'select * from m_tbSearitystrate_scm where iSort<%d;'\
                    %(int(self.data['iSort']))
            datas = search_data(service_sql)
            count = seq_number(datas)
        else:
            count = 0
        number = 1 + count

        if judge_null(self.data['iAppID']):
            set_app_mark(int(self.data['iAppID']), 'add')

        cmd_list = self.get_cmd_list()
        for item in cmd_list:
            iptables_cmd = '%s -I %s %d %s' %(CMD_IPTABLES, CHAIN, number, item)
            (status_log, output_log) = commands.getstatusoutput(iptables_cmd)
            getLogger(LOG_NAME).debug('%s  %s' %(iptables_cmd, output_log))
            number += 1

            if cmd_list.index(item) == 0 and status_log:
                if judge_null(self.data['iAppID']):
                    set_app_mark(int(self.data['iAppID']), 'del')

        os.system('/usr/sbin/service iptables save')

    def delete(self):
        """
        删除安全策略
        args:
            None
        return:
            True: 删除成功
            False: 删除失败
        """

        if judge_null(self.data['iAppID']) and int(self.data['iStatus']) == 1:
            set_app_mark(int(self.data['iAppID']), 'del')

        cmd_list = self.get_cmd_list()
        for item in cmd_list:
            iptables_cmd = '%s -D %s %s' %(CMD_IPTABLES, CHAIN, item)
            (status_log, output_log) = commands.getstatusoutput(iptables_cmd)
            getLogger(LOG_NAME).debug('%s  %s' %(iptables_cmd, output_log))

        os.system('/usr/sbin/service iptables save')

def main():
    """ 主函数 """
    s_sql = 'select * from db_firewall.m_tbSearitystrate_scm where iStatus=1 \
            ORDER BY iSort;'
    datas = search_data(s_sql)
    print 'datas:',datas
    for data in datas:
        safe = SafeTactics(data)
        safe.add()
        #safe.delete()

if __name__ == '__main__':
    main()
    #print 'security policy well done'
