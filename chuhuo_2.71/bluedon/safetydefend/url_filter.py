#!/usr/bin/env python
# coding=utf-8

"""
    第二代防火墙 --> url过滤
    author:
        tanggu
    date:
        2016-1-18
    version:
        1.0.0

    modify log
        2016-4-6:
            1、增加恢复系统默认设置选项
        2016-4-8:
            1、更新掩码转换为二进制的方法
        2016-4-18:
            1、修复开机重启后url过滤规则没有根据表完全写入相关配置文件bug
        2016-5-24:
            1、重构代码(pylint: 4.67/befor 9.56/after)
        2016-7-11:
            1、系统命令路径统一从 core.setting 中导入
        2017-3-22:
            1、使用模板代替文件写入
"""

import json
import sys
import os
import codecs
from jinja2 import Template
from logging import getLogger
from db.config import search_data, mkdir_file
from utils.logger_init import logger_init
from utils.mask_transition import exchange_mask
from core.setting import LOG_BASE_PATH
from IPy import IP


FILE_PATH = '/usr/local/bdwaf/conf/url_filter.conf'
TEMPLATE_PATH = '/usr/local/bluedon/template/url_filter.conf'
LOG_NAME = 'URL_FILTER'
LOG_PATH = os.path.join(LOG_BASE_PATH, 'url_filter.log')
logger_init(LOG_NAME, LOG_PATH, 'DEBUG')
my_logger = getLogger(LOG_NAME)


class UrlFilterConfigFile(object):
    """
    把url过滤参数写入到url过滤配置文件中
    """

    def __init__(self, data=None):
        """
        初始化
        """

        self.data = data
        mkdir_file(FILE_PATH, 'file')

    def ip_ipgroup(self, result):
        """ 处理ip/ip组 """
        if int(result['sAddtype']) == 1:     # ip形式
            if result['sAddress'].endswith('.0'):
                if '.' not in result['sNetmask']:
                    addr = '%s/%s' % (result['sAddress'], result['sNetmask'])
                else:
                    addr = IP('%s/%s' % (result['sAddress'], result['sNetmask']),
                              make_net=True).strNormal(1)
            else:
                if '.' not in result['sNetmask']:
                    addr = '%s/%s' % (result['sAddress'], result['sNetmask'])
                else:
                    mask = exchange_mask(result['sNetmask'])
                    addr = result['sAddress'] + '/' + str(mask)
        elif int(result['sAddtype']) == 2:  # ip段形式
            addr = '%s-%s' % (result['sAddress'], result['sNetmask'])

        return addr

    def get_ips(self):
        """
        根据ip类型获取ip返回一个ip列表
        """
        ips = []
        if int(self.data['iSourceIPType']) == 1:    # ip
            sql = 'select sAddress, sNetmask, sAddtype from m_tbaddress_list\
                    where id=%d;' % (int(self.data['sSourceIPGroup']))
            result = search_data(sql)
            if not result:
                my_logger.debug('m_tbaddress_list table not id %d' % (
                    int(self.data['sSourceIPGroup'])))
                return None
            ips.append(self.ip_ipgroup(result[0]))
        elif int(self.data['iSourceIPType']) == 2:  # ip组
            sql = 'select sIP from m_tbaddressgroup where id=%d;' % (
                int(self.data['sSourceIPGroup']))
            result = search_data(sql)
            if not result:
                my_logger.debug('m_tbaddressgroup table not id %d' % (
                    int(self.data['sSourceIPGroup'])))
                return None
            result = result[0]
            vip = result['sIP'].split(',')
            vip = ['id=%d' % (int(x)) for x in vip]
            vip = ' or '.join(vip)
            sql = 'select sAddress, sNetmask, sAddtype from m_tbaddress_list\
                    where %s;' % (vip)
            results = search_data(sql)
            for result in results:
                ips.append(self.ip_ipgroup(result))
        return ips

    def get_effective_time(self):
        """
        获取规则有效时间
        """
        tfm = '%Y-%m-%d %X'
        if int(self.data['iEffectiveTimeType']) == 1:   # 单次
            sql = 'select dStartTime, dEndTime from m_tbtimeplan_single \
                    where id=%d;' % (int(self.data['iEffectiveTime']))
            result = search_data(sql)
            if not result:
                my_logger.debug('m_tbtimeplan_single table not id %d' % (
                    int(self.data['iEffectiveTime'])))
                return None
            result = result[0]
            stime = result['dStartTime'].strftime(tfm)
            etime = result['dEndTime'].strftime(tfm)
            valid_time_str = 'ST(%s,%s)' % (stime, etime)
        elif int(self.data['iEffectiveTimeType']) == 2:     # 循环
            sql = 'select * from m_tbtimeplan_loop where id=%d;' % (
                int(self.data['iEffectiveTime']))
            result = search_data(sql)
            if not result:
                my_logger.debug('m_tbtimeplan_loop table not id %d' % (
                    int(self.data['iEffectiveTime'])))
                return None
            result = result[0]
            # 根据表字段构建一个字典
            time_dict = {
                'iMondayOn': ['sMonday', 'Mon'],
                'iTuesdayOn': ['sTuesday', 'Tues'],
                'iWednesdayOn': ['sWednesday', 'Wed'],
                'iThursdayOn': ['sThursday', 'Thurs'],
                'iFridayOn': ['sFriday', 'Fri'],
                'iSaturdayOn': ['sSaturday', 'Sat'],
                'iSundayOn': ['sSunday', 'Sun']
            }
            time_list = []
            for key in time_dict.keys():
                if int(result[key]) == 1:
                    items = json.loads(result[time_dict[key][0]])
                    items = ','.join(items)
                    time_str = '(%s %s)' % (time_dict[key][1], items)
                    time_list.append(time_str)
            time_join = ','.join(time_list)
            valid_time_str = 'CT{%s}' % (time_join)
        return valid_time_str

    def get_url_category(self):
        """
        获取url分类
        """
        sql = 'select sURLGroupName from m_tburlgroup \
                where id in (%s);' % (self.data['sUrlType'])
        result = search_data(sql)
        if not result:
            my_logger.debug('m_tburlgroup table not id %d' % (
                int(self.data['sUrlType'])))
            return None
        return result

    def add(self):
        """
        增加url过滤规则到配置文件
        """
        if str(self.data['iStatus']) == '0':
            return
        ips = self.get_ips()
        url_category = self.get_url_category()
        valid_time_str = self.get_effective_time()
        if not url_category or not valid_time_str or not ips:
            return
        template_args = {
            'id': int(self.data['id']),
            'policy_name': self.data['sName'],
            'iLog': int(self.data['iLog']),
            'iAction': int(self.data['iAction']),
            'sip': ','.join(ips),
            'valid_time_str': valid_time_str,
            'url_category': url_category,
        }
        with open(TEMPLATE_PATH, 'r') as fp:
            conf = Template(fp.read())
        with open(FILE_PATH, 'a') as fp:
            fp.write(conf.render(data=template_args).encode('utf-8'))

    def delete(self):
        """
        删除url过滤规则
        """
        # 求匹配的开始和结束索引号
        re_str = 'ID:%d\n' % (int(self.data['id']))
        filepath = codecs.open(FILE_PATH, 'r', 'utf-8')
        line_list = []
        count = 0
        for line in filepath:
            if line == re_str:
                count = 8
            if count:
                count = count - 1
                continue
            line_list.append(line)
        filepath.close()
        fw = codecs.open(FILE_PATH, 'w', 'utf-8')
        fw.write(''.join(line_list))
        fw.close()


def main(args):
    """ 主函数 """
    os.system('/usr/bin/rm -rf %s' % (FILE_PATH))
    if args == 'reboot':
        u_sql = 'select * from m_tburl_filter where iStatus=1;'
        rdatas = search_data(u_sql)
        for rdata in rdatas:
            conf = UrlFilterConfigFile(rdata)
            conf.add()
    elif args == 'init':
        pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        my_logger.debug('more args (eg: python url_filter init/reboot)')
    else:
        main(sys.argv[1])
