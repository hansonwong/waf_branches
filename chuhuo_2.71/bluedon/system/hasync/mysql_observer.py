#!/usr/bin/env python
# coding=utf-8

import os
import time
import threading
import datetime
import json

from db.config import fetchone_sql as fetch_3306
from db.config import fetchall_sql as fcal_3306
from system.hasync.sync_send import dump_table_data, dump_file_data
from system.hasync.sync_config import cf, logger
from db.mysql_db import select_one


TABLES = cf.sections()
TABLES.remove('files')

class MysqlUpdateObserver(threading.Thread):
    def __init__(self,ip):
        super(MysqlUpdateObserver, self).__init__()
        self.event = threading.Event()
        self.ip = ip

    def run(self):

        update_record = {}
        query_sql = ('SELECT TABLE_NAME,UPDATE_TIME FROM information_schema.`TABLES` '
                    'WHERE TABLE_NAME IN %s') % str(tuple(TABLES))

        def judge_tables_change(itype=0):
            """
            监控表的修改时间
            args:
                itype: 0: 初始化表的时间; 1: 定时扫描表的修改时间
            """

            tables_set = set()    # 记录变化的表

            for res in fcal_3306(query_sql):
                tb = res['TABLE_NAME']
                if not isinstance(res, dict):
                    logger.info('[MYSQL_UPDATE_OBSERVER]%s is not available...' % tb)
                    continue
                else:
                    if isinstance(res['UPDATE_TIME'], datetime.datetime):
                        if itype == 0:
                            update_record[tb] = res['UPDATE_TIME']
                        elif itype == 1:
                            if res['UPDATE_TIME'] > update_record[tb]:
                                update_record[tb] = res['UPDATE_TIME']
                                tables_set.add(tb)
                                if dict(cf.items(tb)).get('relation_tb'):
                                    relation_tables = set(json.loads(dict(cf.items(tb)).get('relation_tb')))
                                    tables_set = tables_set | relation_tables
                    else:
                        if itype == 0:
                            update_record[tb] = datetime.datetime.now()
            if itype == 1:
                return tables_set
        #初始化字典update_record,记录表格当前修改时间,键值为表名,value值为时间
        judge_tables_change(0)

        #进入监控表格是否被修改
        while 1:
            time.sleep(5)
            if self.event.isSet():
                logger.info('EVENT SET:[MYSQL_UPDATE_OBSERVER]')
                break

            tables_set = judge_tables_change(1)
            #print tables_set
            if tables_set:
                dump_table_data(tables_set)
                os.system('/usr/bin/rsync -vzrtopg --delete --progress --password-file=/usr/local/rsync/server.passwd /home/rsync/send/ webuser@%s::web'%self.ip)

        logger.info('QUIT:[MYSQL_UPDATE_OBSERVER]')


    def start(self):
        super(MysqlUpdateObserver, self).start()

    def stop(self):
        self.event.set()
        self.join()


if __name__ == '__main__':
    """
    启动配置同步时,先将所有表发到备机,以保证主备环境开始时是一致的,TABLES包含所有需要同步的表
    停止5秒,意在给备机时间同步TABLES里的表,以避免表被覆盖
    """
    os.system('rm -f /home/rsync/send/*')
    ha_info = select_one('select sValue from m_tbconfig where sName="HaSetting"')
    ip = json.loads(ha_info['sValue']).get('sClientIP')
    dump_table_data(TABLES)
    os.system('/usr/bin/rsync -vzrtopg --delete --progress --password-file=/usr/local/rsync/server.passwd /home/rsync/send/ webuser@%s::web'%ip)
    time.sleep(5)
    mysqlup = MysqlUpdateObserver(ip)
    mysqlup.start()
    if os.path.exists('/usr/local/bluedon/conf/online_users'):
        dump_file_data('files')
    # do master init
    for section in TABLES:
        try:
            if 'master_init' in cf.options(section):
                ret = cf.get(section, 'master_init')
                master_init_cmds = json.loads(ret)
                for cmd in master_init_cmds:
                    print cmd
                    os.system(cmd)
        except Exception as e:
            print e
            print 'no master init in section[%s]' % section
