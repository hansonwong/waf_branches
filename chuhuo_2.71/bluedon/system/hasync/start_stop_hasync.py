#!/usr/bin/env python
# coding=utf-8


import json
import os
import sys
import time

from db.mysql_db import select_one
from system.hasync.sync_config import logger

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')



service_path = '/usr/lib/systemd/system'
conf_path = '/usr/local/bluedon/conf'
service_file = ['hasync_deal_data.service', 'hasync_mysql_observer.service']

def judge_service_file():
    """ 判断/usr/lib/systemd/system目录下是否存在监控数据表以及处理数据进程文件 """
    for item in service_file:
        file_path = os.path.join(service_path, item)
        if not os.path.exists(file_path):
            os.system('/usr/bin/scp {0} {1}'.format(os.path.join(conf_path, item), file_path))
    os.system('systemctl daemon-reload')

def get_who():
    """ 获取设备是否为主机 """
    try:
        with open('/etc/keepalived/status.conf', 'r') as fp:
            line = fp.read().strip()
    except IOError as e:
        logger.info('open /etc/keepalived/status.conf error')
        logger.debug(e)
        return 'backup'
    return line.lower()

def sync_main(action):
    """ 入口 """
    judge_service_file()
    os.system('systemctl stop hasync_mysql_observer')
    os.system('systemctl stop hasync_deal_data')
    os.system('systemctl kill hasync_mysql_observer')
    os.system('systemctl kill hasync_deal_data')
    ha_info = select_one('select sValue from m_tbconfig where sName="HaSetting"')
    syn_onoff = json.loads(ha_info['sValue']).get('iSynchronizeSet','0') 
    print 'syn_onoff',syn_onoff
        
    if action == 'stop' or syn_onoff =='0':
        return
    if action == 'master':
        # sync进程执行一系列动作需要一定时间, 才更新状态配置文件

        os.system('systemctl start hasync_mysql_observer')
        logger.info('start hasync_mysql_observer')
    elif action == 'backup':
        os.system('systemctl start hasync_deal_data')
        logger.info('start hasync_deal_data')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.debug('more args (eg: python -m system.hasync.start_stop_hasync master/backup/fault)')
    else:
        sync_main(sys.argv[1])
