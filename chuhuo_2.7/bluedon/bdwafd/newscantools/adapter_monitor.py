#!/usr/bin/env python
#-*-encoding:UTF-8-*-

##################################
#
#     author:kun yin
#     tutor:yuying xia
#     date:9/19/2014
#
##################################

from lib.common import vulscan_popen
import os
import sys
import time
from lib.common import init_log
import logging

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

def main():
    try:
        os.system("service apache2 recheck")
        while 1:
            time.sleep(1)
            if not vulscan_popen(' ps -ef| grep /usr/sbin/apache2 | grep -v grep'):
                time.sleep(10)
                if not vulscan_popen(' ps -ef| grep /usr/sbin/apache2 | grep -v grep'):
                    filepath = sys_path('/waf/apache_IPv6.py')
                    os.system("/usr/bin/python %s"%filepath)
                    time.sleep(2)
                    os.system("service apache2 start")
                    logging.getLogger().error("File:adapter_monitor.py, apache2 recheck")
    except Exception,e:
        logging.getLogger().error("File:adapter_monitor.py main() "+str(e))


if __name__ == '__main__':
    logfilepath = sys_path('/log/')
    init_log(logging.ERROR,logging.ERROR,logfilepath+os.path.split(__file__)[1].split(".")[0]+".log")
    main()
