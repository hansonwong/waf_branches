#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
import datetime
import threading
from config1 import execute_sql as exec_3307
from LogProcessor import LogType
from adutils.redis_utils.redis_op import create_redis, subscribe_channel, publish_channel
from adutils.redis_utils.redis_op import REDIS_CHN_OF_TB, REDIS_CHN_EXIT
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR


# load data infile
class LogProcessorNoDate(threading.Thread):
    def __init__(self, TYPE, LOAD):
        super(LogProcessorNoDate, self).__init__()
        logtype = LogType(TYPE)
        tb = logtype.tb_name
        self.event = threading.Event()
        self.bcp = logtype.bcp
        self.load_sql = LOAD
        self.tb = tb         # table name with date
        self.table_name = tb # origin table name
        # self.current_date = datetime.datetime.now().strftime('%Y%m%d')
        self.redis_chn = logtype.redis_ch
        self.redisdb = create_redis()
        self._current = ''
        ADLOG_DEBUG(self.table_name)

    def load_data_infile(self, log):
        # for log in logs:
        if not os.path.exists(log):
            # log here
            print '%s is not exists' % log
            ADLOG_ERR('%s is not exists' % log)
            return

        # load data infile
        exec_3307(self.load_sql.format(inf=log, tb=self.tb))
        # log here
        ADLOG_DEBUG('load %s done...' % log)
        os.system('rm -f %s' % log)
        ADLOG_DEBUG('rm %s done...' % log)

    def run(self):
        while 1:
            if self.event.isSet():
                #log here
                ADLOG_INFO('[LogProcessorNoDate][%s]even is set' % self.table_name)
                break

            try:
                with subscribe_channel(self.redisdb, self.redis_chn) as logs:
                    for log in logs:
                        # logs = self.search_logfiles()
                        # print log
                        if log['data'] == REDIS_CHN_EXIT:
                            ADLOG_INFO('[%s] GET %s' % (self.table_name, REDIS_CHN_EXIT))
                            raise RuntimeError('[%s] GET %s' % (self.table_name, REDIS_CHN_EXIT))
                        try:
                            # ADLOG_DEBUG(log)
                            self.load_data_infile(log['data'])
                            # ADLOG_DEBUG('load done')
                        except Exception as e:
                            ADLOG_DEBUG('load error %s' % e)
                            continue
                # time.sleep(1)
            except Exception as e:
                self.redisdb = create_redis()
                ADLOG_ERR('load error %s reconnect to redis' % e)
                time.sleep(1)




    def stop(self):
        self.event.set()
        publish_channel(self.redisdb, self.redis_chn, REDIS_CHN_EXIT)


class LogProcessTask(object):
    def __init__(self):
        super(LogProcessTask, self).__init__()

    def add_task(self):
        pass

    def log_scanner(self, path):
        pass

    def task_dispatcher(self):
        pass


if __name__ == '__main__':
    try:
        lp = LogProcessorNoDate()
        # print lp.search_logfiles()
        lp.setDaemon(True)
        lp.start()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        lp.stop()
        lp.join()

