#!/usr/bin/env python
# coding=utf-8

"""
2016-08-12:
    Add get_process_status for PHP, get status of
    mp_server/suricata/bdwaf/nginx/MySQL
"""

from __future__ import division
import os
import psutil
import json

# INFO_PATH = r'/usr/local/bluedon/log/sys_info.json'
INFO_PATH = r'/tmp/sys_info.json'
PROC_STAT = {'mp_server':0,
             'suricata':0,
             'bdwaf':0,
             'nginx':0,
             'mysql':0}

def get_process_status(dct):
    import commands
    if not isinstance(dct, dict):
        return
    get_status = 'ps -ef | grep {proc:} | grep -v grep |wc -l'
    for p in PROC_STAT:
        status, output = commands.getstatusoutput(get_status.format(proc=p))
        PROC_STAT[p] = 1 if int(output) else 0
        dct[p] = PROC_STAT[p]



def get_disk_total_info():
    p_total = 0
    p_used = 0
    for part in psutil.disk_partitions():
        p = part.mountpoint

        p_info = psutil.disk_usage(p)
        p_total += p_info.total
        p_used += p_info.used

    return p_used/1024/1024, p_total/1024/1024

def get_system_usage_info():

    info = {'cpu':0,
            'mem_total': 0, 'mem_used': 0,
            'root_total': 0, 'root_used': 0,
            'var_total': 0, 'var_used': 0
            }

    info['cpu'] = psutil.cpu_percent(interval=1)

    info['mem_total'] = psutil.virtual_memory().total/1024
    info['mem_used'] = psutil.virtual_memory().used/1024

    root_info = psutil.disk_usage('/')
    info['root_total'] = root_info.total/1024/1024
    info['root_used'] = root_info.used/1024/1024

    var_info = psutil.disk_usage('/var')
    info['var_total'] = var_info.total/1024/1024
    info['var_used'] = var_info.used/1024/1024

    for key in info:
        if key == 'cpu':
            pass
        else:
            info[key] = int(round(info[key]))

    get_process_status(info)
    # for key in PROC_STAT:
    #     info[key] = PROC_STAT[key]



    os.system('')
    js = json.dumps(info)
    with open(INFO_PATH, 'w') as fp:
        fp.write(js)



if __name__ == '__main__':
    get_system_usage_info()
    pass
