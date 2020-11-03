#!/usr/bin/python
#-*-encoding:UTF-8-*-
import MySQLdb
from Queue import Queue
import threading
import time
import logging
import socket
import sys
import threading
import GetDomainThread
import ScanDomainThread
from lib.common import *
from lib.waf_netutil import *

class WebScan:
    def __init__(self,task_id,type):
        try:
            self.conn = ""
            self.cursor = ""
            self.task_id = str(task_id)
            self.type = type
            self.task_name = ""
            self.hostmsg_table      = "hostmsg_" + self.task_id
            self.port_list_table    = "port_list_" + self.task_id
            self.domain_list_table  = "domain_list_" + self.task_id
            self.scan_result_table  = "scan_result_" + self.task_id
            self.scan_result_table_en  = "scan_result_" + self.task_id + "_en"
            self.url_list_table     = "url_list_" + self.task_id
            self.state = 2
            self.init_state = 1
            self.prescan_state = 1
            self.web_enable = 1
            self.web_spider_enable = 1
            self.web_thread = 1
            self.target = ''
            self.thread_lock = threading.Lock()
            
            self.domain_queue = Queue()
            
            self.asset_scan_id = 0
            print '''------------------------------------------------------------
WebScan 初始化成功
------------------------------------------------------------'''
        except Exception,e:
            logging.getLogger().error("File:WebScan.py, WebScan.__init__:" + str(e) + ",task id:" + str(task_id))
        #end try
    #end def
    
    def mysqlConnect(self):
        def reconnect():
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            if self.conn == '' or self.cursor == '':
                reconnect()
            else:
                try:
                    self.conn.ping()
                except MySQLdb.OperationalError,e:
                    self.mysqlClose()
                    reconnect()
                    logging.getLogger().error("File:WebScan.py, WebScan.mysqlConnect reconnect:" + str(e) + ",task id:" + str(self.task_id))
            print '''------------------------------------------------------------
数据库连接成功
------------------------------------------------------------'''
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:WebScan.py, WebScan.mysqlConnect:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def mysqlClose(self):
        try:
            if self.conn != '' and self.cursor != '':
                self.cursor.close()
                self.conn.close()
            #end if
            self.conn = ''
            self.cursor = ''
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:WebScan.py, WebScan.mysqlClose:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def init(self):
        try:
            if self.mysqlConnect():
                #create_scanlog_tmp(self.task_id)
                if self.update_domain_list_table() and self.update_hostmsg_table() and self.update_url_list_table() and self.update_scan_result_table() and self.update_scan_result_table_en():
	                if self.type == 'reinit':
	                    
	                    sql = "update `task_manage` set `web_state` = '0', `web_getdomain_state` = '0' where `id` = '%s' " % (self.task_id)
	                    self.cursor.execute(sql)
	                    
	                    sql = ""
	                    sql = "delete from domain_list_%s " % (self.task_id)
	                    self.cursor.execute(sql)
	                    
	                    sql = ""
	                    sql = "delete from scan_result_%s " % (self.task_id)
	                    self.cursor.execute(sql)
	                    
	                    sql = ""
	                    sql = "delete from url_list_%s " % (self.task_id)
	                    self.cursor.execute(sql)
	                    self.conn.commit()
	                    clear_scanlog(self.task_id)

	                #end if
	                sql = "select `task_name`,`asset_scan_id`,`web_target`,`state`,`init_state`,`prescan_state`,`web_enable`,`web_spider_enable`,`web_state`,`web_thread`,`web_getdomain_timeout`,`web_getdomain_policy`,`web_getdomain_state` from `task_manage` where `id` = '%s'" % (self.task_id)
	                self.cursor.execute(sql)
	                self.conn.commit()
	                res = self.cursor.fetchone()
	                if res and len(res) > 0:
	                    self.task_name = res['task_name']
	                    self.state = res['state']
	                    self.init_state = res['init_state']
	                    self.prescan_state = res['prescan_state']
	                    self.web_enable = res['web_enable']
	                    self.web_spider_enable = res['web_spider_enable']
	                    self.web_thread = res['web_thread']
	                    self.target = res['web_target']
	                    self.asset_scan_id = res['asset_scan_id']
	                    
	                else:
	                    logging.getLogger().error("File:WebScan.py, WebScan.init  : get config error ,task id:" + str(self.task_id))
	                    return False
	                #end if
                
                	#create_web_tmp(self.task_id)
                	return True
                #end if
            else:
                logging.getLogger().error("File:WebScan.py, WebScan.init  : mysql connect error ,task id:" + str(self.task_id))
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:WebScan.py, WebScan.init:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def startTask(self):
        try:
            if self.init():   
                #判断初始初始化是否成功
                if self.init_state == 0:
                    logging.getLogger().debug("File:WebScan.py, WebScan.start: task not init ,task id:" + str(self.task_id))
                    return
                #end if
                #判断是否开启了Web漏洞扫描
                if self.web_enable == 0:
                    self.endTask()
                    logging.getLogger().debug("File:WebScan.py, WebScan.start: web_enable is 0 ,task id:" + str(self.task_id))
                    return
                #end if
                #调用获取域名的线程和扫描域名的线程
                thread_list = []
                thread_list.append(GetDomainThread.GetDomainThread(self.task_id,self.domain_queue))
                for i in range(self.web_thread):
                    thread_list.append(ScanDomainThread.ScanDomainThread(self.task_id,self.domain_queue,self.thread_lock))
                #end for
                for t in thread_list:
                    t.start()

                #end for
                for t in thread_list:
                    t.join()
                #end for
                
                self.endTask()
            else:
                logging.getLogger().error("File:WebScan.py, WebScan.start: init function error ,task id:" + str(self.task_id))
            #end if
            
            #self.endTask()
        except Exception,e:
            #self.endTask()
            logging.getLogger().error("File:WebScan.py, WebScan.start:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def
    
    def endTask(self):
        try:
            logging.getLogger().debug("File:WebScan.py, WebScan.endTask: task come to end ,task id:" + str(self.task_id))
            current_time = time.strftime("%Y-%m-%d %X",time.localtime())
            if self.mysqlConnect():
                
                sql = ""
                sql = "select count(*) as c from domain_list_%s where `state` <> '1'" % (self.task_id)

                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                if res and len(res) and res['c'] == 0:
                    sql = "update task_manage set web_state = '1' where id = '%s'" % (self.task_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    vulscan_popen("rm -R /var/webs/task_id" + self.task_id + "domain_id*")
                #end if
                
                sql = ""
                sql = "update hostmsg_%s set `end_time` = now() where `state` = '1' and `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1' and `end_time` = NULL" % (self.task_id)
                self.cursor.execute(sql)
                self.conn.commit()
                
                #check task state and end_time
                sql = "update `task_manage` set `state` = '3', `end_time` = now() where `id` = '%s' and `init_state` = '1' and `prescan_state` = '1' and `port_state` = '1' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1'" % (self.task_id)
                self.cursor.execute(sql)
                self.conn.commit()
                
                remove_web_tmp(self.task_id)
                                
                #updateTaskManage()
                #check_if_all_end(self.task_id)
                #updateAssetCount(self.task_id,self.asset_scan_id)
                
            else:
                logging.getLogger().debug("File:WebScan.py, WebScan.endTask: connect mysql error ,task id:" + str(self.task_id))
            #end if
        except Exception,e:
            logging.getLogger().error("File:WebScan.py, WebScan.endTask:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end if

    def update_hostmsg_table(self):
        try:
            self.mysqlConnect()
            if self.asset_scan_id <= 0:
                if table_exists(self.hostmsg_table):
                    sql = "drop table " + self.hostmsg_table
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
            #end if
            
            if table_exists(self.hostmsg_table):
                sql = "truncate table " + self.hostmsg_table
            else:
                sql = "create table " + self.hostmsg_table + "("
                sql += "`id` int(11) NOT NULL AUTO_INCREMENT,"
                sql += "`task_id` int(11) DEFAULT NULL,"
                sql += "`task_name` varchar(256) DEFAULT NULL,"
                sql += "`ip` varchar(45) DEFAULT NULL,"
                sql += "`state` int(1) DEFAULT NULL,"
                sql += "`port_state` int(1) DEFAULT NULL,"
                sql += "`host_state` int(1) DEFAULT NULL,"
                sql += "`web_state` int(1) DEFAULT NULL,"
                sql += "`weak_state` int(1) DEFAULT NULL,"
                sql += "`mac_address` varchar(128) DEFAULT '',"
                sql += "`real_address` varchar(256) DEFAULT NULL,"
                sql += "`os` varchar(512) DEFAULT '',"
                sql += "`mother_board` varchar(128) DEFAULT NULL,"
                sql += "`device_type` varchar(128) DEFAULT NULL,"
                sql += "`net_distance` varchar(128) DEFAULT NULL,"
                sql += "`web_server` varchar(128) DEFAULT NULL,"
                sql += "`start_time` timestamp NULL DEFAULT NULL,"
                sql += "`end_time` timestamp NULL DEFAULT NULL,"
                sql += "`asset_scan_id` int(11) default 0,"
                sql += "`host_progress` int(3) DEFAULT 0,"
                sql += "`weak_progress` int(3) DEFAULT 0,"
                sql += "PRIMARY KEY (`id`),"
                sql += "KEY `asset_scan_id` (`asset_scan_id`),"
                sql += "KEY `ip` (`ip`)"
                sql += ")ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.update_hostmsg_table:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try 
    #end def

    def update_domain_list_table(self):
        try:
            self.mysqlConnect()
            if self.asset_scan_id <= 0:
                if table_exists(self.domain_list_table):
                    sql = "drop table " + self.domain_list_table
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
            #end if
            if table_exists(self.domain_list_table):
                sql = "truncate table " + self.domain_list_table
            else:
                sql = "create table " + self.domain_list_table + "("
                sql += "`id` int(10) NOT NULL AUTO_INCREMENT,"
                sql += "`task_id` int(10) DEFAULT NULL,"
                sql += "`task_name` varchar(512) DEFAULT NULL,"
                sql += "`scheme` varchar(6) DEFAULT 'http',"
                sql += "`domain` varchar(500) DEFAULT NULL,"
                sql += "`ip` varchar(45) DEFAULT NULL,"
                sql += "`state` int(1) DEFAULT NULL,"
                sql += "`spider_state` int(1) DEFAULT NULL,"
                sql += "`progress` text DEFAULT NULL,"
                sql += "`progress_status` mediumtext,"
                sql += "`exception` varchar(512) DEFAULT NULL,"
                sql += "`exception_count` int(1) DEFAULT NULL,"
                sql += "`title` varchar(500) DEFAULT NULL,"
                sql += "`base_path` varchar(500) DEFAULT NULL,"
                sql += "`policy` int(1) DEFAULT NULL,"
                sql += "`policy_detail` text default NULL,"
                sql += "`service_type` varchar(255) DEFAULT NULL,"
                sql += "`site_type` varchar(255) DEFAULT NULL,"
                sql += "`database_type` varchar(255) DEFAULT NULL,"
                sql += "`start_time` timestamp NULL DEFAULT NULL,"
                sql += "`end_time` timestamp NULL DEFAULT NULL,"
                sql += "`next_start_time` timestamp NULL DEFAULT NULL,"
                sql += "`cookie_url` varchar(1024) DEFAULT NULL,"
                sql += "`begin_path` varchar(500) DEFAULT NULL,"
                sql += "`asset_scan_id` int(11) default 0,"
                sql += "`exclude_url` text DEFAULT NULL,"
                sql += "PRIMARY KEY (`id`),"
                sql += "KEY `asset_scan_id` (`asset_scan_id`),"
                sql += "KEY `ip` (`ip`)"
                sql += ")ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.update_domain_list_table:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def

    def update_scan_result_table(self):
        try:
            self.mysqlConnect()
            if self.asset_scan_id <= 0:
                if table_exists(self.scan_result_table):
                    sql = "drop table " + self.scan_result_table
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
            #end if
            if table_exists(self.scan_result_table):
                sql = "truncate table " + self.scan_result_table
            else:
                sql = "create table " + self.scan_result_table + "("
                sql += "`id` int(11) NOT NULL auto_increment,"
                sql += "`domain_id` int(11) default NULL,"
                sql += "`url` varchar(500) default NULL,"
                sql += "`ip` varchar(45) default NULL,"
                sql += "`vul_type` varchar(512) default NULL,"
                sql += "`domain` varchar(255) default NULL,"
                sql += "`level` varchar(10) default NULL,"
                sql += "`detail` mediumtext,"
                sql += "`output` mediumtext,"
                sql += "`vul_id` int(11) default NULL,"
                sql += "`request` mediumtext,"
                sql += "`response` mediumtext,"
                sql += "`asset_scan_id` int(11) default 0,"
                sql += "`report` int(11) default 0,"
                sql += "`vul_name` varchar(255) default '',"
                sql += "`solu` text,"
                sql += "PRIMARY KEY (`id`),"
                sql += "KEY `asset_scan_id` (`asset_scan_id`),"
                sql += "KEY `vul_id` (`vul_id`),"
                sql += "KEY `domain_id` (`domain_id`)"
                sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.update_scan_result_table:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def

    def update_scan_result_table_en(self):
        try:
            self.mysqlConnect()
            if self.asset_scan_id <= 0:
                if table_exists(self.scan_result_table_en):
                    sql = "drop table " + self.scan_result_table_en
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
            #end if
            if table_exists(self.scan_result_table_en):
                sql = "truncate table " + self.scan_result_table_en
            else:
                sql = "create table " + self.scan_result_table_en + "("
                sql += "`id` int(11) NOT NULL auto_increment,"
                sql += "`domain_id` int(11) default NULL,"
                sql += "`url` varchar(500) default NULL,"
                sql += "`ip` varchar(45) default NULL,"
                sql += "`vul_type` varchar(512) default NULL,"
                sql += "`domain` varchar(255) default NULL,"
                sql += "`level` varchar(10) default NULL,"
                sql += "`detail` mediumtext,"
                sql += "`output` mediumtext,"
                sql += "`vul_id` int(11) default NULL,"
                sql += "`request` mediumtext,"
                sql += "`response` mediumtext,"
                sql += "`asset_scan_id` int(11) default 0,"
                sql += "`report` int(11) default 0,"
                sql += "`vul_name` varchar(255) default '',"
                sql += "`solu` text,"
                sql += "PRIMARY KEY (`id`),"
                sql += "KEY `asset_scan_id` (`asset_scan_id`),"
                sql += "KEY `vul_id` (`vul_id`),"
                sql += "KEY `domain_id` (`domain_id`)"
                sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.update_scan_result_table_en:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def

    def update_url_list_table(self):
        try:
            self.mysqlConnect()
            if self.asset_scan_id <= 0:
                if table_exists(self.url_list_table):
                    sql = "drop table " + self.url_list_table
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
            #end if
            if table_exists(self.url_list_table):
                sql = "truncate table " + self.url_list_table
            else:
                sql = "create table " + self.url_list_table + "("
                sql += "`id` int(11) NOT NULL auto_increment,"
                sql += "`domain_id` int(11) default NULL,"
                sql += "`url` varchar(500) default NULL,"
                sql += "`params` text default NULL,"
                sql += "`method` varchar(5) default NULL,"
                sql += "`refer` varchar(500) default NULL,"
                sql += "`asset_scan_id` int(11) default 0,"
                sql += "PRIMARY KEY (`id`),"
                sql += "KEY `asset_scan_id` (`asset_scan_id`)"
                sql += ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.update_url_list_table:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
#end class 

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        '''
        task_id = str(sys.argv[1])
        
        if len(sys.argv) == 3:
            task_id = str(sys.argv[1].replace("#", ""))
            type = sys.argv[2]
            
            cmd = "/usr/bin/python /var/waf/WebScan.py %s# %s" % (task_id,type)
            res = checkProcess(cmd)
            if res == False:
                logging.getLogger().error("File:WebScan.py, __main__: Process: %s is exist" % (cmd))
                sys.exit(0)
            #end if 
            ob = WebScan(task_id,type)
            ob.startTask()
        elif len(sys.argv) == 2:
            task_id = str(sys.argv[1].replace("#", ""))
            type = "init"
            cmd = "/usr/bin/python /var/waf/WebScan.py %s#" % (task_id)
            res = checkProcess(cmd)
            if res == False:
                logging.getLogger().error("File:WebScan.py, __main__: Process: %s is exist" % (cmd))
                sys.exit(0)
            #end if
            ob = WebScan(task_id,type)
            ob.startTask()
        else:
            print "WebScan.py argv error"
        #end if
        '''
        task_id = sys.argv[1]#186   # webscan9
        type = "reinit"
        cmd = "/usr/bin/python /var/waf/WebScan.py %s#" % (task_id)
        res = checkProcess(cmd)
        if res == False:
            print '''------------------------------------------------------------
checkProcess 结果: False
------------------------------------------------------------'''
            logging.getLogger().error("File:WebScan.py, __main__: Process: %s is exist" % (cmd))
            sys.exit(0)
        #end if
        ob = WebScan(task_id,type)
        ob.startTask()
    except Exception,e:
        logging.getLogger().error("File:WebScan.py, __main__:" + str(e))
    #end try
#end if

