#! /usr/bin/env python
# -*- coding:utf-8 -*-

from time import struct_time, gmtime, mktime
import os
from logging import getLogger
# from itertools import islice

# from os.path import getsize
# from config_sql import execute_sql_logs, fetchone_sql

# """put in somewhere"""
# def create_linking_num_log_table():
#     sql = """CREATE TABLE IF NOT EXISTS `t_linking_num_log_size` (
#       `id` int(20) NOT NULL AUTO_INCREMENT,
#       `size` bigint(20) DEFAULT NULL COMMENT 'linking num log',
#       PRIMARY KEY (`id`)
#     ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;"""
#     execute_sql_logs(sql)
#     sql_get = 'select * from logs.t_linking_num_log_size '
#     result = fetchone_sql(sql_get)
#     if not result:
#         execute_sql_logs('insert into t_linking_num_log_size(size) values("0")')
#
#
# def getoldsize():
#     size = fetchone_sql('select * from logs.t_linking_num_log_size')[1]
#     return size
#
# """"clear disk task should call this func after remove the log"""
# def savenewsize(path_to_file, table_name='t_linking_num_log_size'):
#     newsize = getsize(path_to_file)
#     sql = "UPDATE %s SET size=%d" % (table_name, newsize)
#     execute_sql_logs(sql)

def reversed_lines(file):
    "Generate the lines of file in reverse order."
    part = ''
    for block in reversed_blocks(file):
        for c in reversed(block):
            if c == '\n' and part:
                yield part[::-1]
                part = ''
            part += c
    if part: yield part[::-1]

def reversed_blocks(file, blocksize=4096):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        yield file.read(delta)

def close_enough(utc1, utc2, precision):
    epoch1 = mktime(utc1)
    epoch2 = mktime(utc2)
    #getLogger('main').info("close_enough")
    #getLogger('main').info(utc1)
    #getLogger('main').info(utc2)
    #getLogger('main').info(epoch1)
    #getLogger('main').info(epoch2)
    distance = abs(epoch1 - epoch2)
    if distance < precision:
        return True
    return False

def have_passed_py(utc1, utc2, precision):
    epoch1 = mktime(utc1)
    epoch2 = mktime(utc2)
#    getLogger('main').info("passed")
#    getLogger('main').info(utc1)
#    getLogger('main').info(utc2)
#    getLogger('main').info(epoch1)
#    getLogger('main').info(epoch2)
    distance = epoch1 - epoch2
    if distance >= precision:
#        getLogger('main').info("havevvvvvvvvvvpassed")
        return True
    return False

# def check_last_10_lines(file, key):
#     for line in islice(reversed_lines(file), 10):
#         if line.rstrip('\n') == key:
#             print 'FOUND'
#             break



def parse_log(utc, iplist, precision1=1, precision2=2, path_to_file='linking_num.log'):
    if not isinstance(utc, struct_time)  or not isinstance(iplist, list) :
        raise TypeError
    #size=getoldsize()
    dict_ = {}
    with open(path_to_file, "r") as fp:
#        #fp.seek(size)
        for line in reversed_lines(fp):
            line = line.split(',')
            logtime = gmtime(int(line[1][5:]))
            if have_passed_py(utc, logtime, precision2):
                break
            ip = line[3][3:]
    #        getLogger('main').info("pl"+ip)
   #         getLogger('main').info(iplist)
            if ip not in iplist:
                continue
            if not close_enough(utc, logtime, precision1):
                continue
            #print line
            dict_['NEW_LINK_NUM'] = int(filter(str.isdigit, line[4]))
            dict_['CURRENT_LINK_NUM'] = int(filter(str.isdigit, line[5]))
            dict_['TRANSACTION_NUM'] = int(filter(str.isdigit, line[6]))
            #savenewsize(path_to_file)
            return dict_
    #savenewsize(path_to_file)
   # getLogger('main').info("parse_log {}")
    return dict_


if __name__ == '__main__':
    # time = gmtime(1473133486)
    # iplist = ['172.16.2.106']
    # r = parse_log(time, iplist)
    # print r
    pass
