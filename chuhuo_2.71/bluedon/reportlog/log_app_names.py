#!/usr/bin/env python
# coding=utf-8
import os
pwd = os.getcwd()
def get_app_names_old(path=os.path.join(pwd, 'nDPI_support_protocol_list.txt')):
    try:
        with open(path,'r') as fp:
            lines = fp.readlines()
    except IOError:
        path = os.path.join(pwd, 'reportlog/nDPI_support_protocol_list.txt')
        with open(path,'r') as fp:
            lines = fp.readlines()
    name = lambda x:x.split(',')[1].strip('\n')
    names = [ name(line) for line in lines ]
    return names


"""
get app names from database `m_tbndpi_protocol`
"""
def get_app_names():
    from db.config import fetchall_sql as fcal_3306

    names = dict()
    # sql = ("SELECT sAppName FROM m_tbndpi_protocol;")
    sql = ("SELECT sName, app_id_ten FROM m_tbdefault_app_list;")
    for res in fcal_3306(sql):
        names[int(res['app_id_ten'])] = res['sName']
    return names


if __name__ == '__main__':
    lines = get_app_names()
    print lines
    # lines = get_app_names_tb()
    # for l in lines:
    #     print l
    pass


