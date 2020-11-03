#!/usr/bin/env python
# -*- coding: utf-8 -*-

import stat
import os
import time
import threading
import pickle
import MySQLdb
import MySQLdb.cursors
import datetime
import random
import requests
import Queue
import urlparse
import socket
from config import config
from logging import getLogger
from db import conn_scope, session_scope, SiteStatus, rows2list
from config_sql import execute_sql, fetchall_sql, fetchone_sql, execute_sql_logs


queue = Queue.Queue()


class SiteChecker(threading.Thread):

    ''' 网站状态检测 '''
    
    event = threading.Event()

    def __init__(self, ):
        super(SiteChecker, self).__init__(name=self.__class__.__name__)
    
    def start(self):
        from db import conn_scope, session_scope, SiteStatus, rows2list
        with session_scope() as session:
            sites = rows2list(session.query(SiteStatus).all())
            # print sites
            try:
                for site in sites:
                    # print site
                    site["type"] = 0
                    with session_scope() as session1:
                        session1.query(SiteStatus).filter(SiteStatus.id == site['id']).\
                            update({SiteStatus.type: site["type"]})
            except:
                pass
                # print "OK"

        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(SiteChecker, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')

    def proc(self):
        from db import conn_scope, session_scope, SiteStatus, rows2list
        from sqlalchemy import and_
        with session_scope() as session:
            sites = rows2list(session.query(SiteStatus).filter(and_(
                SiteStatus.status == 1, SiteStatus.type == 0)).all())
            if not sites:
                # print "fuck!"
                return

        for site in sites:
            # print site["type"]
            if self.event.isSet():
                return
            site["type"] = 1
            with session_scope() as session:
                session.query(SiteStatus).filter(SiteStatus.id == site['id']). \
                    update({SiteStatus.type: site["type"]})
            thread_update = threading.Thread(target=update_sql, args=(site,))
            thread_update.start()
            # # from db import conn_scope, session_scope, SiteStatus, rows2list
            # site["type"] = 1
            # with session_scope() as session:
            #     session.query(SiteStatus).filter(SiteStatus.id == site['id']). \
            #         update({SiteStatus.type: site["type"]})
            # print id(thread_update)
        delete_table()
            
    def run(self):
        while 1:
            try:
                # for _ in range(60):
                #     if self.event.isSet():
                #         return
                #     time.sleep(1)
                if self.event.isSet():
                    return
                self.proc()
                try:
                    execute_sql(queue.get())
                except:
                    pass
            except Exception, e:
                getLogger('main').exception(e)


def update_sql(data):
    global queue
    # print "OK"
    # from db import conn_scope, session_scope, SiteStatus, rows2list
    # data["type"] = 1
    # with session_scope() as session:
    #     session.query(SiteStatus).filter(SiteStatus.id == data['id']).\
    #         update({SiteStatus.type: data["type"]})

    # data['time'] = int(time.mktime(time.localtime()))

    data["protype"] = data["url"].split(":")[0]
    if data["rate"]:
        sleep_time = int(data["rate"])*60
    else:
        sleep_time = random.randint(1, 4)*20
    # print "start", data["url"]
    time.sleep(sleep_time)
    # time.sleep(20)
    data['time'] = int(time.mktime(time.localtime()))
    # print "starting...", data["url"]

    # iptables暂时允许检测的ip通过
    ip_set = set()
    try:
        netloc = urlparse.urlparse(data['url']).netloc.split(':')[0]
        for result in socket.getaddrinfo(netloc, None, socket.AF_INET):
            ip_set.add(result[4][0])
    except Exception, e:
        pass
        # getLogger('main').info(netloc)
        # getLogger('main').error(e)
    for siteip in ip_set:
        os.system('ipset add sitecheck {siteip}'.format(siteip=siteip))

    try:
        result = requests.get(data['url'], timeout=3, verify=False)
        data["responsetime"] = result.elapsed.microseconds/1000000.0
    except Exception, e:
        data['result'] = 0
        data['desc'] = e.message
        data["responsetime"] = 0
    else:
        if result.status_code == 200:
            data['result'] = 1
        else:
            data['result'] = 0
        data['desc'] = result.status_code

    finally:
        for siteip in ip_set:
            os.system('ipset del sitecheck {siteip}'.format(siteip=siteip))

        ntime = datetime.datetime.now()
        ntime = ntime.strftime("%Y%m%d %H:%M:%S").split()[0]
        table_name = "t_sitestatus" + "_" + "%s" % ntime
        sql = create_table(table_name)
        execute_sql_logs(sql)
        data["type"] = 0
        insert_sql = "insert into " + table_name + "(url,`time`,`status`,result,`desc`,protype,responsetime,`type`)" + """ values('%s','%s','%s','%s',"%s",'%s','%s','%s')"""
        insert_sql_cmd = insert_sql % (data['url'], data['time'],
                                       data['status'], data['result'],
                                       data['desc'], data["protype"],
                                       data["responsetime"], data["type"])
        # print insert_sql_cmd
        execute_sql_logs(insert_sql_cmd)
        # print "excute sql"
        up_sql = 'update t_sitestatus set `time`="%s",result="%s", `desc`="%s", protype="%s", type="%s", responsetime="%s" where id=%s' % \
                     (data["time"], data["result"], data["desc"],
                      data["protype"],
                      data["type"], data["responsetime"], data["id"])
        queue.put(up_sql)

        # with session_scope() as session:
        #     session.query(SiteStatus).filter(SiteStatus.id == data['id']).\
        #         update({SiteStatus.type: data["type"],
        #                 SiteStatus.time: data["time"],
        #                 SiteStatus.result: data["result"],
        #                 SiteStatus.desc: data["desc"],
        #                 SiteStatus.protype: data["protype"],
        #                 SiteStatus.responsetime: data["responsetime"]})


def create_table(table_name):
    # 每天创建一个新表
    sql = """CREATE TABLE IF NOT EXISTS `%s` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `status` tinyint(4) DEFAULT '0' COMMENT '0:disable 1:enable',
  `result` tinyint(4) DEFAULT '0' COMMENT '0:unnormal 1:normal',
  `desc` varchar(512) COLLATE utf8_unicode_ci DEFAULT '',
  `protype` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `freq` int(11) DEFAULT NULL,
  `responsetime` float(11) DEFAULT NULL,
  `type` tinyint(4) DEFAULT '0',
  `rate` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;""" % table_name

    return sql


def delete_table():
    # 删除30天前的数据表
    table = "t_sitestatus_"
    thirty_day_ago = (datetime.datetime.now() - datetime.timedelta(days=30))
    table_time = thirty_day_ago.strftime("%Y%m%d %H:%M:%S").split()[0]
    table_name = table + table_time
    delete_sql = "DROP TABLE %s" % table_name
    execute_sql_logs(delete_sql)


def checkSite():
    from docopt import docopt
    import json
    try:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    except:
        pass
    try:
        from requests.packages.urllib3.exceptions import SNIMissingWarning
        requests.packages.urllib3.disable_warnings(SNIMissingWarning)
    except:
        pass
    try:
        from requests.packages.urllib3.exceptions import InsecurePlatformWarning
        requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
    except:
        pass
    doc = """ Bluedon Site Usability Check

Usage:
  SiteChecker.py -site [URL]

Arguments:
   URL check url

Options:
  -h --help                  show this help message and exit
  -v --version               show version and exit
  -site URL                  set the check url
"""

    args = docopt(doc, version='1.0.0')
    url = args['URL']
    SiteStatus = {"result" : 0}
    statusCode = [200, 302, 301]
    try:
        result = requests.head(url, timeout=4, verify=False)
        if result.status_code in statusCode: SiteStatus["result"] = 1
        SiteStatus["desc"] = result.status_code
    except Exception, e:
            SiteStatus['desc'] = "%s"%(e.message)
    SiteStatusData = json.dumps(SiteStatus)        
    # print SiteStatusData
    return SiteStatusData

                
if __name__ == '__main__':
    #a = SiteChecker()
    #a.start()
    checkSite()
    # from db import conn_scope, session_scope, SiteStatus, rows2list
    # from sqlalchemy import and_
    #
    # with session_scope() as session:
    #     sites = rows2list(session.query(SiteStatus).filter(and_(
    #         SiteStatus.status == 1, SiteStatus.type == 0)).all())
    #     if not sites:
    #         print "III"
    #
    # for site in sites:
    #     print site

