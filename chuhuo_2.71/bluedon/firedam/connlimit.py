#! /usr/bin/env python 
# -*- coding:utf-8 -*-

from logging import getLogger
import os
import commands
import shelve
from functools import partial
from collections import OrderedDict
from db.mysqlconnect import mysql_connect, mysql_connect_dict
from db.mysql_db import select_one, select
from objectdefine.ip_range import deal_ip

TABLE_SQL = 'select * from {} where state=1 order by snum'
LOG_SQL = 'select count(*) from {} where iLog=1 and state=1 and snum<{}'

SRC = '/usr/sbin/iptables -I CONNLIMIT_SRC'
DST = '/usr/sbin/iptables -I CONNLIMIT_DST'
LIMIT = '-m connlimit --connlimit-above'
IPSET = '-m set --match-set'
IP_LOG_LMT = '{} {} -p tcp {} {} {} -j LOG --log-prefix "ipt_log=DROP"'
IP_LMT = '{} {} -p tcp {} {} {} -j DROP'
G_LOG_LMT = '{} {} -p tcp {} {} src {} {} -j LOG --log-prefix "ipt_log=DROP"'
G_LMT = '{} {} -p tcp {} {} src {} {} -j DROP'

SRC_DST = {
    'source': SRC,
    'destination': DST
}


def getone(sql):
    """获取一行数据"""
    cur = mysql_connect()
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    return result


def get_ip_mask_type(num):
    """
    从表m_tbaddress_list中获取ip和对应的mask, iptype
    """
    sql = "select sAddress, sNetmask, sAddtype " \
          "from m_tbaddress_list where id={}".format(num)
    ip_mask_type = getone(sql)
    return ip_mask_type


def ip_to_iptableip(num, types):
    """
    把ip或ip段转化为iptables的一部分
    """
    s_d = {
        'source': 's',
        'destination': 'd'
    }
    fmts = {
        '1': '-{} {}',
        '2': '-m iprange --{}rc-range {}-{}'
    }

    ips = get_ip_mask_type(num)
    if ips:
        tbs = fmts[ips[2]]
        ip_mask, _ = deal_ip(ips[0], ips[1])
        if ips[2] == '1':
            iptables = tbs.format(s_d[types], ip_mask)
            print 'ip/mask'
            print iptables
        else:
            iptables = tbs.format(s_d[types], ips[0], ips[1])
        return iptables


def iptable_order(shelve_filename, src_or_dst):
    table = 'm_tbsipcon' if src_or_dst == 'source' else 'm_tbdipcon'
    info = select(TABLE_SQL.format(table))
    conname = OrderedDict()
    db = shelve.open(shelve_filename)
    for tmp in info:
        conname['nolog_num'] = ''
        conname['log_num'] = ''
        logcount = select_one(LOG_SQL.format(table, int(tmp['snum'])))
        order = int(tmp['snum']) + logcount['count(*)']
        if tmp['iLog'] == 1:
            conname['log_num'] = order
            order += 1
        conname['nolog_num'] = order
        db[str(tmp['conname'])] = conname
    db.close()


def delete(shelve_name, src_or_dst, conname):
    """
    shelve里保存了删除连接的iptables命令的字典，根据连接名称来删除
    """
    print'before del:'
    print 'shelve_name', shelve_name
    db = shelve.open(shelve_name)
    for _, value in db[conname].items():
        if value:
            cmd = '{} {}'.format(SRC_DST[src_or_dst], str(value)).replace('-I', '-D')
            print 'CMD', cmd
            os.system(cmd)
        del db[conname]
        db.close()
        print 'after*******'
    iptable_order(shelve_name, src_or_dst)


def add_or_del(status):
    if status == '0':
        process = 'del'
    else:
        process = 'add'
    return process


def run_cmd(log, str_):
    """
    args:
        log: iptables_log
        str_: iptables_str
    """
    if log:
        (status, output) = commands.getstatusoutput(log)
        getLogger('main').info('{} {}'.format(log, output))
    (status, output) = commands.getstatusoutput(str_)
    getLogger('main').info('{} {}'.format(log, output))


def ip_(src_or_dst, order, iptable_ip, limittype, log, limit_num):
    """
    根据源或目的，来得到相应的iptables规则
    """
    iptables_log = ''
    if limittype == 1:
        if log == 1:
            iptables_log = IP_LOG_LMT.format(
                SRC_DST[src_or_dst], order, iptable_ip, LIMIT, limit_num
            )
            order += 1
        iptables_str = IP_LMT.format(
            SRC_DST[src_or_dst], order, iptable_ip, LIMIT, limit_num
        )
    else:
        if log == 1:
            iptables_log = IP_LOG_LMT.replace('DROP', 'ACCEPT').format(
                SRC_DST[src_or_dst], order, iptable_ip, '', ''
            )
            order += 1
        iptables_str = IP_LMT.replace('DROP', 'ACCEPT').format(
            SRC_DST[src_or_dst], order, iptable_ip, '', ''
        )
    return iptables_log, iptables_str, order


def ip_group(src_or_dst, order, ipgroup, limittype, log, limit_num):
    iptables_log = ''
    if limittype == 1:
        if log == 1:
            iptables_log = G_LOG_LMT.format(
                SRC_DST[src_or_dst], order, IPSET, ipgroup, LIMIT, limit_num)
            order += 1
        iptables_str = G_LMT.format(
            SRC_DST[src_or_dst], order, IPSET, ipgroup, LIMIT, limit_num)
    else:
        if log == 1:
            iptables_log = G_LOG_LMT.replace('DROP', 'ACCEPT').format(
                SRC_DST[src_or_dst], order, IPSET, ipgroup, '', '')
            order += 1
        iptables_str = G_LMT.replace('DROP', 'ACCEPT').format(
            SRC_DST[src_or_dst], order, IPSET, ipgroup, '', '')
    return iptables_log, iptables_str, order


def connect_limit(process, info, src_or_dst, shelve_name):
    """源IP、目的IP连接数控制"""

    info = eval(info)
    conname = str(info['conname'])
    if src_or_dst == 'source':
        ip_num = info['sip']
        ip_type = info['sipType']
        sdtb = 'm_tbsipcon'
    else:
        ip_num = info['dip']
        ip_type = info['dipType']
        sdtb = 'm_tbdipcon'

    # 从表m_tbsipcon中取出当前连接之前的所有有日志的数量，加上当前的序号即为iptables规则的序号
    sql = LOG_SQL.format(sdtb, int(info['snum']))
    num = getone(sql)[0]
    order = int(info['snum']) + num

    if process == 'enable':
        process = add_or_del(info['state'])

    if process == 'add' and info['state'] != '0':
        iptable_order(shelve_name, src_or_dst)     
        if int(ip_type) == 1:
            print src_or_dst
            print conname
            iptable_ip = ip_to_iptableip(ip_num, src_or_dst)
            iptables_log, iptables_str, order = ip_(
                src_or_dst, order, iptable_ip,
                int(info['lnumtype']), int(info['iLog']), info['lnum']
            )
        else:
            selectstr = "select HideID from m_tbaddressgroup where id={}".format(ip_num)
            ipgroup = getone(selectstr)[0]
            iptables_log, iptables_str, order = ip_group(
                src_or_dst, order, ipgroup,
                int(info['lnumtype']), int(info['iLog']), info['lnum']
            )
        print 'log: ', iptables_log
        print 'str: ', iptables_str
        run_cmd(iptables_log, iptables_str)

    if process == 'del':
        delete(shelve_name, src_or_dst, conname)


# 为了与旧代码兼容,这里使用了functools.partail(),减少了参数数量
source_connect_limit = partial(
    connect_limit, src_or_dst='source', shelve_name='connlimit-src-shelve'
)
destination_connect_limit = partial(
    connect_limit, src_or_dst='destination',
    shelve_name='connlimit-dst-shelve'
)


def recover():
    cur = mysql_connect_dict()
    source_connect_sql = 'select * from m_tbsipcon where state=1 order by snum'
    cur.execute(source_connect_sql)
    source_connect_info = cur.fetchall()
    for source_connect_data in source_connect_info:
        source_connect_data = str(source_connect_data)
        source_connect_limit('add', source_connect_data)

    des_connect_sql = 'select * from m_tbdipcon where state=1 order by snum'
    cur.execute(des_connect_sql)
    des_connect_info = cur.fetchall()
    for des_connect_data in des_connect_info:
        des_connect_data = str(des_connect_data)
        destination_connect_limit('add', des_connect_data)

    cur.close()


if __name__ == "__main__":
    recover()
