#/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, re, MySQLdb
from config import config

set_devL = raw_input('请输入设备型号,示例：BD-WAF-M4000: ')
set_devS = raw_input('请输入SN,示例：0310890110: ')

def add_devtype():
    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()
    cursor.execute("update t_devinfo set model='%s',serial_num='%s'" % (set_devL,set_devS) )

    conn.commit()
    cursor.close()
    conn.close()

if 'BD-WAF' in set_devL and '0310' in set_devS : 
    add_devtype()
    print '添加成功'
else :
    print '设备型号或者SN有误'

