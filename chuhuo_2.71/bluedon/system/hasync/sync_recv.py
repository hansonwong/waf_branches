#!/usr/bin/env python
# -*- coding=utf-8 -*-


"""
2016-08-19:
    把HA中发送过来的数据进行同步操作
"""


import os
import json

from db.config import execute_sql, search_data
from utils.app_mark_count import default_scount_field
from system.hasync.sync_config import cf, logger
from system.system_config import sys_config_processer
from logging import  getLogger
from db.mysql_db import update


TABLES = cf.sections()
TABLES.remove('files')

def load_to_file(files=None):
    """
    同步配置文件
    args:
        files: list，待copy配置文件的全路径
    """

    if not files:
        #print 'not config file'
        logger.info('not conf file!')
        return

    flag = False
    #os.system('echo "" > /usr/local/bluedon/tmp/syncfile')
    for item in files:
        to_dir = item.split('sync_tar_conf')[1]
        cp_cmd = 'cp -r -p {0} {1}'.format(item, to_dir)
        ##print cp_cmd
        #os.system('echo "{0}" >> /usr/local/bluedon/tmp/syncfile'.format(cp_cmd))
        os.system(cp_cmd)
        if 'online_users' == item.rsplit('/', 1)[1]:
            #cp_to_tmp = 'cp -r -p {0} {1}'.format(item, '/usr/local/bluedon/tmp/')
            #os.system(cp_to_tmp)
            #logger.info(cp_to_tmp)
            flag = True
            line = ''
            with open(item, 'r') as fp:
                line = fp.read()
            logger.info('recv online user: {}'.format(line))
        logger.info(cp_cmd)

    # 执行完所有开机恢复后再设置ipset
    if flag:
        try:
            with open('/usr/local/bluedon/conf/online_users', 'r') as fp:
                contents = fp.read()
                if '\n' == contents:
                    contents = {}
                else:
                    contents = json.loads(contents) if contents else {}
        except Exception as e:
            contents = {}
            logger.debug(e)

        #os.system('echo "{}" >> /usr/local/bluedon/tmp/synctables'.format(contents))
        os.system('/usr/local/sbin/ipset -F authed_set')
        for content in contents:
            ipset_cmd = '/usr/local/sbin/ipset add authed_set %s' %(content)
            logger.info(ipset_cmd)
            os.system(ipset_cmd)

    os.system('rm -rf /home/rsync/send/lock_file')
    logger.info('all deal files!!!')


def load_to_mysql(tables=None):
    """
    同步数据库
    args:
        tables: dict，key=表名称，value=表数据路径
    """

    if not tables:
        #print 'not table file'
        logger.info('not table file!')
        return

    def process_init_reboot(tb, action):
        if action in dict(cf.items(tb)):
            cmd_lst = json.loads(dict(cf.items(tb)).get(action, '[]'))
            getLogger('main').info(cmd_lst)
            for item in cmd_lst:
                logger.info('{0} {1} {2}'.format(tb, action, item))
                #print item
                os.system(item)

    load_data_infile = """load data infile '{filepath}' ignore into table
                        `{tablename}` character set utf8 fields TERMINATED BY
                        '|' ENCLOSED BY '"' LINES TERMINATED BY '\r\n'"""

    # 如果是安全策略, 策略路由, 流控则先清空应用计数表和APPMARK链
    for item in ["m_tbSearitystrate", "m_tbflow_socket"]:
        if item in tables:
            os.system('/usr/sbin/iptables -t mangle -F APPMARK')
            default_scount_field()
            break

    for tb in tables:
        if tb in ['m_tbconfig', 'm_tbusers_authentication_tactics','m_tbnetport']:
            continue
        process_init_reboot(tb, 'init')
        execute_sql('delete from {0}'.format(tb))
        execute_sql(load_data_infile.format(filepath=tables[tb], tablename=tb))
        process_init_reboot(tb, 'reboot')
        logger.info('deal table: {}'.format(tb))
   
    #ipmac绑定,同步例外网口,只同步表m_tbnetport的字段'exStatus' 
    if 'm_tbnetport' in tables:
        for line in open(tables['m_tbnetport'],'r'):
            info = line.strip('\r\n').split('|')
            update('update m_tbnetport set exStatus=%s where sPortName=%s'%(info[1],info[0]))
        process_init_reboot('m_tbnetport', 'reboot')

                    
    # 单独处理m_tbconfig配置表[此表还存有其它配置文件, 不能直接覆盖]
    tbconfig = 'm_tbconfig'
    if tbconfig in tables:
        load_data_infile_config = """load data infile '{filepath}' ignore into table
                            `{tablename}` character set utf8 fields TERMINATED BY
                            '|' ENCLOSED BY '"' LINES TERMINATED BY '\r\n'
                            (`sName`, `sValue`, `sMark`, `sCommand`)"""
        if 'sql_where' in dict(cf.items(tbconfig)):
            where_str = json.loads(dict(cf.items(tbconfig))['sql_where'])[0]
        else:
            where_str = ' '
        if where_str:
            process_init_reboot(tbconfig, 'init')
            del_cmd = 'delete from m_tbconfig {0}'.format(where_str)
            execute_sql(del_cmd)
            execute_sql(load_data_infile_config.format(filepath=tables[tbconfig], tablename=tbconfig))
            process_init_reboot(tbconfig, 'reboot')
            data = search_data('select sValue from m_tbconfig where sName="TimeSet";')
            if data and data[0]['sValue']:
                getLogger('main').info(data[0]['sValue'])
                os.system('python -m system.restore_sys_config &')
            logger.info('deal table: {}'.format(tbconfig))


    # 单独处理用户认证--> 策略表(推送页ip需是本机网口ip)
    tbauth = 'm_tbusers_authentication_tactics'
    if tbauth in tables:
        process_init_reboot(tbauth, 'init')
        execute_sql('delete from {0}'.format(tbauth))
        execute_sql(load_data_infile.format(filepath=tables[tbauth], tablename=tbauth))
        #推送页ip替换为本机该网卡ip
        auth_sql = 'select sAuthNetport from {0} where sAuthNetport!=""'.format(tbauth)
        update_sql = 'update {0} set sTuisongIp="{1}" where sAuthNetport="{2}"'
        del_sql = 'delete from {0} where sAuthNetport="{1}"'
        datas = search_data(auth_sql)
        if datas:
            ports = ['sPortName="{0}"'.format(data['sAuthNetport']) for data in datas]
            port_sql = 'SELECT sIPV4Address, sPortName from m_tbnetport where {0}'.format(' or '.join(ports))
            results = search_data(port_sql)
            for result in results:
                port = result['sPortName']
                ip4 = result['sIPV4Address'].split(',')[0].split('/')[0] if result['sIPV4Address'] else ''
                if ip4:
                    execute_sql(update_sql.format(tbauth, ip4, port))
                else:
                    execute_sql(del_sql.format(tbauth, port))
            process_init_reboot(tbauth, 'reboot')
            logger.info('deal table {}'.format(tbauth))

        #tables.pop(tbauth)

    os.system('rm -rf /home/rsync/send/lock_file')
    logger.info('all deal tables!!!')


if __name__ == '__main__':
     #tables = {'m_tbconfig': '/usr/local/bluedon/tmp/hasync/sync_tar_table/m_tbconfig'}
     tables = {'m_tbusers_authentication_tactics': ''}
     load_to_mysql(tables)
