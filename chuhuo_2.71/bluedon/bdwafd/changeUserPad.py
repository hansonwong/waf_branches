#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hashlib
from config import config
from docopt import docopt
from db import conn_scope

def check_user(userName):
    with conn_scope(**config['db']) as (conn, cursor): 
        cursor.execute("select username from t_user where username='%s'"%(userName))
        databasesUserName = cursor.fetchone()
        if not databasesUserName:
            print '0',
            sys.exit(0)
    print '1',
    sys.exit(1)    
            


def change_pad(userName, pad):
    with conn_scope(**config['db']) as (conn, cursor):
        passWord = hashlib.md5(hashlib.md5(pad).hexdigest()+userName).hexdigest()
        cursor.execute("update t_user set password='%s' where username='%s'"%(passWord, userName))
    print '1',
    sys.exit(1)

if __name__ == "__main__":
    doc = """ 
Usage:
  changeUserPad.py -username [USERNAME] -passwd [PASSWORD]

Arguments:
   USERNAME username
   PASSWORD password

Options:
  -h --help                  show this help message and exit
  -v --version               show version and exit
  -username USERNAME         username
  -passwd PASSWORD           password
"""
    args = docopt(doc, version='1.0.0')  
    userName = args["USERNAME"]
    passWord =  args["PASSWORD"]
    if not passWord:
        check_user(userName)
    else:    
        change_pad(userName, passWord)
