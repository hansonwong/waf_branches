#!/usr/bin/env python
# coding=utf-8

"""
    Log statistics

"""

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import datetime
import json
import signal
from collections import namedtuple
from adutils.config1 import execute_sql as exec_3307
from adutils.config1 import fetchall_sql as fcal_3307
from LogProcessor import LogType, LogProcessor
from adutils.audit_utils import ERR_TEXT, TIP_TEXT
from adutils.redis_utils.redis_op import create_redis, publish_channel
from adutils.audit_logger import ADLOG_DEBUG, ADLOG_INFO, ADLOG_ERR

COUNTER_CHN = 'AUDIT_NEW_LOG_COUNTER'

LOG_TYPE = ('audit', 'alert', 'filter')

LOG_STATIS = namedtuple('LOG_STATIS', 'log_time, app_type, log_type, sip, user, \
                        dept, kw, ove dev_id')
LOG_KEYS = ['log_time', 'app_type', 'log_type', 'sip', 'user', 'dept', 'kw',
            'ove', 'dev_id']

LOG_COUNT_MIN = 180

# QUOTE = lambda x : '"' + str(x) + '"'
QUOTE = lambda x : str(x).decode('utf-8')
LOG_PATH = '/tmp/audit_log/'

# define logtype of statistics
statistics_log_type = 'statistics_audit'
statistics_log = LogType(statistics_log_type)


load_sql = """load data  infile "{inf}" into table `{tb}` character set utf8
              fields terminated by '\t' lines terminated by '\n'
              (`iTime`,`sAppType`,`sStatisticsType`,`sIP`,`sUsername` ,`sDept` ,
              `sKeyword` ,`iOverseas`, `sDeviceID`, `iCount`);"""


class StatisticsLogProcessor(LogProcessor):
    def __init__(self, _type, _load_sql):
        super(StatisticsLogProcessor, self).__init__(TYPE=_type, LOAD=_load_sql)
        self.summary_tbname = self.table_name + '_all'

        self.add_sub_tables()

    def create_summary_table(self):
        drop_sql = "DROP TABLE IF EXISTS %s"
        exec_3307(drop_sql % (self.summary_tbname))
        create_sql = "CREATE TABLE IF NOT EXISTS %s like %s"
        # create summary table
        exec_3307(create_sql % (self.summary_tbname, self.table_name))


    def get_sub_tables(self):
        _sub_tb = []
        sql = "SELECT TABLE_NAME FROM information_schema.`TABLES` WHERE TABLE_NAME LIKE 'm_tb_statistics_audit_2%';"
        for res in fcal_3307(sql):
            _tbname = res.get('TABLE_NAME', '')
            if _tbname.startswith(self.table_name):
                _sub_tb.append(_tbname)

        return _sub_tb


    def add_sub_tables(self):
        _sub_tb = self.get_sub_tables()
        if len(_sub_tb) == 0:
            # log here
            ADLOG_ERR('[add_sub_tables]no sub table exists')
            return

        self.create_summary_table()
        add_sql = "ALTER TABLE %s ENGINE=MERGE UNION=(%s) INSERT_METHOD=LAST"
        exec_3307(add_sql % (self.summary_tbname, ','.join(_sub_tb)))

        pass



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

            # add sub-table(self.tb) to summary table
            self.add_sub_tables()
            pass
            # self.create_table_by_date()
        # load data infile
        exec_3307(self.load_sql.format(inf=log, tb=self.tb))
        # log here
        ADLOG_DEBUG('[StatisticsLog]load %s done...' % log)
        os.system('rm -f %s' % log)
        ADLOG_DEBUG('[StatisticsLog]rm %s done...' % log)
        # et = time.time()
        # ADLOG_DEBUG('[%s]  process done...at %f' % (log, et))
        # print '[%s]  process time=%f' % (log, et - st)
        pass

StatisticsLog = StatisticsLogProcessor(statistics_log_type, load_sql)


class LogCount(object):
    def __init__(self, _log=None,):
        self.log = None
        self.log_type = None
        try:
            _nt = LOG_STATIS._make(_log)
        except Exception as e:
            ADLOG_ERR('LogCount init Error')

        self.log = {
            'log_time': _nt.log_time, 'app_type': _nt.app_type,
            'log_type': _nt.log_type, 'sip': _nt.sip,
            'user': _nt.user, 'dept': _nt.dept, 'ove': _nt.ove, 'kw': _nt.kw,
            'dev_id': _nt.dev_id
        }
        self.log_type = _nt.log_type
        pass

    def send_count(self):
        try:
            if not isinstance(self.log, dict):
                ADLOG_DEBUG('%s is not a dict' % self.log)
                return
            msg = json.dumps(self.log, encoding="UTF-8", ensure_ascii=False)
            send_to_counter(msg, self.log_type)
            # ADLOG_DEBUG('send msg %s' % msg)
        except Exception as e:
            ADLOG_ERR('[LogCount]error %s' % e)


_COUNTER_REDIS = create_redis()

def send_to_counter(msg=None, typ=None):
    if msg is None or typ is None:
        ADLOG_DEBUG('get null msg or typ')
        return

    publish_channel(_COUNTER_REDIS, COUNTER_CHN, msg)

    # re = create_redis()
    # publish_channel(re, COUNTER_CHN, msg)
    # re.connection_pool.disconnect()


# class LogStatistics(object):
#     def __init__(self):
#         super(LogStatistics, self).__init__()
#         self.email_log = {}



class LogCounter(object):
    def __init__(self):
        super(LogCounter, self).__init__()
        self.stopped = False
        self.timeout = False
        self.last_check = time.time()
        self.counter = {}
        self.i_time = None

        # add different log types

        # check if log path exists
        if not os.path.exists(LOG_PATH):
            os.system('mkdir -p %s' % LOG_PATH)

        # redis_obj
        self.redis_obj = create_redis()


    def timeout_checker(self):
        if time.time() - self.last_check >= 10:
            self.last_check = time.time()
            return True

        return False


    def timeout_handler(self):
        # if self.i_time is None:
        #     ADLOG_DEBUG('[LogCounter] self.i_time is None')
        #     return

        if len(self.counter) == 0:
            ADLOG_DEBUG('[LogCounter] self.counter length is 0')
            return

        # put all args into one record
        print 'timeout_handler'
        # print self.counter

        # write to file and notify redis there is a new file to import
        # file name of data
        # _log_filename = statistics_log.bcp + '.' + str(self.i_time)
        _log_filename = statistics_log.bcp + '.' + str(int(time.time()))
        _log_path = os.path.join(LOG_PATH, _log_filename)
        print TIP_TEXT('Write to file %s' % _log_path)
        with open(_log_path, 'wb') as fp:
            for _idx in self.counter:
                if self.stopped is True: break
                try:
                    if self.counter[_idx] == 0: continue
                    _l = [ QUOTE(it) for it in _idx]
                    _values = '\t'.join(_l) + '\t' + QUOTE(self.counter[_idx])
                    fp.write('%s\n' % _values)
                except Exception as e:
                    print e
                    pass
            fp.flush()

        self.counter = {}
        # notify redis
        if os.path.exists(_log_path):
            print TIP_TEXT('Send msg to %s' % statistics_log.redis_ch)
            # re = create_redis()
            # publish_channel(re, statistics_log.redis_ch, _log_path)
            # re.connection_pool.disconnect()
            publish_channel(self.redis_obj, statistics_log.redis_ch, _log_path)


    def sighandler(self, v1, v2):
        ADLOG_DEBUG('LogCounter sighandler get TERM signal')
        self.stopped = True


    def start_counter(self):
        try:
            signal.signal(signal.SIGTERM, self.sighandler)
            re = create_redis()
            re.ping()
            ps = re.pubsub()
            ps.subscribe(COUNTER_CHN)
            ADLOG_DEBUG(TIP_TEXT("[LogCounter] connected to redis"))
        except:
            # log here
            ADLOG_ERR("[LogCounter] Can't not connect to redis")
            return

        msg_count = 0
        null_msg_count = 0

        while 1:
            try:
                msg = ps.get_message()
                if self.stopped:
                    break

                if not msg:
                    null_msg_count += 1
                    # wait time
                    time.sleep(1)

                else:
                    if msg['type'] == 'message':
                        dmsg = json.loads(msg['data'])

                        msg_count += 1
                        # # initial self.i_time if self.i_time is None
                        # i_time = dmsg.get('log_time', None)
                        # if self.i_time is None:
                        #     self.i_time = i_time
                        # # log statistics
                        # if self.i_time != i_time:
                        #     self.timeout_handler()
                        #     # print TIP_TEXT('Timeout commit')
                        #     self.i_time = i_time

                        # timeout condition
                        if msg_count >= 5000 or null_msg_count > 10:
                            self.timeout_handler()
                            msg_count = 0
                            null_msg_count = 0

                        _idx = [ dmsg[k] for k in LOG_KEYS]
                        _idx = tuple(_idx)
                        # 'log_time, app_type, log_type, sip, user, dept, kw')
                        if _idx not in self.counter:
                            self.counter[_idx] = 1
                        else:
                            self.counter[_idx] += 1
            except (KeyboardInterrupt, RuntimeError) as e:
                ADLOG_INFO("[LogCounter] Exit %s" % e)
                break
            except Exception as e:
                ADLOG_ERR("[LogCounter] Error...%s\nget message redis again..." % e)
                continue

        ADLOG_INFO('Exit LogCounter...')



    def stop_counter(self):
        self.stopped = True
        pass
