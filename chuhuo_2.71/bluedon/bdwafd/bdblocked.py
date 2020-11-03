#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import threading
import MySQLdb
from logging import getLogger
from config import config
from db import conn_scope,get_config


class seniorblock(threading.Thread):
    event = threading.Event()

    def __init__(self, ):
        super(seniorblock, self).__init__(name=self.__class__.__name__)

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(seniorblock, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def proc(self):
        pass

    def run(self):

        while(1):
            try:
                st = 0
                while st < 300:
                    # getLogger('audit').info('testtesttest......................')
                    if self.event.isSet():
                        return
                    time.sleep(1)
                    st = st + 1
                addrs = {}
                # getLogger("audit").info('fuck000!!!!!!!!!!!!!!!!!!!!!!!!!')
                with conn_scope(**config['db']) as (conn, cursor):
                    # getLogger("audit").info('fuck111!!!!!!!!!!!!!!!!!!!!!!!!!')
                    # selsql = 'select is_autodefence, autodefence_cycle, autodefence_count, autodefence_second from t_securityset'
                    autodefence = get_config("SmartBlock")
                    # getLogger("audit").info('this is a test')
                    # getLogger("audit").info(type(results))
                    fence_time = int(autodefence["standardBlockTime"])

                    if not autodefence["enable"]:
                        continue
                    # get the start date and time
                    timeStamp = time.time() - (autodefence["cycle"] if autodefence["cycle"] != "" else 0)
                    timeArray = time.localtime(timeStamp)
                    otherStyleTime = time.strftime(
                        "%Y-%m-%d %H:%M:%S", timeArray)
                    otherStyleTime_new = int(time.mktime(
                        time.strptime(otherStyleTime, '%Y-%m-%d %H:%M:%S')))
                    buff = otherStyleTime.split(" ")
                    tdate = buff[0][0:4] + buff[0][5:7]

                    selsql = "select SourceIP, Host, id from logs.t_alertlogs where LogDateTime >= '%s'" % otherStyleTime
                    cursor = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
                    cursor.execute(selsql)
                    datas = cursor.fetchall()
                    for data in datas:
                        if data['SourceIP'] in addrs:
                            addrs[data['SourceIP']].append(data)
                        else:
                            addrs[data['SourceIP']] = [data]

                    # blocking the soureip?
                    for source_ip, data in addrs.items():
                        getLogger('audit').info("get %d times of %s" %(len(data), source_ip))
                        if len(data) >= autodefence["invadeCount"]:
                            try:
                                # insert first data
                                log_sql = '''insert into logs.t_bdblockedlogs (id, logtime, srcip, host, bdtime) 
                                             values(%s, %s, %s, %s, %s)'''
                                cursor.execute(log_sql, (data[0]['id'], otherStyleTime_new, 
                                                data[0]['SourceIP'], data[0]['Host'], fence_time))
                                getLogger('audit').info("%s:%s" % (source_ip, data[0]['Host']))
                            except Exception, e:
                                getLogger("audit").exception(e)

                            cmdstr = 'ipset add backlist %s timeout %s' % (source_ip, str(autodefence["standardBlockTime"]))
                            os.system(cmdstr)
                            getLogger('audit').info(cmdstr)
            except Exception, e:
                getLogger('audit').exception(e)

if __name__ == '__main__':
    import threading
    aa = seniorblock()
    aa.start()