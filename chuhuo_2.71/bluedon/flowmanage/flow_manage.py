#!/usr/bin/env python
# coding=utf-8

"""
    flow manage

    modify log:
        2016-4-5:
            1、增加流控对ipset(ip组)、ip区间段(192.168.2.1-192.168.2.100)的支持
            2、修复日志重复打印的bug
            3、增加恢复出厂设置选项功能
        2016-4-7:
            1、修复单次执行任务的不可删除bug
        2016-4-18:
            1、修复开机重启后没有删除crontab和at中的定时任务bug
            2、取消开机初始化所有应用的mark, 改为使用某个应用才设置该应用的mark标签
        2016-4-26:
            1、应用的mark(提高性能)
                old: '/usr/sbin/iptables -t mangle -%s APPMARK -m ndpi --%s -j MARK --set-mark %d'
                new: '/usr/sbin/iptables -t mangle -%s APPMARK -m mark --mark 0 -m ndpi --%s -j MARK --set-mark %d'
            2、后台添加虚拟线路接口修改 改为: tcs -A vEth1 -O vEth0 -l 20 -v 20/20 mbps
        2016-5-11:
            1、新增ip掩码识别二进制(1.1.1.0/24)
            2、将定时任务从 /etc/crontab 迁移到 /etc/cron.d/flow_manage, 防止误删/etc/crontab中的定时任务
        2016-5-25:
            1、重构代码(pylint 2.56/befer 9.5/after)
            2、修复恢复出厂设置时没有对应用的计数器减一的动作
        2016-6-12:
            1、确认所执行的系统命令会不会自动退出，不会则加'&' 让其后台运行
        2016-7-11:
            1、系统命令路径统一从 core.setting 中导入
        2016-8-16:
            1、新增用户/用户组
"""

import re
import sys
import os
import time
import json
import commands
from datetime import datetime
from logging import getLogger

from db.config import search_data, mkdir_file
from utils.logger_init import logger_init
# from utils.app_mark_count import set_app_mark
from core.exceptions import ArgumentError
from core.setting import CMD_SED, CMD_AT, CMD_SERVICE, LOG_BASE_PATH

from IPy import IP

# TODO(ruan.lj): remove commited set_app_mark code, if needless

TCS_CLIENT = '/home/ng_platform/bd_dpdk_warper/clients/tcs'
TCS_SERVER = '/home/ng_platform/bd_dpdk_warper/run.sh'
TCS_FILE = '/usr/local/bluedon/tmp/tcs_file.conf'
AT_FILE = '/usr/local/bluedon/tmp/at.txt'

LOG_NAME = 'FLOW_MANAGE'
LOG_PATH = os.path.join(LOG_BASE_PATH, 'flow_manage.log')

COMMANDS = commands.getstatusoutput

logger_init(LOG_NAME, LOG_PATH, 'DEBUG')


mkdir_file('/etc/cron.d/flow_manage', 'file', mod=644)
os.system('/usr/bin/chmod 644 /etc/cron.d/flow_manage')

def change_unit(val, unit):
    """
    带宽单位转换为kbps
    args:
        val: 数值
        unit: 单位
    return:
        value: 转换为kbps后的数值
    """

    if unit.upper() == 'MBPS':
        value = int(float(val)) * 1000
    elif unit.upper() == 'KBPS':
        value = int(float(val))
    return value

def change_time_format(s_time):
    """
    改变时间的格式(2016-01-08 10:20:05 --> 10:20 08.01.16)
    args:
        s_time: 只处理这种格式的时间('2015-12-21 16:11:00')
              主要用于处理单次循环时间
    return:
        data: 返回MM:HH DD.MM.YY格式的时间日期
    """

    frm = '%Y-%m-%d %H:%M:%S'
    cfrm = '%H:%M %d.%m.%Y'
    time_str = time.mktime(time.strptime(s_time, frm))
    d_time = time.localtime(time_str)
    r_time = time.strftime(cfrm, d_time)
    return r_time

def update_crontab(action, data):
    """ 更新crontab文件 """

    if action == 'add' and data:
        lines = '\n'.join(data)
        lines = lines + '\n'
        try:
            with open('/etc/cron.d/flow_manage', 'a') as filepath:
                filepath.write(lines)
        except IOError as err:
            getLogger(LOG_NAME).debug(err)
    elif action == 'del':
        os.system(r'%s -i "/-g %d\>/"d %s' %(CMD_SED, int(data),
                                             '/etc/cron.d/flow_manage'))

def get_atq_id(content):
    """ 获取at的id号 """

    num = ''
    try:
        content = content.split('\n')
        for line in content:
            if 'job' in line and 'at' in line:
                line = line.split('at')[0]
                num = re.search(r'\d+', line).group()
                break
    except Exception as err:
        getLogger(LOG_NAME).debug(err)
    return num


class UpdateAtq(object):
    """ 更新at任务序列号 """
    def __init__(self):
        self.path = '/usr/local/bluedon/tmp/atq.txt'
        mkdir_file(self.path, 'file')
        self.content = self.read()

    def read(self):
        """ 读取 """
        with open(self.path, 'r') as filepath:
            content = filepath.read().strip()
            content = json.loads(content) if content else {}
        return content

    def add(self, tcs_id, atq_id):
        """ 增加 """
        if tcs_id in self.content:
            self.content[tcs_id].append(atq_id)
        else:
            self.content.setdefault(tcs_id, [atq_id])
        self.write()

    def delete(self, tcs_id):
        """ 删除 """
        if tcs_id in self.content:
            atq_id = self.content[tcs_id]
            self.content.pop(tcs_id)
            self.write()
            return atq_id
        else:
            getLogger(LOG_NAME).debug('atq.txt not key %s' %(str(tcs_id)))
            return []

    def write(self):
        """ 写 """
        content = json.dumps(self.content)
        with open(self.path, 'w') as filepath:
            filepath.write(content)

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
        raise ArgumentError
    return results

class VirtualLine(object):
    """ 虚拟线路增删改 """

    def __init__(self, data):
        """ 初始化 """

        self.data = data
        self.log_type = 'VIRTUAL_LINE'

    def add(self):
        """
        增加线路
        args:
            None
        return:
            True: 增加线路成功
            False: 增加线路失败
        """

        # 转换单位
        upvalue = change_unit(self.data['sUpLoad'], self.data['sUpUnit'])
        downvalue = change_unit(self.data['sDownLoad'], self.data['sDownUnit'])

        virtual_str = '%s -A %s -O %s -l %d -v %d/%d' %(TCS_CLIENT,
                                                        self.data['sInnerPort'],
                                                        self.data['sOutPort'],
                                                        int(self.data['id']),
                                                        downvalue, upvalue
                                                       )
        (status, output) = COMMANDS(virtual_str)
        getLogger(LOG_NAME).debug(virtual_str)
        getLogger(LOG_NAME).debug(output)

        if status:
            return False
        else:
            return True

    def delete(self):
        """
        删除虚拟线路(注: 需把crontab中该线路下的通道都删除)
        args:
            None
        return:
            True: 删除成功
            False: 删除失败
        """

        virtual_str = '%s -D %s -l %d' %(TCS_CLIENT, self.data['sInnerPort'],
                                         int(self.data['id']))
        (status, output) = COMMANDS(virtual_str)
        getLogger(LOG_NAME).debug(virtual_str)
        getLogger(LOG_NAME).debug(output)

        # 把crontab中该线路下的通道定时任务都删除
        sql = 'select id, iEffectiveTimeType from m_tbflow_socket \
                where sEffectiveLine=%d;' %(int(self.data['id']))
        results = search_data(sql)
        for result in results:
            if int(result['iEffectiveTimeType']) == 1:
                update_ate = UpdateAtq()
                nums = update_ate.delete(str(result['id']))
                for num in nums:
                    os.system('/usr/bin/atrm %s' %(str(num)))
            else:
                update_crontab('del', int(result['id']))


class Aisle(object):
    """ 通道 """

    def __init__(self, data):
        """
        初始化
        args:
            data: 操作数据行的记录集
        return:
            None
        """
        for key, val in data.iteritems():
            if key.startswith('i'):
                data[key] = int(float(val or 0))

        self.data = data
        self.log_type = 'AISLE'
        mkdir_file(TCS_FILE, 'file')
        mkdir_file(AT_FILE, 'file')

    def write_log(self, status='', output=''):
        """ 写入日志 """
        if str(status):
            getLogger(LOG_NAME).debug(status)
        if output:
            getLogger(LOG_NAME).debug(output)

    def add(self):
        """
        增加宽带控制规则
        args:
            None
        return:
            True: 增加成功
            False: 增加失败
        """

        str_list = []

        # 指定插入的位置(序列)
        subport = '[subport=%d]' %(int(self.data['id']))
        str_list.append(subport)
        priority = 'priority=%d' %(int(self.data['iSort']))
        str_list.append(priority)

        # 指定虚拟线路
        virtual_line = 'virtual line=%d' %(int(self.data['sEffectiveLine']))
        str_list.append(virtual_line)

        # 保证通道
        if int(self.data['iSocketType']) == 1:
            # 单位转换为kbps
            upsafeval = change_unit(self.data['sUpLoadSafeNumber'],
                                    self.data['sUpLoadSafeUnit'])
            upmaxval = change_unit(self.data['sUpLoadMaxNumber'],
                                   self.data['sUpLoadMaxUnit'])
            downsafeval = change_unit(self.data['sDownLoadSafeNumber'],
                                      self.data['sDownLoadSafeUnit'])
            downmaxval = change_unit(self.data['sDownLoadMaxNumber'],
                                     self.data['sDownLoadMaxUnit'])

            ceil = 'ceil=%d/%d' %(downmaxval, upmaxval)
            rate = 'rate=%d/%d' %(downsafeval, upsafeval)
            str_list.append(ceil)
            str_list.append(rate)

        # 限制通道
        elif int(self.data['iSocketType']) == 2:
            limitupmaxval = change_unit(self.data['sLimitUpNumber'],
                                        self.data['sLimitUpUnit'])
            limitdownmaxval = change_unit(self.data['sLimitDownNumber'],
                                          self.data['sLimitDownUnit'])

            ceil = 'ceil=%d/%d' %(limitdownmaxval, limitupmaxval)
            str_list.append(ceil)

        # 启动单ip限制
        if int(self.data['iTurnOnIPMax']) == 1:
            ipupval = change_unit(self.data['sIPUpLoad'],
                                  self.data['sIPUpLoadUnit'])
            ipdownval = change_unit(self.data['sIPDownLoad'],
                                    self.data['sIPDownLoadUnit'])
            single_ceil = 'single ceil=%d/%d' %(ipdownval, ipupval)
            str_list.append(single_ceil)

        # 适用应用
        if int(self.data['iForApplication']) == 1:    # 所有应用
            protocol = 'protocol=0'
        elif int(self.data['iForApplication']) == 2:  # 自定义的应用
            protocol = 'protocol=%s' %(str(self.data['sApplicationId']))
        str_list.append(protocol)

        # 适用对象
        ips = []
        if str(self.data['iForObject']) == '1':     # ip组
            g_sql = 'select HideID from m_tbaddressgroup where id=%d;'\
                    %(int(self.data['sObjectId']))
            result = judge_data(g_sql)[0]
            userset = 'userset=%s' %(result['HideID'])
            ips.append(userset)
        elif str(self.data['iForObject']) in ['2', '4']:   # 2用户/4用户组
            d = {'2': 'id={0}', '4': 'iGroupID={0}'}[str(self.data['iForObject'])]
            v = str(self.data['sObjectId'])
            sql = 'select sIP from m_tbusers where %s;' %(d.format(v))
            results = search_data(sql)
            for result in results:
                if result['sIP']:
                    user = 'user=%s' %(result['sIP'])
                    ips.append(user)
        elif str(self.data['iForObject']) == '3':    # ip
            addr_sql = 'select sAddress, sAddtype, sNetmask from \
                    m_tbaddress_list where id=%s;' %(str(self.data['sObjectId']))
            result = judge_data(addr_sql)[0]
            if str(result['sAddtype']) == '1':    # ip和掩码形式
                if result['sAddress'].endswith('.0'):
                    if '.' not in result['sNetmask']:
                        addr = '%s/%s' %(result['sAddress'], result['sNetmask'])
                    else:
                        addr = IP('%s/%s' %(result['sAddress'], result['sNetmask']),
                                  make_net=True).strNormal(1)
                else:
                    addr = result['sAddress']
                user = 'user=%s' %(addr)
            elif str(result['sAddtype']) == '2':    # ip段
                user = 'userrange=%s-%s' %(result['sAddress'], result['sNetmask'])
            ips.append(user)

        for i in ips:
            str_list.append(i)

        # 把命令行参数写入tcs配置文件
        lines = '\n'.join(str_list)
        #print lines
        with open('%s' %(TCS_FILE), 'w') as filepath:
            filepath.write(lines)

        # 获取端口号, 并新增通道
        v_sql = 'select sInnerPort from m_tbflow_virtualline where id=%d;'\
                %(int(self.data['sEffectiveLine']))
        result = judge_data(v_sql)[0]
        inport = result['sInnerPort']

        # 设置应用的mark
        # if int(self.data['iForApplication']) == 2:  # 自定义的应用
        #     set_app_mark(int(self.data['sApplicationId']), 'add')

        # 添加通道
        tcs_str = '%s -A %s -f %s' %(TCS_CLIENT, inport, TCS_FILE)
        (status, output) = COMMANDS(tcs_str)
        self.write_log(status, output)

        # 如果增加通道失败, 则删除该应用的mark
        # if status != 0:
        #     if int(self.data['iForApplication']) == 2:# 自定义的应用
        #         set_app_mark(int(self.data['sApplicationId']), 'del')
        #     raise ArgumentError

        self.process_time(inport)

    def process_time(self, inport):
        """ 生效时间处理 """
        # 当前的系统时间和周几
        time_format = '%Y-%m-%d %X'
        local_time = datetime.now().strftime(time_format)
        # 0-6(6代表周日)
        week = datetime.today().weekday()

        tcs_up = '%s -U %s UP -g %d' %(TCS_CLIENT,
                                       inport, int(self.data['id']))
        tcs_down = '%s -U %s DOWN -g %d' %(TCS_CLIENT,
                                           inport, int(self.data['id']))

        # 生效时间
        if int(self.data['iEffectiveTimeType']) == 1:    # 单次模式
            t_sql = 'select dStartTime, dEndTime from m_tbtimeplan_single \
                    where id=%d;'%(int(self.data['iEffectiveTime']))
            res = judge_data(t_sql)[0]

            # 如果当前时间早于开始时间 则关闭当前通道的流量管理
            if res['dStartTime'].strftime(time_format) > local_time:
                (status, output) = COMMANDS(tcs_down)
                self.write_log(status, output)

            os.system('%s atd restart' %(CMD_SERVICE))   # at需启动atd服务

            def w_at(s_time):
                """ 更新at """
                with open('%s' %(AT_FILE), 'w') as filepath:
                    filepath.write(tcs_up)

                stat, outp = COMMANDS('%s -f %s %s' %(CMD_AT, AT_FILE, s_time))
                satq_id = get_atq_id(outp)
                u_atq = UpdateAtq()
                if satq_id:
                    u_atq.add(str(self.data['id']), satq_id)

            # 把计时任务写入at
            stime = change_time_format(res['dStartTime'].strftime(time_format))
            etime = change_time_format(res['dEndTime'].strftime(time_format))
            w_at(stime)
            w_at(etime)

        elif int(self.data['iEffectiveTimeType']) == 2:   # 循环模式
            time_sql = 'select * from m_tbtimeplan_loop where id=%d;' \
                    %(int(self.data['iEffectiveTime']))
            res = judge_data(time_sql)[0]

            week_dict = {'0': ['iMondayOn', 'sMonday'],
                         '1': ['iTuesdayOn', 'sTuesday'],
                         '2': ['iWednesdayOn', 'sWednesday'],
                         '3': ['iThursdayOn', 'sThursday'],
                         '4': ['iFridayOn', 'sFriday'],
                         '5': ['iSaturdayOn', 'sSaturday'],
                         '6': ['iSundayOn', 'sSunday']
                        }
            now_time = local_time.split()[1]
            # 判断当前时间是否在预设的时间内, 不在则关闭流量管理
            flag = False
            on_off = int(res[week_dict['%d' %(week)][0]])
            if on_off == 1:
                items = json.loads(res[week_dict['%d' %(week)][1]])
                for item in items:
                    item = item.split('-')
                    if item[0] <= now_time and now_time < item[1]:
                        flag = True
                        break
            if not flag:
                (status, output) = COMMANDS(tcs_down)
                self.write_log(status, output)

            # 把计时任务写入crontab中(crontab中0-6, 0表示周日)
            week_name = {'iMondayOn': ['sMonday', 1],
                         'iTuesdayOn': ['sTuesday', 2],
                         'iWednesdayOn': ['sWednesday', 3],
                         'iThursdayOn': ['sThursday', 4],
                         'iFridayOn': ['sFriday', 5],
                         'iSaturdayOn': ['sSaturday', 6],
                         'iSundayOn': ['sSunday', 0]
                        }
            lines_list = []
            for key in week_name:
                if int(res[key]) == 1:
                    items = json.loads(res[week_name[key][0]])
                    for item in items:
                        item = item.split('-')
                        stime = item[0].split(':')
                        etime = item[1].split(':')
                        scrontab = '%s %s * * %d  root %s # tcs'\
                                %(stime[1], stime[0], week_name[key][1], tcs_up)
                        ecrontab = '%s %s * * %d  root %s # tcs'\
                                %(etime[1], etime[0], week_name[key][1], tcs_down)
                        lines_list.append(scrontab)
                        lines_list.append(ecrontab)

            # 更新crontab
            update_crontab('add', lines_list)

    def delete(self):
        """
        删除通道
        args:
            data: 删除的数据
        return:
            True: 删除成功
            False: 删除失败
        """

#	if int(self.data['iStatus']) != 1:
#	    return

        vir_sql = 'select sInnerPort from m_tbflow_virtualline where id=%d;'\
                %(int(self.data['sEffectiveLine']))
        result = judge_data(vir_sql)[0]

        tcs_str = '%s -D %s -g %d' %(TCS_CLIENT, result['sInnerPort'],
                                     int(self.data['id']))
        (status, output) = COMMANDS(tcs_str)
        self.write_log(status, output)

        # 删除应用的mark
        # if (status == 0 and int(self.data['iStatus']) == 1
        #     and int(self.data['iForApplication']) == 2):
        #     set_app_mark(int(self.data['sApplicationId']), 'del')

        # 删除crontab相关的定时任务
        if int(self.data['iEffectiveTimeType']) == 1:
            update_ate = UpdateAtq()
            nums = update_ate.delete(str(self.data['id']))
            for num in nums:
                os.system('/usr/bin/atrm %s' %(str(num)))
        else:
            update_crontab('del', int(self.data['id']))

        if status:
            return False
        else:
            return True

    def seq(self):
        """
        通道优先级排序
        args:
            None
        return:
            True: 修改优先级成功
            False: 修改优先级失败
        """

        vir_sql = 'select sInnerPort from m_tbflow_virtualline where id=%d;' \
                %(int(self.data['sEffectiveLine']))
        result = judge_data(vir_sql)[0]

        # 调整通道优先级
        tcs_str = '%s -S %s -g %d -o %d' %(TCS_CLIENT, result['sInnerPort'],
                                           int(self.data['id']), int(self.data['iSort']))
        (status, output) = COMMANDS(tcs_str)
        self.write_log(status, output)

        if status:
            return False
        else:
            return True

def main(args):
    """ 主函数 """
    # 删除/etc/crontab中的所有tcs定时任务
    os.system(r'%s -i "/# tcs\>/"d %s' %(CMD_SED, '/etc/cron.d/flow_manage'))
    # 删除at定时任务
    update_atq = UpdateAtq()
    at_nums = update_atq.content
    if at_nums:
        for at_num in at_nums:
            for i in at_num:
                os.system('/usr/bin/atrm %s' %(str(i)))

    line_sql = 'select * from m_tbflow_virtualline;'
    line_datas = search_data(line_sql)

    aisle_sql = 'select * from m_tbflow_socket where iStatus=1 order by iSort;'
    aisle_datas = search_data(aisle_sql)

    if args == 'reboot':
        # 虚拟线路
        for line_data in line_datas:
            vir_line = VirtualLine(line_data)
            vir_line.add()
        # 通道
        for aisle_data in aisle_datas:
            aisle = Aisle(aisle_data)
            aisle.add()
    elif args == 'init':
    # 删除虚拟线路(该线路下的通道也会失效)
        for line_data in line_datas:
            vir_line = VirtualLine(line_data)
            vir_line.delete()
        # for aisle_data in aisle_datas:
        #     if int(aisle_data['iForApplication']) == 2:# 自定义的应用
        #         set_app_mark(int(aisle_data['sApplicationId']), 'del')


if __name__ == '__main__':

    if len(sys.argv) < 2:
        getLogger(LOG_NAME).debug('more args (eg: python url_filter init/reboot)')
    else:
        main(sys.argv[1])
    #print "flow manage well done"
