#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
import datetime
import threading
from adutils.config1 import execute_sql as exec_3307
from adutils.redis_utils.redis_op import create_redis, subscribe_channel, publish_channel
from adutils.redis_utils.redis_op import REDIS_CHN_OF_TB, REDIS_CHN_EXIT
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR

LOG_PATH = '/tmp/audit_log/'
LOG_PATH_ERR = '/tmp/audit_log_fail/'

PATH_LOG = lambda x: os.path.join(LOG_PATH, x)
PATH_LOG_ERR = lambda x: os.path.join(LOG_PATH_ERR, x)
TBNAME = lambda x : 'm_tb_{}'.format(x)
TYPE_BCP = lambda x : '{}.bcp'.format(x)


REDIS_CHN_STOP_LOADING = 'REDIS_CHN_STOP_LOADING'
REDIS_CHN_RESUME_LOADING = 'REDIS_CHN_RESUME_LOADING'


class LogType(object):
    def __init__(self, typ):
         super(LogType, self).__init__()
         self.TYPE = typ
         self.bcp = TYPE_BCP(typ)
         self.redis_ch = REDIS_CHN_OF_TB(typ)
         self.tb_name = TBNAME(typ)


def set_loading(action, log_type=None):
    log_name = '*' if log_type is None else log_type
    ch_name = REDIS_CHN_OF_TB(log_name)
    if action.upper() == 'START': msg = REDIS_CHN_RESUME_LOADING
    else: msg = REDIS_CHN_STOP_LOADING

    # get all file channel
    r = create_redis()
    log_channels = r.execute_command("PUBSUB CHANNELS {}".format(ch_name))
    for ch in log_channels:
        publish_channel(r, ch, msg)


# load data infile
class LogProcessor(threading.Thread):
    def __init__(self, TYPE, LOAD):
        super(LogProcessor, self).__init__()
        logtype = LogType(TYPE)
        tb = logtype.tb_name
        self.event = threading.Event()
        self.bcp = logtype.bcp
        self.load_sql = LOAD
        self.tb = tb         # table name with date
        self.table_name = tb # origin table name
        self.cmd_search_log = ''
        # self.current_date = datetime.datetime.now().strftime('%Y%m%d')
        self.redis_chn = logtype.redis_ch
        self.redisdb = create_redis()
        self._current = ''
        self.setName(self.table_name)
        self.should_load = True
        ADLOG_DEBUG(self.table_name)

        # make directory for temp file is not exists
        if not os.path.exists(LOG_PATH):
            os.system('/usr/bin/mkdir -p {}'.format(LOG_PATH))

        if not os.path.exists(LOG_PATH_ERR):
            os.system('/usr/bin/mkdir -p {}'.format(LOG_PATH_ERR))

        os.system('/usr/bin/rm -f {}*'.format(PATH_LOG(self.bcp)))
        os.system('/usr/bin/rm -f {}*'.format(PATH_LOG_ERR(self.bcp)))


    @property
    def current_date(self):
        return self._current

    @current_date.setter
    def current_date(self, value):
        ADLOG_DEBUG('self.current_date = %s' % value)
        self._current = value
        self.create_table_by_date()


    def search_logfiles(self):
        try:
            logs = os.listdir(LOG_PATH)
        except OSError:
            # log here
            print 'OSError[search_logfiles]'
            ADLOG_ERR('OSError[search_logfiles]')
            return None

        logfiles = [ PATH_LOG(f) for f in logs if f.startswith(self.bcp) ]
        return logfiles or None

    def create_table_by_date(self):
        create_tb_sql = "CREATE TABLE IF NOT EXISTS `{new_tb}` LIKE {origin_tb}"
        self.tb = self.table_name + '_' + self.current_date
        try:
            exec_3307(create_tb_sql.format(new_tb=self.tb, origin_tb=self.table_name))
        except:
            print 'something wrong while creating table..[%s]' % n_tb
            ADLOG_ERR('something wrong while creating table..[%s]' % n_tb)


    def load_data_infile(self, log):
        # for log in logs:
        if not os.path.exists(log):
            # log here
            print '%s is not exists' % log
            ADLOG_ERR('%s is not exists' % log)
            return

        # st = time.time()
        # ADLOG_DEBUG('[%s] size=[%d], start processing...at %f' % (log, os.path.getsize(log), st))
        # split tables by timestamp
        log_ts = log.split('.')[-1]
        try:
            dt = datetime.datetime.fromtimestamp(int(log_ts))
            date = dt.strftime('%Y%m%d')
        except Exception as e:
            # log here
            print 'datetime: ',e
            ADLOG_ERR('load_data_infile datetime error: ',e)
            return

        if self.current_date != date:
            self.current_date = date
            # self.create_table_by_date()
        # load data infile
        ret = exec_3307(self.load_sql.format(inf=log, tb=self.tb))
        if ret is False:
            ADLOG_DEBUG('load %s FAILD...FAILD...FAILD' % log)
            log_file = os.path.split(log)[-1]
            os.system('mv {fr} {to}'.format(fr=log, to=PATH_LOG_ERR(log_file)))
        # log here
        else:
            ADLOG_DEBUG('load %s done...' % log)
            os.system('rm -f %s' % log)
            ADLOG_DEBUG('rm %s done...' % log)
        # et = time.time()
        # ADLOG_DEBUG('[%s]  process done...at %f' % (log, et))
        # print '[%s]  process time=%f' % (log, et - st)

    def run(self):
        while 1:
            if self.event.isSet():
                #log here
                ADLOG_INFO('[LogProcessor][%s]even is set' % self.table_name)
                break

            try:
                with subscribe_channel(self.redisdb, self.redis_chn) as logs:
                    for log in logs:
                        # logs = self.search_logfiles()
                        # print log
                        # Here we check the processing switch, it will be turned
                        # off while the DISK is FULL
                        if log['data'] == REDIS_CHN_EXIT:
                            ADLOG_INFO('[%s] GET %s' % (self.table_name, REDIS_CHN_EXIT))
                            raise RuntimeError('[%s] GET %s' % (self.table_name, REDIS_CHN_EXIT))
                        elif log['data'] == REDIS_CHN_STOP_LOADING:
                            self.should_load = False
                            ADLOG_INFO('[%s] GET %s' % (self.table_name, REDIS_CHN_STOP_LOADING))
                            continue
                        elif log['data'] == REDIS_CHN_RESUME_LOADING:
                            self.should_load = True
                            # ADLOG_INFO('[%s] GET %s' % (self.table_name, REDIS_CHN_RESUME_LOADING))
                            continue
                        try:
                            # ADLOG_DEBUG(log)
                            if self.should_load:
                                self.load_data_infile(log['data'])
                            # ADLOG_DEBUG('load done')
                        except Exception as e:
                            if log.get('type', None) == 'message':
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
        lp = LogProcessor()
        # print lp.search_logfiles()
        lp.setDaemon(True)
        lp.start()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        lp.stop()
        lp.join()

