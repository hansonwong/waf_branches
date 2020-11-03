#!/usr/bin/env python
# coding=utf-8


"""
用户下线
"""


import os
import sys
import time
import json


os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from usermanage.authentication import auth_downline, logger
from db.config import mkdir_file


def user_down_line():
    """ 对比/tmp/user/下在线用户文件和/usr/local/bluedon/conf/online_users
    中的在线用户，找出下线的用户，并删除其ipset和在线状态"""

    # php在线用户，正在认证的用户，认证通过的用户
    php_user_path = '/tmp/user/'
    php_users = set(os.listdir(php_user_path))

    os.system('/usr/bin/rm -rf /tmp/user/*')

    # python在线用户，json dict
    python_user_path = '/usr/local/bluedon/conf/online_users'
    if not os.path.exists(python_user_path):
        mkdir_file(users_login_path, 'file')
        logger.debug('online_users is not creat, now creat!')
        return
    else:
        try:
            with open(python_user_path, 'r') as fp:
                content = fp.read()
                if '\n' == content:
                    logger.info('online_users is null')
                    return
        except IOError as e:
            logger.debug(e)
            return

    content = json.loads(content)

    py_users = set()  # python记录的上线用户
    for k, v in content.iteritems():
        line = v[0] + '_' + k # username_ip
        py_users.add(line)

    logger.info('php users: %s' %(', '.join(php_users)))
    logger.info('py users: %s' %(', '.join(py_users)))

    # 此轮下线用户
    users = py_users.difference(php_users)

    if not users:
        return

    del_users = dict()
    del_users_path = '/usr/local/bluedon/conf/del_users'
    if not os.path.exists(del_users_path):
        mkdir_file(del_users_path, 'file')
    else:
        with open(del_users_path, 'r') as fp:
            delusers = fp.read()
            if delusers:
                del_users = json.loads(delusers)

    # 确认是否3次下线, 是则删除, 否则计数器增1
    down_users = set()
    for item in users:
        if item in del_users:
            if del_users[item] >= 3:
                down_users.add(item)
                del_users.pop(item)
            else:
                del_users[item] = del_users[item] + 1
        else:
            del_users[item] = 1

    try:
        with open(del_users_path, 'w') as fp:
            fp.write(json.dumps(del_users))
    except IOError as e:
        logger.debug(e)

    #print del_users
    for user in down_users:
        data = {}
        username, sip = user.rsplit('_', 1)
        logger.info('user downline: %s %s' %(username, sip))
        data['sUserName'] = username
        data['sIP'] = sip
        data['sPassword'] = ''
        data['filename'] = ''
        auth_downline(data)


if __name__ == '__main__':
    user_down_line()
