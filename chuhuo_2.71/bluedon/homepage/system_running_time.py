#!/usr/bin/python
#-*- coding: utf-8 -*-
import commands


def system_running_time():
    s = commands.getoutput('uptime').split()
    if len(s) == 10:
        d = 0
    else:
        d = s[2]
    if len(s[-8].split(':')) < 2:
        d = 0
        h = 0
        m = s[-9]
    else:
        h = s[-8].split(':')[0]
        m = s[-8].split(':')[1].rstrip(',')
    res = '%s天%s小时%s分' % (d,h,m)
    return res 

if __name__ == '__main__':
    res = system_running_time()
    print res
