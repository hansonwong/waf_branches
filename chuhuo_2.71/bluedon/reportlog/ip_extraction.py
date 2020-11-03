#!/usr/bin/env python
import time
import gc
import os
import shelve
import threading
from reportlog.mysql_log_backup import mysql_table_exists as table_exists
from db.config1 import fetchall_sql as fcall_3307
from db.config import fetchall_sql as fcall_3306
from utils.log_logger import rLog_dbg, rLog_err
#today = time.strftime('%Y%m%d',time.localtime())
_day ='19700101'
today ='20100610'
tb = 'm_tblog_webapplication'
scan_list = [('m_tblog_ips',           'invasion_protect.txt'),
             ('m_tblog_webapplication','web_attract.txt'),
             ('m_tblog_ddos',          'ddos.txt'),
             ('m_tblog_evil_code',     'virus_protect.txt'),
             ('m_tblog_info_leak',     'info_leakage.txt'),]

scan_list_nodate = [
             ('m_tbauto_strategy_exception',     'monitor.txt'),
             ('m_tbhoneypot_log',      'dionaea.txt'),
             ('m_tbprotected_log',     'scan.txt'),  ]

scan_record_init = {'m_tblog_ips':            0,
                    'm_tblog_webapplication': 0,
                    'm_tblog_ddos':           0,
                    'm_tblog_evil_code':      0,
                    'm_tblog_info_leak':      0,
                    'm_tbhoneypot_log':       0,
                    'm_tbprotected_log':      0,
                    'm_tbauto_strategy_exception': 0} # in 3306

RES_PATH = r'/etc/antidetect/src_file/'
IP_EXTRA_SHELVE = '/usr/local/bluedon/conf/ip_extra.shelve'

#define logger
FWLOG_DBG = lambda x : rLog_dbg('ip_extraction', x)
FWLOG_ERR = lambda x : rLog_err('ip_extraction', x)

def ip_extraction(log,date,target):
    _scan_list = [ item[0] for item in scan_list ]
    # FWLOG_DBG(_scan_list)
    if log in _scan_list:
        tb = log + '_' + date
    else: tb = log
    # FWLOG_DBG('processing %s to %s' % (tb,target))
    current = current_result(tb)
    pre = previous_result(target)
    new_res = current - pre
    # FWLOG_DBG('new_res')
    # FWLOG_DBG(new_res)
    # FWLOG_DBG('pre')
    # FWLOG_DBG(pre)
    # FWLOG_DBG('current')
    # FWLOG_DBG(current)
    with open(target,'a+') as fp:
        for res in new_res:
            fp.write(res+'\n')
    del pre
    del current
    del new_res

def current_result(tb):
    _scan_list = [ item[0] for item in scan_list ]
    # global scan_record
    scan_record = shelve.open(IP_EXTRA_SHELVE)
    s = set()
    # index = 0 for test
    tb_type = tb[0:-9]
    if tb_type not in _scan_list: tb_type = tb
    # index = 0
    # index = int(time.time())
    # if current time is newest timestamp, save it
    # scan_record is max(current_timestamp,newest_tb_timestamp)

    # if scan_record[tb_type] == 0:
    #     scan_record[tb_type] =int(time.time())

    if table_exists(tb) or tb in ['m_tbauto_strategy_exception']:
        # FWLOG_DBG('processing %s' % tb)
        # sql = 'SELECT DISTINCT id,sSourceIP FROM %s WHERE id>%s LIMIT 5000;' % (tb,scan_record[tb[0:-9]])
        if tb.startswith('m_tbprotected_log') or tb.startswith('m_tbhoneypot_log'):
            sql = ('SELECT DISTINCT iTime,sSourceAddr FROM %s '
                   'WHERE iTime>%s GROUP BY sSourceAddr LIMIT 5000;') % (tb,scan_record[tb_type])
        elif tb.startswith('m_tbauto_strategy_exception'):
            sql = ('SELECT DISTINCT unix_timestamp(iLifeTime) AS iTime, sSourceIP FROM %s '
                   'WHERE unix_timestamp(iLifeTime)>%s GROUP BY sSourceIP LIMIT 5000;') % (tb,scan_record[tb_type])
        else:
            sql = ('SELECT DISTINCT iTime,sSourceIP FROM %s '
                   'WHERE iTime>%s GROUP BY sSourceIP LIMIT 5000;') % (tb,scan_record[tb_type])
        #sql = 'SELECT DISTINCT id,sSourceIP FROM %s' % tb
        # FWLOG_DBG(sql)
        # print sql
        if tb.startswith('m_tbauto_strategy_exception'): fetch_sql = fcall_3306
        else: fetch_sql = fcall_3307
        for res in fetch_sql(sql):
        # for res in result:
            try:
                s.add(str(res['sSourceIP']))
            except:
                s.add(str(res['sSourceAddr']))

            # global scan_record
            # always keep the newest timestamp
            if res['iTime'] > scan_record[tb_type]:
                scan_record[tb_type] = res['iTime']
    else:
        #print '[%s] not exists' % tb
        FWLOG_ERR('[%s] not exists' % tb)

    # global scan_record
    # print tb[0:-9],scan_record[tb_type]
    scan_record.close()
    return s

def previous_result(txt):
    s = set()
    try:
        with open(txt,'r') as fp:
            for l in fp:
                s.add(l.strip('\n'))
        return s
    except:
        return set()

def ip_extra(start_time = 0):
    global _day
    t = time.localtime()
    today = time.strftime('%Y%m%d',t)
    # FWLOG_DBG(_day + ' ip_extra running... ')
    db = shelve.open(IP_EXTRA_SHELVE)
    for k in scan_record_init:
        if k not in db: db[k] = 0
    db.close()

    if not _day == today:
        _day = today
        tmp = [os.system('rm -f %s' % RES_PATH+f[1]) for f in scan_list]
        del tmp
        # process log not endswith date
        tmp = [os.system('rm -f %s' % RES_PATH+f[1]) for f in scan_list_nodate]
        del tmp

    tmp = [ip_extraction(tb,today,RES_PATH+fl) for (tb,fl) in scan_list]
    del tmp
    tmp = [ip_extraction(tb,today,RES_PATH+fl) for (tb,fl) in scan_list_nodate]
    del tmp


class IPExtraction(threading.Thread):
    def __init__(self):
        super(IPExtraction, self).__init__()
        self.event = threading.Event()
        self.setName('ip_extra')

    def run(self):
        while 1:
            if self.event.isSet():
                FWLOG_DBG('[ip_extraction] EVENT SET')
                break

            try:
                ip_extra()
            except Exception as e:
                FWLOG_ERR('[ip_extraction] error %s' % e)
            time.sleep(10)

        FWLOG_DBG('[ip_extraction] run exit')

    def start(self):
        super(IPExtraction, self).start()

    def stop(self):
        self.event.set()
        FWLOG_DBG('[ip_extraction] stopped')

class IPExtractionController(object):

    # _monitor = TrafficStatistic()
    _monitor = None

    @classmethod
    def get_monitor(cls):
        return cls._monitor

    @classmethod
    def start_monitor(cls):
        FWLOG_DBG('start ip_extraction')
        if cls._monitor is None:
            cls._monitor = IPExtraction()
            cls._monitor.start()
        else:
            FWLOG_DBG('ip_extraction has already started')
        FWLOG_DBG('start ip_extraction done')

    @classmethod
    def stop_monitor(cls):
        FWLOG_DBG('stop ip_extraction')
        if cls._monitor is not None:
            cls._monitor.stop()
            FWLOG_DBG('close monitor')

        cls._monitor = None
        FWLOG_DBG('stop ip_extraction done')
    pass

if __name__ == '__main__':
    #ip_extraction(tb,today)
    #ip_extraction(scan_list[1][0],today,RES_PATH+scan_list[1][1])
    #s = previous_result(RES_PATH+scan_list[1][1])
    #print s
    #[ip_extraction(tb,today,RES_PATH+fl) for (tb,fl) in scan_list]
    # while 1:
    #     ip_extra()
    #     gc.collect()
    #     time.sleep(1)
    try:
        IPExtractionController.start_monitor()
        while 1:
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        IPExtractionController.stop_monitor()
    pass

