#!/usr/bin/env python
# coding=utf-8

"""
第二代防火墙 --> 安全策略
1、如果网口是桥模式: 入口: -m physdev --physdev-in  出口: -m physdev --physdev-out
1、勾选单向时需设两条iptables:
    iptables -A SECURITYPOLICY -i 入网口 -o 出网口 -s 10.10.10.24/32 -d 1.1.1.101/32 \
        -p tcp --sport 12 --dport 34 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
    iptables -A SECURITYPOLICY -o 入网口 -i 出网口 -d 10.10.10.24/32 -s 1.1.1.101/32 \
        -p tcp --dport 12 --sport 34 -m state --state ESTABLISHED,RELATED -j ACCEPT
2、动作为拒绝时, 单向变为: -m state --state NEW, 且不需要配置反向的iptables
1、当协议为icmp且是ipv6时, 将协议icmp转为icmpv6
1、新增基于应用(FTP_CONTROL, FTP_DATA)的规则:
    iptables -A SECURITYPOLICY -m state --state ESTABLISHED,RELATED --j ACCEPT
1、当协议为TCP且目的端口为21时, 同样新增:
iptables -A SECURITYPOLICY -m state --state ESTABLISHED,RELATED --j ACCEPT
"""

import os
import sys
import json
import commands
from logging import getLogger

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from utils.logger_init import logger_init
from utils.app_mark_count import set_app_mark
from db.config import search_data
from core.setting import CMD_IPTABLES, CMD_IP6TABLES, LOG_BASE_PATH
from db.mysql_db import select_one
from objectdefine.ip_range import deal_ip

CHAIN = 'SECURITYPOLICY'
LOG_NAME = 'SAFE_TACTICS'
LOG_PATH = os.path.join(LOG_BASE_PATH, 'safe_tactics.log')
logger_init(LOG_NAME, LOG_PATH, 'DEBUG')
IPTABLES = None
IP_MASK = '{}/{}'
EXCEPT_PRO = ['icmp', '89', 'gre']


def appid_classification(appid):
    """
    根据appid运算出应用类别:1类，2类，3类
    """
    appid = int(appid)
    two_num, three_class = appid / 256, appid % 256
    first_class, two_class = two_num/256, two_num % 256

    if two_class != 0:
        if three_class != 0:
            mark_str = '%s/0XFFFFF' % appid
        else:
            mark_str = '%s/0XFFF00' % appid
    else:
        mark_str = '%s/0XF0000' % appid
    return mark_str


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
        getLogger(LOG_NAME).debug('%s table not %s' % (tablename, condiction))
        from core.exceptions import ArgumentError
        raise ArgumentError
    return results


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


def _service(id_):
    """
    args:
        stype: 类型为服务组或服务
        sid: 相关服务/服务组表的id
    returns:
        iptables规则关于协议,端口部分的字段
    """
    sql = 'select * from m_tbservices_list where id={};'
    if id_:
        data = select_one(sql.format(int(id_)))
    else:
        data = {'sProtocol': '', 'sSourcePort': '', 'sTargetPort': ''}
    return data


def net_port_mode(port_name):
    """
    根据网口名称, 查找该网口的的工作模式并返回
    """
    sql = 'select sWorkMode from m_tbnetport where sPortName="{}";'. \
        format(port_name)
    data = judge_data(sql)[0]
    return data['sWorkMode']


def ip_ipgroup(vtype, vid, sdtype, iptype='ipv4'):
    """
    args:
        vtype: ip(1)或ip组(2)
        vid: 相关连ip/ip组表的id
        sdtype: 源地址(s), 目的地址(d)
        iptype: ip类型(ipv4 or ipv6)
    return:
        istr: 拼接后的字符串
    """

    type_dict = {
        's': {
            'onlyip': ' -s {} ',
            'iprange': ' -m iprange --src-range {}-{} ',
            'ipgroup': ' -m set --match-set {} src '
        },
        'd': {
            'onlyip': ' -d {} ',
            'iprange': ' -m iprange --dst-range {}-{} ',
            'ipgroup': ' -m set --match-set {} dst '
        }
    }

    istr = u' '
    if vtype == '1':  # ip
        ip_sql = 'select sAddress, sNetmask, sAddtype from \
                m_tbaddress_list where id={};'.format(vid)
        data = judge_data(ip_sql)[0]
        # ip和掩码形式
        if str(data['sAddtype']).strip() == '1':
            if iptype == 'ipv6':
                if (data['sAddress'].endswith('::') or
                        data['sAddress'].endswith(':0')):
                    if data.get('sNetmask', ''):
                        addr = IP_MASK.format(data['sAddress'], data['sNetmask'])
                    else:
                        addr = data['sAddress']
                else:
                    addr = data['sAddress']
            else:
                addr, _ = deal_ip(data['sAddress'], data['sNetmask'])
            istr = type_dict[sdtype]['onlyip'].format(addr)
        # ip段
        elif str(data['sAddtype']).strip() == '2':
            istr = type_dict[sdtype]['iprange'].format(
                        data['sAddress'], data['sNetmask'])
    elif vtype == '2':  # ip组
        # 需要从id组表读取相应的组名
        g_sql = 'select HideID from m_tbaddressgroup where id={};'.format(vid)
        data = judge_data(g_sql)[0]
        istr = type_dict[sdtype]['ipgroup'].format(data['HideID'])
    return istr


class SafeTactics(object):
    """
    安全策略设置
    """

    def __init__(self, data, change=False):
        """
        初始化
        """
        self.data = data
        self.change = change

    def cmd_str(self):
        """
        拼接命令行的字符串
        args:
            None
        return:
            log_cmd_list: 日记命令行列表
            s_cmd_list: 策略命令行列表
        """

        # 源ip
        sip_str = u' '
        if judge_null(self.data['sSourceValue']):
            sip_str = ip_ipgroup(
                str(self.data['iSourceType']), int(self.data['sSourceValue']),
                's', self.data['sIPV']
            )
        # 目的ip
        dip_str = u' '
        if judge_null(self.data['sTargetValue']):
            dip_str = ip_ipgroup(
                str(self.data['iTargetIPType']), int(self.data['sTargetValue']),
                'd', self.data['sIPV']
            )

        # 单向
        ioneway_str = u' '
        if self.data['iOneway'] and str(self.data['iOneway']) == '1':
            ioneway_str = ' -m state --state NEW,ESTABLISHED,RELATED '

        # 协议
        if self.data['sProtocol'] is None:
            pro_ = u' '
        else:
            pro_ = self.data['sProtocol'].lower()
        prot_str = u' '
        if judge_null(pro_):
            prot_str = ' -p {} '.format(str(pro_))
            if pro_ == 'icmp' and self.data['sIPV'] == 'ipv6':
                prot_str = prot_str.replace(' icmp ', ' icmpv6 ')

        # 源端口
        sport_str = u' '
        if (judge_null(self.data['sSourcePort']) and (pro_ not in EXCEPT_PRO)):
            sport_str = ' -m multiport --sport {} '.format(str(self.data['sSourcePort']).replace('-', ':'))

        # 目的端口
        dport_str = u' '
        if (judge_null(self.data['sTargetPort']) and (pro_ not in EXCEPT_PRO)):
            dport_str = ' -m multiport --dport {} '.format(str(self.data['sTargetPort']).replace('-', ':'))

        # 应用
        app_str = u' '
        if judge_null(self.data['iAppID']):
            app_str = ' -m mark --mark {}'.format(appid_classification(self.data['iAppID']))

        # 入口
        inport_str = u' '
        if judge_null(self.data['sInputPort']):
            port_mode = net_port_mode(self.data['sInputPort'])
            if port_mode == 'bridge':
                inport_str = ' -m physdev --physdev-in {} '.format(
                        self.data['sInputPort'])
            else:
                inport_str = ' -i {} '.format(str(self.data['sInputPort']))

        # 出口
        outport_str = u' '
        if judge_null(self.data['sOutPort']):
            port_mode = net_port_mode(self.data['sOutPort'])
            if port_mode == 'bridge':
                outport_str = ' -m physdev --physdev-out {} '.format(
                    self.data['sOutPort'])
            else:
                outport_str = ' -o {} '.format(str(self.data['sOutPort']))

        # 生效时间
        time_list = []
        if judge_null(self.data['iEffectiveTime']):
            if str(self.data['iEffectiveTimeType']) == '1':        # 单次时间
                t_sql = 'select dStartTime, dEndTime from m_tbtimeplan_single \
                        where id=%d;' %(int(self.data['iEffectiveTime']))
                result = judge_data(t_sql)[0]

                fmt = '%Y-%m-%d %X'
                stime = result['dStartTime'].strftime(fmt).replace(' ', 'T')
                etime = result['dEndTime'].strftime(fmt).replace(' ', 'T')
                time_str = ' -m time --kerneltz --datestart %s --datestop %s '\
                        %(stime, etime)
                time_list.append(time_str)
            elif str(self.data['iEffectiveTimeType']) == '2':      # 循环时间
                tl_sql = 'select * from m_tbtimeplan_loop where id=%d;'\
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
                        items = json.loads(result[week_dict[key][0]])
                        for item in items:
                            stime = item.split('-')[0]
                            etime = item.split('-')[1]
                            time_str = time_format %(stime, etime, week_dict[key][1])
                            time_list.append(time_str)

        # 动作
        j_str = u' '
        log_str = u' '
        # 日志中ACCEPT或DROP的后面要保留一个空格，为了日志解释用
        if str(self.data['iAction']) == '1':       # 允许
            j_str = ' -j ACCEPT '
            log_str = ' -j LOG --log-prefix "ipt_log=ACCEPT "'
        elif str(self.data['iAction']) == '0':     # 拒接
            j_str = ' -j DROP '
            log_str = ' -j LOG --log-prefix "ipt_log=DROP "'

        b_cmd_str = sip_str + dip_str + prot_str + sport_str + dport_str + \
                    inport_str + outport_str

        def result_str(string):
            """ 拼接时间 """
            string = string + app_str + ioneway_str
            if time_list:
                string_list = [string + x for x in time_list]
            else:
                string_list = [string]
            return string_list

        def replace_str(string):
            """ 替换字符串 """
            string = string.replace('-s ', '-# ').replace('-d ', '-s ')\
                    .replace('-# ', '-d ').replace('-i ', '-$ ')\
                    .replace('-o ', '-i ').replace('-$ ', '-o ')\
                    .replace('--src', '--@').replace('--dst', '--src')\
                    .replace('--@', '--dst').replace('--sport', '--&')\
                    .replace('--dport', '--sport').replace('--&', '--dport')\
                    .replace(' src ', ' # ').replace(' dst ', ' src ')\
                    .replace(' # ', ' dst ')
            return string

        s_cmd_list = []
        r_cmd_list = []
        log_cmd_list = []

        b_cmd_list = result_str(b_cmd_str)
        s_cmd_list = [x + j_str for x in b_cmd_list]

        # 如果勾选的应用是FTP_CONTROL和FTP_DATA 或者tcp dport:21则新增一条规则
        app_cmd_list = []
        if str(self.data['iAction']) == '1' and (str(self.data.get('sProtocol', '')).lower() == 'tcp'
            and str(self.data.get('sTargetPort', '')) == '21'):
            app_cmd_str = ' -m state --state ESTABLISHED,RELATED '
            if time_list:
                app_cmd_list = [app_cmd_str + item + j_str for item in time_list]
            else:
                app_cmd_list = [app_cmd_str + j_str]

        if self.change:
            if str(self.data['iAction']) == '0':
                change_str = b_cmd_str
            else:
                change_str = replace_str(b_cmd_str)
            change_str_list = result_str(change_str)
            log_cmd_list = [x + log_str for x in change_str_list]
        else:
            log_cmd_list = [x + log_str for x in b_cmd_list]

        # 如果勾选了单向
        if str(self.data['iAction']) == '1':     # 允许
            if self.data['iOneway'] and str(self.data['iOneway']) == '1':
                r_cmd_str = sip_str + dip_str + prot_str + sport_str + \
                        dport_str + inport_str + outport_str
                r_cmd_str = replace_str(r_cmd_str)
                r_cmd_str_list = [r_cmd_str + app_str +\
                        ' -m state --state ESTABLISHED,RELATED ']

                if (judge_null(self.data['sProtocol']) and
                    self.data['sProtocol'].strip().lower() == 'tcp'):
                    item = r_cmd_str + app_str + ' --tcp-flags PSH,ACK PSH,ACK '
                    r_cmd_str_list.insert(0, item)

                r_cmd_list = []
                for i in time_list:
                    item = []
                    for j in r_cmd_str_list:
                        item.append(j + i + j_str)
                    if item:
                        r_cmd_list.append(item)
                else:
                    r_cmd_str_list = [item + j_str for item in r_cmd_str_list]
                    r_cmd_list.append(r_cmd_str_list)

        return s_cmd_list, r_cmd_list, log_cmd_list, app_cmd_list

    def get_cmd_list(self):
        """ 对待设置的iptables规则进行排序 """

        s_list, r_list, l_list, a_list = self.cmd_str()
        cmd_list = []
        num = len(s_list)
        # 日记模式
        if int(self.data['iLog']) == 1:
            if int(self.data['iOneway']) == 1:
                for i in xrange(num):
                    cmd_list.append(l_list[i])
                    cmd_list.append(s_list[i])
                    if r_list:
                        cmd_list.append(r_list[i])
                    if a_list:
                        cmd_list.append(a_list[i])
            else:
                for i in xrange(num):
                    cmd_list.append(l_list[i])
                    cmd_list.append(s_list[i])
                    if a_list:
                        cmd_list.append(a_list[i])
        else:
            if int(self.data['iOneway']) == 1:
                for i in xrange(num):
                    cmd_list.append(s_list[i])
                    if r_list:
                        cmd_list.append(r_list[i])
                    if a_list:
                        cmd_list.append(a_list[i])
            else:
                for i in xrange(num):
                    cmd_list.append(s_list[i])
                    if a_list:
                        cmd_list.append(a_list[i])
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

        def execu_cmd(cmd):
            iptables_cmd = '{} -A {} {}'.format(IPTABLES, CHAIN, cmd)
            (status, output) = commands.getstatusoutput(iptables_cmd)
            getLogger(LOG_NAME).debug('{} {}'.format(iptables_cmd, output))

        global IPTABLES
        IPTABLES = CMD_IPTABLES if self.data['sIPV'] == 'ipv4' else CMD_IP6TABLES

        cmd_list = self.get_cmd_list()
        for item in cmd_list:
            if isinstance(item, list):
                for i in item:
                    execu_cmd(i)
            else:
                execu_cmd(item)


def del_mark_scount(data, action):
    if judge_null(data['iAppID']):
        set_app_mark(int(data['iAppID']), action)


def oneway(data, change):
    if data['iOneway'] and str(data['iOneway']) == '1':
        if int(data['iAction']) == 0:
            data['iOneway'] = '0'
            change = True
            safe = SafeTactics(data, change)
            safe.add()
        else:
            safe = SafeTactics(data, change)
            safe.add()
    else:
        safe = SafeTactics(data, change)
        safe.add()


def main(datas):
    for data in datas:
        del_mark_scount(data,'add')
        change = False
        if data['sService'] == u'':
            data['sProtocol'] = data['sSourcePort'] = data['sTargetPort'] = u''
            print 'no service'
            oneway(data, change)
        else:
            ids = []
            id_ = data['sService']

            if data['iServiceType'] == 1:
                ids.append(id_)
            else:
                res = select_one(
                    'select sServices from m_tbservice_group where id={}'.format(id_))
                print 'res', res
                ids.extend(res['sServices'].split(','))

            for id_ in ids:
                ip_sdport = _service(id_)
                data['sSourcePort'] = ip_sdport['sSourcePort'] if ip_sdport['sSourcePort'] else u''
                data['sTargetPort'] = ip_sdport['sTargetPort'] if ip_sdport['sTargetPort'] else u''
                pro_list = ip_sdport['sProtocol'].split(',')
                if len(pro_list) == 0:
                    print 'no pro'
                    data['sProtocol'] = u''
                    oneway(data, change)
                else:
                    for item in pro_list:
                        data['sProtocol'] = item.strip().lower()
                        print 'pro', item
                        if data['sProtocol'] in EXCEPT_PRO:
                            data['sSourcePort'] = data['sTargetPort'] = u''
                        oneway(data, change)


def safetactics_main():
    """ 主函数 """

    s_sql = 'select * from db_firewall.m_tbSearitystrate where iStatus=1 ORDER BY iSort;'
    results = search_data(s_sql)
    del_cmd_v4 = '/usr/sbin/iptables -F SECURITYPOLICY'
    del_cmd_v6 = '/usr/sbin/ip6tables -F SECURITYPOLICY'
    os.system(del_cmd_v4)
    os.system(del_cmd_v6)
    main(results)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        pass
    else:
        if sys.argv[1] == 'init':
            os.system('{0} -F {1}'.format(CMD_IPTABLES, CHAIN))
            os.system('{0} -F {1}'.format(CMD_IP6TABLES, CHAIN))
        elif sys.argv[1] == 'reboot':
            safetactics_main()
