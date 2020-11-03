#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import os
import sys
import logging
import MySQLdb
import ConfigParser
from lib.common import *
from lib.waf_netutil import *


from nvscan_xmlrpc import *
import time
from random import randint


WAF_CONFIG   = "/var/waf/waf.conf"

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
HOST   = cfg.get("mysql","db_ip").replace('"','')
USER   = cfg.get("mysql","db_user").replace('"','')
PASSWD = cfg.get("mysql","db_passwd").replace('"','')

db = None

class db_manager:
    """docstring for db_manager"""
    def __init__(self):
        try:
            self._connect()
        except Exception, e:
            ERROR("db_manager.__init__:"+str(e))

    def __del__(self):
        try:
            self.conn.close()
        except Exception, e:
            ERROR("db_manager.__del__:"+str(e))

    def _connect(self):
        try:
            self.conn = MySQLdb.connect(HOST, USER, PASSWD, db='waf_hw', charset='utf8')
            self.cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
        except Exception, e:
            ERROR("db_manager._connect:"+str(e))

    def _check_connect(self):
        try:
            self.conn.ping()
        except Exception, e:
            ERROR("db_manager._check_connect:"+str(e) + "--will reconnect.")
            self._connect()

    def _execute(self,sql, args=None):
        try:
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)
            self.conn.commit()
        except Exception, e:
            self._check_connect()
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)
            self.conn.commit()

    def get_one_item_from_db(self, sql):
        try:
            if not sql:
                return None
            self._execute(sql)
            return self.cur.fetchone()
        except Exception, e:
            ERROR("db_manager.get_one_item_from_db:"+str(e)+'##'+str(self.conn)+str(self.cur))
            return -1

    def get_all_item_from_db(self, sql):
        try:
            if not sql:
                return None
            self._execute(sql)
            return self.cur.fetchall()
        except Exception, e:
            ERROR("db_manager.get_all_item_from_db:"+str(e))

    def get_one_item_from_db_by_args(self, sql, args):
        try:
            self._execute(sql, args)
            return self.cur.fetchone()
        except Exception, e:
            ERROR("db_manager.get_one_item_from_db_by_args:"+str(e))

    def set_item_to_db(self, sql):
        try:
            DEBUG('set_item_to_db:' + sql)
            self._execute(sql)
        except Exception, e:
            ERROR("db_manager.set_item_to_db:"+str(e))

    def safe_execute(self,sql, args=None):
        try:
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)
        except Exception, e:
            self._check_connect()
            if not args:
                self.cur.execute(sql)
            else:
                self.cur.execute(sql, args)

    def set_item_to_db_safe(self, sql):
        try:
            self.safe_execute(sql)
        except Exception, e:
            ERROR("db_manager.set_item_to_db_safe:"+str(e))

    def commit_trans(self):
        try:
            self.conn.commit()
        except Exception, e:
            ERROR("db_manager.commit_trans:"+str(e))

    def set_item_to_db_by_args(self, sql, args):
        try:
            self._execute(sql, args)
        except Exception, e:
            ERROR("db_manager.set_item_to_db_by_args:"+str(e))

class nvscan_clear(object):
    """docstring for nvscan_manager"""
    def __init__(self, task_id):
        try:
            self.scanner = nvscan_xmlrpc()
            self.task_id = task_id
            self.scan_uuid = ''

        except Exception, e:
            ERROR("nvscan_clear.__init__:"+str(e))


    def scan_stop(self):
        DEBUG('Etner nvscan_clear.scan_stop')
        try:
            sql = "select scan_uuid from task_manage where `id` = %d" % (int(self.task_id))
            res = db.get_one_item_from_db(sql)
            if res:
                self.scan_uuid = res.get('scan_uuid')

            if not self.scan_uuid:
                return
            sql = "update task_manage set scan_uuid = '' where `id` = %d" % (int(self.task_id))
            db.set_item_to_db(sql)

            self.scanner.stop_scan(self.scan_uuid)
            self.scanner.del_report(self.scan_uuid)

        except Exception, e:
            ERROR("nvscan_clear.scan_stop:"+str(e))
        DEBUG('Leave nvscan_clear.scan_stop')



if __name__ == "__main__":
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    DEBUG("========================HOSTSCAN BEGIN==========================")
    task_id = int(sys.argv[1].replace("#", ""))
    db = db_manager()
    c = nvscan_clear(task_id)
    c.scan_stop()

#end if