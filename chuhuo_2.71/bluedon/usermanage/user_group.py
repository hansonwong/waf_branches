#!/usr/bin/env python
# coding=utf-8

"""
modify log:
    2016-11-4:
        1、用户/用户组
    2016-12-12:
        1、修复批量导入或删除时radiusd服务无法重启的bug
"""


import os
import sys
import codecs
import commands
import base64

from IPy import IP

from db.config import search_data, mkdir_file
from utils.logger_init import logger_init
from core.exceptions import ArgumentError
from core.setting import LOG_BASE_PATH, CMD_SED


CMD = '/usr/sbin'

LOG_PATH = os.path.join(LOG_BASE_PATH, 'user_group.log')
LOG_NAME = 'UserGroup'

COMMANDS = commands.getstatusoutput

logger = logger_init(LOG_NAME, LOG_PATH, 'DEBUG')


def judge_data(msql, flag=True):
    """ 判断查询的记录集是否为空 """

    key_word = ''
    tablename = ''
    condiction = ''
    words = msql.split()
    for word in words:
        if key_word == 'from':
            tablename = word
        elif key_word == 'where':
            condiction = word
        key_word = word.lower()
    results = search_data(msql)
    if not results and flag:
        logger.debug('%s table not %s' %(tablename, condiction))
        return None
    return results

def write_log(content, status=0, output='', action='add', itype='user'):
    """ 把状态和输出信息写到日志 """
    if int(status) == 0:
        logger.info('{0} {1}: {2} success!'.format(action, itype, content))
    else:
        logger.info('{0} {1}: {2} error!'.format(action, itype, content))
        logger.info(output)


class UserGroup(object):
    """ 用户组增删改操作 """

    def __init__(self, data):
        """ 初始化 """

        self.data = data

    def add(self):
        """
        增加用户组
        args:
            None
        return:
            增加成功返回True, 失败返回False
        """

        group_add = '%s/groupadd %s' %(CMD, self.data['sGroupName'])
        (status, output) = COMMANDS(group_add)
        write_log(self.data['sGroupName'], status, output, 'add', 'group')

    def delete(self, u_data):
        """
        删除用户组
        args:
            None
        return:
            True: 全部删除成功
            False: 删除失败
        """

        # 先删除该组下的所有用户再删除该组
        for item in u_data:
            item = {'sUserName': item}
            item.setdefault('iGroupID', self.data['id'])
            user = User(item)
            user.delete()

        group_del = '%s/groupdel %s' %(CMD, self.data['sGroupName'])
        (status, output) = COMMANDS(group_del)
        write_log(self.data['sGroupName'], status, output, 'del', 'group')


class User(object):
    """ 用户的增删改操作 """

    def __init__(self, data):
        """ 初始化 """

        self.data = data

    def modify_cron(self):
        """
        修改crontab文件
        """
        mkdir_file('/etc/cron.d/user_downline', 'file', mod=644)
        os.system('/usr/bin/chmod 644 /etc/cron.d/user_downline')
        os.system(r'%s -i "/%s\>/"d %s' %(CMD_SED, 'cron_del_user.py', '/etc/cron.d/user_downline'))
        del_user = '*/1 * * * * root /usr/bin/python /usr/local/bluedon/usermanage/cron_del_user.py'
        os.system('echo "{0}" >> /etc/cron.d/user_downline'.format(del_user))

    def add(self):
        """
        增加新的用户
        args:
            None
        return:
            True: 增加用户成功
            False: 增加用户失败
        """

        self.modify_cron()   # crontab定时任务
        # 查找用户所属组
        g_sql = 'select * from m_tbgroup where id=%d;'\
                %(int(self.data['iGroupID']))
        result = judge_data(g_sql)
        if not result:
            return
        result = result[0]

        # 添加用户
        # 过期时间
        if int(self.data['iExpiredStatus']) == 1:
            user_add = '%s/useradd -g %s -e %s %s'
            user_add = user_add %(CMD, result['sGroupName'],
                                  self.data['iExpiredTime'].split(' ')[0],
                                  self.data['sUserName'])
        elif int(self.data['iExpiredStatus']) == 0:
            user_add = '%s/useradd -g %s %s'
            user_add = user_add %(CMD, result['sGroupName'],
                                  self.data['sUserName'])

        (status, output) = COMMANDS(user_add)
        write_log(self.data['sUserName'], status, output, 'add', 'user')

        # 本地密码，弃用
        if int(self.data['iLocalPass']) == 0:
            return

        # 设置用户密码
        pw = base64.b64decode(self.data['sPassword'])
        passwd_str = '/usr/bin/echo "%s" | passwd --stdin %s'\
                %(pw, self.data['sUserName'])
        (status, output) = COMMANDS(passwd_str)
        write_log(self.data['sUserName'], status, output, 'change passwd', 'user')

        radius_file(self.data, 'add')

    def delete(self):
        """
        删除用户
        args:
            None
        return:
            True: 删除成功
            False: 表示删除失败
        """

        self.modify_cron()
        user_del = '%s/userdel -f -r %s' %(CMD, self.data['sUserName'])
        (status, output) = COMMANDS(user_del)
        write_log(self.data['sUserName'], status, output, 'del', 'user')

        radius_file(self.data, 'del')


def radius_file(user, add_del):
    """ 把策略ip范围内的用户添加到RADIUS库或删除 """

    file_path = '/etc/raddb/mods-config/files/authorize'
    filepath = codecs.open(file_path, 'r', 'utf-8')
    content_list = filepath.readlines()
    filepath.close()

    if add_del == 'add':
        password = base64.b64decode(user['sPassword'])
        line = '''%s Auth-Type:= CHAP, Cleartext-Password:= "%s"
                Reply-Message= "Response from localhost server: Hello, %s"\n'''\
                %(user['sUserName'], password, '%{User-Name}')
        # 寻找待插入点(默认插入到文件首行)
        content_list.insert(0, line)
        contents = ''.join(content_list)
    else:
        nums = []
        rex = user['sUserName'] + u' '
        for content in content_list:
            if content.startswith(rex) and 'Auth-Type' in content:
                num = content_list.index(content)
                nums.append(num)
                nums.append(num+1)

        nums = reversed(nums)
        for num in nums:
            content_list.pop(num)
        contents = ''.join(content_list)

    with open(file_path, 'w') as filepath:
        filepath.write(contents)

    os.system('systemctl start radiusd.service')
    #os.system('/usr/bin/killall radiusd')
    #os.system('/usr/sbin/service radiusd restart')


def main(action):
    """ 主函数 """

    # 删除用户
    u_sql = 'select * from m_tbusers;'
    u_datas = search_data(u_sql)
    for item in u_datas:
        user = User(item)
        user.delete()
    # 删除用户组
    g_sql = 'select * from m_tbgroup;'
    g_datas = search_data(g_sql)
    for item in g_datas:
        user_group = UserGroup(item)
        user_group.delete([])

    if action == 'reboot':
        # 新增用户组
        for item in g_datas:
            user_group = UserGroup(item)
            user_group.add()
        # 新增用户
        for item in u_datas:
            user = User(item)
            user.add()


if __name__ == '__main__':

    if len(sys.argv) < 2:
        logger.debug('more args (eg: python -m usermanage.user_group reboot/init)')
    else:
        main(sys.argv[1])
