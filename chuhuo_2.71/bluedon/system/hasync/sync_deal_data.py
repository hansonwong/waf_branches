#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
2016-08-19:
    处理待同步数据
"""


import os
import time
from commands import getstatusoutput
from utils.logger_init import logger_init

from .sync_recv import load_to_mysql, load_to_file
from utils.file_handling import folders_walker
from db.config import mkdir_file
from system.hasync.sync_config import logger, SYNC_FILE, SEND_FILE, KEY, BASEPATH


UPDATE_CONF = os.path.join(BASEPATH, 'sync_update_conf')
UPDATE_TABLE = os.path.join(BASEPATH, 'sync_update_table')
tar_table = os.path.join(SYNC_FILE, 'synctbdata.sing')
tar_conf = os.path.join(SYNC_FILE, 'synccfdata.sing')

UNTAR_CMD = 'dd if={in_file}|openssl des3 -d -k {key}|tar zxf - --strip-components 1 -C {out_path}'


def main():
    """ 函数入口 """


    # touch lock_file 文件到主端，告知正在处理数据，勿传新数据
    lockfile = os.path.join(SEND_FILE, 'lock_file')
    os.system('touch {0}'.format(lockfile))

    # 如果不存在存放解压文件的路径则创建并修改权限
    if not os.path.exists(UPDATE_TABLE):
        os.system('mkdir -p {0}'.format(UPDATE_TABLE))
        os.system('chmod 777 {0}'.format(UPDATE_TABLE))
    if not os.path.exists(UPDATE_CONF):
        os.system('mkdir -p {0}'.format(UPDATE_CONF))
        os.system('chmod 777 {0}'.format(UPDATE_CONF))


def deal_sync_conf_data(file_path):
    """
    解压同步配置文件并同步
    """

    # 删除上次待同步配置文件
    os.system('rm -rf {0}/*'.format(UPDATE_CONF))

    status, output = getstatusoutput(UNTAR_CMD.format(in_file=file_path,
                                                      key=KEY,
                                                      out_path=UPDATE_CONF))
    if status:
        logger.debug('extract conf file error!')
        #print output
        #print 'deal conf erro'
        return

    conffiles = []
    for filename in folders_walker(UPDATE_CONF):
        conffiles.append(filename)

    #print conffiles
    load_to_file(conffiles)
    #print 'success deal sync conf'

def deal_sync_table_data(file_path):
    """ 解压表同步文件并同步 """

    # 删除上次待同步表数据文件
    os.system('rm -rf {0}/*'.format('/usr/local/bluedon/tmp/hasync/sync_update_table'))
    
    #将数据解压到/usr/local/bluedon/tmp/hasync/sync_update_table
    status, output = getstatusoutput(UNTAR_CMD.format(in_file=file_path,
                                                      key=KEY,
                                                      out_path='/usr/local/bluedon/tmp/hasync/sync_update_table'))
    if status:
        logger.debug('extract table file error!')
        return
    
    tables = {}
    for file_name in folders_walker('/usr/local/bluedon/tmp/hasync/sync_update_table'):
        key = file_name.rsplit('/', 1)[1]
        tables[key] = file_name

    load_to_mysql(tables)

def run():
    df = {'tb': tar_table, 'fp': tar_conf}
    # 判断是否存在待同步的数据
    for key in df:
        if not os.path.exists(df[key]):
            logger.info('not {}, now create ...'.format(df[key]))
            mkdir_file(df[key], 'file')

    tb_m_time = int(os.stat(tar_table).st_mtime)
    cf_m_time = int(os.stat(tar_conf).st_mtime)
    while True:
        if os.path.exists(df['tb']):
            tb_n_time = int(os.stat(tar_table).st_mtime)
            print 'old time',tb_m_time
            print 'new time',tb_n_time
            print  tb_m_time != tb_n_time
            if tb_m_time != tb_n_time:
                tb_m_time = tb_n_time
                main()
                deal_sync_table_data('/home/rsync/recv/synctbdata.sing')
        if os.path.exists(df['fp']):
            cf_n_time = int(os.stat(tar_conf).st_mtime)
            if cf_m_time != cf_n_time:
                cf_m_time = cf_n_time
                main()
                deal_sync_conf_data('/home/rsync/recv/synccfdata.sing')
        time.sleep(5)


if __name__ == '__main__':
    #在同步前，备设备得先同步所有表，以达到与主设备的配置环境一致
    main()
    #if os.path.exists('/usr/local/bluedon/tmp/synctbdata.sing'):
    #    deal_sync_table_data('/usr/local/bluedon/tmp/synctbdata.sing')
    #    os.remove('/usr/local/bluedon/tmp/synctbdata.sing')
    #if os.path.exists('/usr/local/bluedon/tmp/synccfdata.sing'):
     #   deal_sync_conf_data('/usr/local/bluedon/tmp/synccfdata.sing')
      #  os.remove('/usr/local/bluedon/tmp/synccfdata.sing')

    logger_init('main','/usr/local/bluedon/log/main.log','INFO')

    lockfile = os.path.join(SEND_FILE, 'lock_file')
    os.system('rm -rf {0}'.format(lockfile))
    run()
