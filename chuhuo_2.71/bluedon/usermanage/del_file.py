#!/usr/bin/env python
# coding=utf-8

"""
php读取后删除用户认证状态的php文件
"""

import os
import sys
import time


os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')


from db.config import mkdir_file

def defl_authenticate_status_file():
    """ 每天晚上9点遍历/tmp/fifo目录，查找所有认证返回值文件
        休眠5分钟后删除该用户认证状态文件
    """

    mkdir_file('/usr/local/bluedon/log/del_authenticate_status_file.log', 'file')

    # 获取用户认证状态文件
    files = os.listdir('/tmp/fifo')
    rzfiles = []
    for item in files:
        if item.startswith('rz') and item[2:].isdigit():
            if os.path.isfile(os.path.join('/tmp/fifo', item)):
                rzfiles.append(item)

    #print rzfiles
    # 睡眠5分钟后删除此次查找到的文件
    time.sleep(300)
    for item in rzfiles:
        filepath = os.path.join('/tmp/fifo', item)
        os.system('/usr/bin/echo "%s" >> /usr/local/bluedon/log/\
                  del_authenticate_status_file.log' %(filepath))
        os.system('/usr/bin/rm -rf %s' %(filepath))


if __name__ == '__main__':
    defl_authenticate_status_file()
