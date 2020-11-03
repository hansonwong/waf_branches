#!/usr/bin/env python
# coding=utf-8

import time
import threading
import datetime
from logging import getLogger
from db.config import fetchone_sql as fetch_3306
from db.config import fetchall_sql as fcal_3306
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR

class MysqlObserver(object):
    FWLOG_DEBUG('in MysqlObserver')
    ob = {}
    ob_count = 0
    def __init__(self):
        super(MysqlObserver, self).__init__()

    @classmethod
    def add_ob_count(cls):
        cls.ob_count += 1
        if cls.ob_count > 255:
            raise RuntimeError('Too Much observers...')

    @classmethod
    def add_observer(cls, key, observer):

        if not cls.ob.has_key(key):
            cls.ob[key] = [observer]
        else:
            cls.ob[key].append(observer)
        # cls.ob[key] = observer
        cls.add_ob_count()
        cls.notify_observer(key, 'adding ob[%s] key=%s' % (cls.ob_count, key))


    @classmethod
    def notify_observer(cls, key, *args, **kwargs):
        if key in cls.ob:
            # cls.ob[key].onUpdate(*args, **kwargs)
            for fun in cls.ob[key]:

                fun(*args, **kwargs)

            # cls.ob[key](*args, **kwargs)
        else:
            raise RuntimeError('Observer didn\'t have this observer[%s]' % key)



class MysqlUpdateObserver(threading.Thread):
    def __init__(self):
        super(MysqlUpdateObserver, self).__init__()
        self.event = threading.Event()
        self.setName('mysql_ob')

    def run(self):
        task_num = MysqlObserver.ob_count
        if not task_num > 0:
            FWLOG_ERR('[MYSQL_UPDATE_OBSERVER]no task is waiting for watch')
            #return

        # query_sql = ('SELECT UPDATE_TIME FROM information_schema.`TABLES` '
        #              'WHERE TABLE_NAME="%s";')
        update_record = {}

        # query_sql = ('SELECT TABLE_NAME,UPDATE_TIME FROM information_schema.`TABLES` '
        #              'WHERE TABLE_NAME="')

        # query_sql = query_sql + '" or TABLE_NAME="'.join(MysqlObserver.ob.keys()) + '";'

        query_sql = ('SELECT TABLE_NAME,UPDATE_TIME FROM information_schema.`TABLES` '
                     'WHERE TABLE_NAME IN %s') % str(tuple(MysqlObserver.ob))

        for res in fcal_3306(query_sql):
            tb = res['TABLE_NAME']
            if not isinstance(res, dict):
                FWLOG_ERR('[MYSQL_UPDATE_OBSERVER]%s is not available...' % tb)
                continue
            else:
                if isinstance(res['UPDATE_TIME'], datetime.datetime):
                    update_record[tb] = res['UPDATE_TIME']
                else:
                    update_record[tb] = datetime.datetime.now()

        # init tb update_time record
        # update_record = {}
        # for tb in MysqlObserver.ob:
        #     res = fetch_3306(query_sql % tb)
        #     if not isinstance(res, dict):
        #         print '[MYSQL_UPDATE_OBSERVER]%s is not available...' % tb
        #         continue
        #     else:
        #         if isinstance(res['UPDATE_TIME'], datetime.datetime):
        #             update_record[tb] = res['UPDATE_TIME']
        #         else:
        #             update_record[tb] = datetime.datetime.now()


        while 1:
            if self.event.isSet():
                FWLOG_DEBUG('EVENT SET:[MYSQL_UPDATE_OBSERVER]')
                getLogger('log_daemon').debug('EVENT SET:[MYSQL_UPDATE_OBSERVER]')
                break
            # query_sql = ('SELECT TABLE_NAME,UPDATE_TIME FROM information_schema.`TABLES` '
            #              'WHERE TABLE_NAME="')

            # query_sql = query_sql + '" or TABLE_NAME="'.join(MysqlObserver.ob.keys()) + '";'
            query_sql = ('SELECT TABLE_NAME,UPDATE_TIME FROM information_schema.`TABLES` '
                         'WHERE TABLE_NAME IN %s') % str(tuple(MysqlObserver.ob))

            for res in fcal_3306(query_sql):
                tb = res['TABLE_NAME']
                if not isinstance(res, dict):
                    FWLOG_ERR('[MYSQL_UPDATE_OBSERVER]%s is not available...' % tb)
                    continue

                if isinstance(res['UPDATE_TIME'], datetime.datetime):
                    if res['UPDATE_TIME'] > update_record[tb]:
                        # print '%s update at %s' % (tb, res['UPDATE_TIME'])
                        update_record[tb] = res['UPDATE_TIME']
                        FWLOG_DEBUG('tb %s' % tb)
                        # MysqlObserver.ob[tb](tb)
                        try:
                            MysqlObserver.notify_observer(tb,tb)
                        except:
                            FWLOG_ERR('MysqlObserver :run function error[%s]' % tb)

            # for tb in MysqlObserver.ob:
            #     res = fetch_3306(query_sql % tb)
            #     if not isinstance(res, dict):
            #         print '[MYSQL_UPDATE_OBSERVER]%s is not available...' % tb
            #         continue

            #     if isinstance(res['UPDATE_TIME'], datetime.datetime):
            #         if res['UPDATE_TIME'] > update_record[tb]:
            #             print '%s update at %s' % (tb, res['UPDATE_TIME'])
            #             update_record[tb] = res['UPDATE_TIME']
            #             MysqlObserver.ob[tb]()

            time.sleep(1)
        FWLOG_DEBUG('QUIT:[MYSQL_UPDATE_OBSERVER]')
        getLogger('log_daemon').debug('QUIT:[MYSQL_UPDATE_OBSERVER]')


    def start(self):
        super(MysqlUpdateObserver, self).start()

    def stop(self):
        self.event.set()
        self.join()


class MysqlOb(object):
    def __init__(self, fn, msg='new ob'):
        super(MysqlOb, self).__init__()
        self.msg = msg
        self.fn = fn
        print self.msg + ':' + str(id(self))


    def onUpdate(self, *args, **kwargs):
        print 'update:'
        self.fn(*args, **kwargs)


    def onAdd(self):
        pass

