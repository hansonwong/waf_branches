#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import time
import sys
from db import conn_scope
from config import config

def getIp():
    with conn_scope(**config['db']) as (conn, cursor):
        cursor.execute("select ip from t_nicset where nic='eth0'")
        result = cursor.fetchall()[0][0]
        return result


def checkWaf(Ip):
    #now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    #os.system('echo %s:check >> /home/bluedon/keepalivedTest/keepalived.log'% now)
    pathname = '/usr/local/bluedon/bdwaf/logs/access.log'
    os.popen('curl http://%s'%Ip)
    mtime =  os.stat(pathname).st_mtime
    nowtime = time.time()
    if not (nowtime - 1 < mtime < nowtime + 1):
        exit(1)
    exit(0)


if __name__ == '__main__':
    checkWaf(getIp())
