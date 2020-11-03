#! /usr/bin/env python 
# -*- coding:utf-8-*-


from config import config
from db import conn_scope
import os
weblogfile  = '/var/log/weboutlog'
backipfile   = '/proc/net/xt_recent/DROPLINK'

def test():
    with open('logs','r') as fr:
         lines=fr.readlines()
         for line in lines:
             print line

if __name__=="__main__":
   test()

   
 
