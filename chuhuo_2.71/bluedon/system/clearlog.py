#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import itertools

def clearlog():
    for logfile in os.listdir('/usr/local/bluedon/log'):
        if logfile.endswith('.log'):
            rmlog=os.path.join('/usr/local/bluedon/log',logfile)
            open(rmlog, 'w').close()

    for logfile in os.listdir('/Data/apps/nginx/logs/'):
        if logfile.endswith('.log'):
            rmlog=os.path.join('/Data/apps/nginx/logs/',logfile)
            open(rmlog, 'w').close()

    open('/Data/apps/php7/var/log/php-fpm.log','w').close()
    for logfile in os.listdir('/usr/local/bdwaf/logs/'):
        if logfile.endswith('.log'):
            rmlog=os.path.join('/usr/local/bdwaf/logs/',logfile)
            open(rmlog,'w').close()


if __name__=="__main__":
    clearlog()
