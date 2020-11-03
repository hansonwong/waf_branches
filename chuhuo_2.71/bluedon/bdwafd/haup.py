#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import time
from config import config
from db import conn_scope

def up():
    with conn_scope(**config['db']) as (conn, cursor):
        cursor.execute("update `t_ha_setting` set `state`='master'")
    #now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    #os.system('echo %s:up >> /home/bluedon/keepalivedTest/keepalived.log'% now)

if __name__ == '__main__':
    up()
