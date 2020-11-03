#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import MySQLdb
import sys
from subprocess import Popen, PIPE

sys.path.append("/usr/local/bluedon/bdwafd/")
from common import logger_init
from config import config
from db import session_scope, DevInfo
from logging import getLogger
from backupeveryday import procbackup

dbconfig = {
    'host':'localhost',
    'user':'root',
    'passwd':'bd_123456',
    'db':'waf',
    'port':3306,
    'charset':'utf8',
    'use_unicode':False
}

class Update_Waf:
    def __init__(self):
        '''
        初始化:
        1.将需要的文件按照属性进行分类
        2.获取运行的绝对路径
        '''
        self.obj_home = os.getcwd()
        self.sql_files = []
        self.tar_files = []
        self.sh_files = []
        self.ver_files = []
        self.patch_info = {}
        keyword = {
            '.sql': self.sql_files,
            '.sh': self.sh_files,
            '.tar': self.tar_files,
            '.ver': self.ver_files
        }
        for dir_name in os.listdir(self.obj_home):
            extension_name = os.path.splitext(dir_name)[1]
            if extension_name and extension_name in keyword:
                keyword[extension_name].append(dir_name)

    def checkver(self):
        """
        检查更新包适用的版本更新，.ver文件格式如下：
            patch_type:rule_ver or sys_ver
            patch_ver:1.1.1.3
            min:1.1.1.1
            max:1.1.1.2
        """
        # get pre_ver info
        if not self.ver_files:
            return False
        ver_file =self.ver_files[0]
        lines = []
        with open(ver_file) as fileobj:
            lines = fileobj.readlines()
        for line in lines:
            info = line.split(':')
            self.patch_info[info[0]] = info[1].strip()
        # get sys_ver
        db = MySQLdb.connect(**config['db'])
        cursor = db.cursor()
        cursor.execute('select %s from t_devinfo' % self.patch_info['patch_type'])
        version = cursor.fetchone()[0]
        # compare sys_ver and pre_verinfo
        # TODO:完善版本判断规则
        if version >= self.patch_info['min'] and version <= self.patch_info['max']:
            return True
        return False

    def run_sql(self):
        '''
        备份数据库于当前文件夹
        运行sql文件,更新数据库, 成功返回True
        若sql执行失败 还原数据库 返回False
        '''
        getLogger('main').info('backup waf database')
        dbsaver = os.system("mysqldump -u%s -p'%s' waf >> %s/backup.sql"%(dbconfig['user'], dbconfig['passwd'], self.obj_home))
        for sql_file in self.sql_files:
            getLogger('main').info('source sql file: %s' % sql_file)
            result = os.system("mysql -u%s --password='%s' -e 'source %s/%s'" % (dbconfig['user'], dbconfig['passwd'], self.obj_home, sql_file))
            if result != 0:
                getLogger('main').info('update database fail!')
                return False
        os.system('rm -rf %s/backup.sql' % self.obj_home)
        getLogger('main').info('patch update database success!')
        return True

    def run_overwrite(self):
        '''
        运行解压操作，覆盖旧文件
        '''
        if not self.tar_files:
            return
        print 'tar files found'
        for tar_file in self.tar_files:
            print 'decompress tar file %s' % tar_file
            os.system('tar xfP %s' % tar_file)
        print 'file decompress done'


    def run_update(self):
        '''
        运行环境配置脚本
        '''
        if not self.sh_files:
            return
        print 'sh files found'
        for sh_file in self.sh_files:
            os.popen('chmod +x ./%s'%sh_file)
            result = os.popen('./%s'%sh_file)
            print result.read()
    
    def update_rule(self):
        if self.sql_files:
            if not self.run_sql():
                getLogger('main').info("Update database fail!")
                return False
        self.run_overwrite()
        self.run_update()
        return True
    
    def update_sys(self):
        if self.sql_files:
            print "sql files found"
            if not self.run_sql():
                getLogger('main').info("Update database fail!")
                return False
        self.run_overwrite()
        self.run_update()
        return True

    def proc(self):

        # 检查版本是否正确
        # if not checkver():
        #     getLogger('main').info("Patch version isn't satisfied!")
        #     return False
        
        # 备份文件
        # procbackup('%s/' % self.obj_home)     
        
        # 判断补丁包类型
        # if self.patch_info['patch_type'] == "rule_ver":
        #     result = self.update_rule()
        # else if self.patch_info['patch_type'] == "sys_ver":
            # result = self.update_sys()
        
        # 更新数据库版本信息
        #if result:
        #    db = MySQLdb.connect(**dbconfig)
        #    cursor = db.cursor()
        #    cursor.execute('update t_devinfo set `%s`="%s"' % (self.patch_info['patch_type'], self.patch_info['patch_ver']))
        
        # 删除备份文件
        #    os.system('rm -f %s/backup.sql' % self.obj_home)
        
        result = self.update_sys()


if __name__ == "__main__":
    Update_Waf().proc()
    print 'success, restarting services'
    os.system('chown -R www:www /Data/apps/wwwroot/waf/')
    os.system('systemctl restart bdwafd-python-daemon.service')
    os.system('systemctl restart firewall-python-daemon.service')
    os.system('systemctl restart bdauditd-python-daemon.service')
    os.system('systemctl restart mysql_log_daemon.service')
    print 'update done'

