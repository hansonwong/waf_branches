#!/usr/bin/env python
# -*- coding=utf-8 -*-


"""
2016-08-19:
    把需同步的表数据/配置文件导出打包发送到对端
"""


import os
import time
import json

from db.config import execute_sql
from system.hasync.sync_config import cf, logger, SYNC_FILE, SEND_FILE, KEY, BASEPATH


TABLES = cf.sections()
TABLES.remove('files')
TABLE_FILE = os.path.join(BASEPATH, 'sync_tar_table')
CONF_FILE = os.path.join(BASEPATH, 'sync_tar_conf')
TAR_CMD = 'tar -zcvf - {infp} -P|openssl des3 -salt -k {key} | dd of={outfp}/{fn}'


def judge_lock_file():
    # 判断是否存在锁文件，存在则说明对端还在处理数据，
    # 需等待对端处理完才发送新待同步数据
    lockfile = os.path.join(SYNC_FILE, 'lock_file')
    count = 0
    while count < 15:
        if os.path.exists(lockfile):
            #print 'have lock_file'
            time.sleep(1)
            count += 1
        else:
            break


def dump_table_data(tables=[]):
    """
    导出表数据
    """
    if not tables:
        logger.info('not sync tables!')
        return

    judge_lock_file()
    # 删除上次待打包的备份文件(因为文件名存在则会备份失败)
    os.system('rm -rf {0}/*'.format(TABLE_FILE))

    # 如果不存在待打包文件路径则创建并修改权限
    if not os.path.exists(TABLE_FILE):
        os.system('mkdir -p {0}'.format(TABLE_FILE))
        os.system('chmod 777 {0}'.format(TABLE_FILE))
    if not os.path.exists(CONF_FILE):
        os.system('mkdir -p {0}'.format(CONF_FILE))
        os.system('chmod 777 {0}'.format(CONF_FILE))

    dump_sql = """SELECT * INTO OUTFILE '{filepath}/{filename}' FIELDS
                TERMINATED BY '|' OPTIONALLY ENCLOSED BY '"' LINES
                TERMINATED BY '\r\n' FROM {tablename} {where}"""

    logger.info('sync_send_table: {0}'.format(tables))
    for tb in tables:
        if 'sql_where' in dict(cf.items(tb)):
            where_str = json.loads(dict(cf.items(tb))['sql_where'])[0]
        else:
            where_str = ' '

        # m_tbconfig配置表另行处理
        if tb == 'm_tbconfig':
            dump_sql_config = """SELECT sName, sValue, sMark, sCommand INTO OUTFILE '{filepath}/{filename}' FIELDS
                        TERMINATED BY '|' OPTIONALLY ENCLOSED BY '"' LINES
                        TERMINATED BY '\r\n' FROM {tablename} {where}"""
            sql = dump_sql_config.format(filepath=TABLE_FILE, filename=tb,
                                        tablename=tb, where=where_str)
        elif tb=='m_tbnetport':
            dump_netport_sql = """SELECT sPortName,exStatus INTO OUTFILE '{filepath}/{filename}' FIELDS
                        TERMINATED BY '|' OPTIONALLY ENCLOSED BY '"' LINES
                        TERMINATED BY '\r\n' FROM {tablename}"""
            sql = dump_netport_sql.format(filepath=TABLE_FILE,filename=tb,tablename=tb)

        else:
            sql = dump_sql.format(filepath=TABLE_FILE, filename=tb,
                                  tablename=tb, where=where_str)
        #print sql
        execute_sql(sql)
    os.system(TAR_CMD.format(infp=TABLE_FILE, key=KEY, outfp=SEND_FILE, fn='synctbdata.sing'))

def dump_file_data(files=None):
    # 同步相关文件
    if not files:
        logger.info('not sync file!')
        return

    judge_lock_file()
    # 删除上次待打包的备份文件(因为文件名存在则会备份失败)
    os.system('rm -rf {0}/*'.format(CONF_FILE))

    cp_cmd = 'cp --parents -p {0} {1}'
    cp_list = json.loads(dict(cf.items(files)).get('cp_file', '[]'))
    for item in cp_list:
        if 'online_users' in item:
            line = ''
            with open(item, 'r') as fp:
                line = fp.read()
            logger.info('send online users: {}'.format(line))
        cmd = cp_cmd.format(item, CONF_FILE)
        #print cmd
        os.system(cmd)
        logger.info('sync_send_file: {0}'.format(cmd))
    os.system(TAR_CMD.format(infp=CONF_FILE, key=KEY, outfp=SEND_FILE, fn='synccfdata.sing'))


if __name__ == '__main__':
    # dump_table_data(['m_tbconfig'])
    TABLES = cf.sections()
    dump_table_data(TABLES)
