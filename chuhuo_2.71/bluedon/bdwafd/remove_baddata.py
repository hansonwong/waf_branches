#! /usr/bin/env python
# -*- coding:utf-8 -*-


import MySQLdb
from config import config

def remove_baddata():
    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()    
    cursor.execute('select * from t_bridge')
    for data in cursor.fetchall():
        print data

if __name__=='__main__':
   remove_baddata()
