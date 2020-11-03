#!/usr/bin/env python
#-*-encoding:UTF-8-*-
#Author: jianxiao@yxlink.com 
#Date: 2011.2.18

import os
import logging


def start_nginx():
    os.system("/usr/bin/service nginx start")
    
def stop_nginx():
    os.system("/usr/bin/service nginx stop")
    
def restart_nginx():
    stop_nginx()
    start_nginx()

    
def save_nginx_conf(conf,filename="/etc/nginx/nginx.conf"):
    try:
        ngxfile=open(filename,"w")
        ngxfile.write(conf)
        ngxfile.close()
    except Exception,e:
        logging.getLogger().debug("save_nginx_conf Exception:" + str(e))
        return -1
    
def test_nginx_conf(conf):
    testfilename="/etc/nginx/nginx.conf.test"
    save_nginx_conf(conf,testfilename)
    return os.system("/usr/sbin/nginx -t -c %s"%testfilename)

def remove_nginx_conf(conf):
    os.system("/bin/rm /etc/nginx/nginx.conf")

