#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import atexit
import logging
import thread
import threading
import struct
from Queue import Queue
from lib.common import *
from lib.waf_netutil import *


class PreScan_thread(threading.Thread):
    def __init__(self, queue, task_id, hostmsg_table, asset_scan_id):
        try:
            threading.Thread.__init__(self)
            self.queue = queue
            self.task_id = str(task_id)
            self.hostmsg_table = hostmsg_table
            self.conn = ""
            self.cursor = ""
            
            self.asset_scan_id = asset_scan_id
            
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan_thread.__init__:" + str(e) + ",task id:" + str(task_id))
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
                    logging.getLogger().error("File:PreScan.py, PreScan.mysqlConnect reconnect:" + str(e) + ",task id:" + str(self.task_id))
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:PreScan.py, PreScan_thread.mysqlConnect:" + str(e) + ",task id:" + str(self.task_id))
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
            logging.getLogger().error("File:PreScan.py, PreScan_thread.mysqlClose:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def checkIp(self,ip):
        try:
            iface = getIfaceByRoute(ip)
            cmd = ""
            cmd_iptype = ""
            if ip.find(":") > 0 and checkIpv6(ip):
                cmd_iptype = " -6"
            #end if
            if iface == '':
                cmd = "/usr/bin/nmap %s -sP %s --host-timeout 60s" % (cmd_iptype, ip)
            else:
                cmd = "/usr/bin/nmap %s -sP %s --host-timeout 60s -e %s" % (cmd_iptype, ip, iface)
            #end if
            lines = vulscan_popen(cmd)
            for row in lines:
                if row.find('#') < 0:
                    if row.find('MAC Address') >= 0 or row.find("appears to be up") >= 0 or row.find("1 host up") >= 0:
                        return True
                    #end if
                #end if
            #end for

            if checkIpv6(ip):
                if iface == "":
                    cmd = "/usr/bin/nmap -6 %s -p 21,23,25,80,135,139,445,2121,3389,3306,1433,7777,2433,5631,4899,5800,5900,8000,8080,16433 --host-timeout 30s -P0" % (ip)
                else:
                    cmd = "/usr/bin/nmap -6 %s -p 21,23,25,80,135,139,445,2121,3389,3306,1433,7777,2433,5631,4899,5800,5900,8000,8080,16433 --host-timeout 30s -P0 -e %s" % (ip, iface)
                #end if
            else:
                if iface == "":
                    cmd = "/usr/bin/nmap -sS %s -p 21,23,25,80,135,139,445,2121,3389,3306,1433,7777,2433,5631,4899,5800,5900,8000,8080,16433 --host-timeout 30s -P0" % (ip)
                else:
                    cmd = "/usr/bin/nmap -sS %s -p 21,23,25,80,135,139,445,2121,3389,3306,1433,7777,2433,5631,4899,5800,5900,8000,8080,16433 --host-timeout 30s -P0 -e %s" % (ip, iface)

            lines = vulscan_popen(cmd)
            for row in lines:
                if (row.find('/tcp') > 0 and row.find('open') > 0) or row.find('MAC Address') >= 0:
                    return True
                #end if
            #end for
            
            return False
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan_thread.checkIp:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + str(ip))
            return False
        #end try
    #end def
    
    def update_ip_range(self,list1,list2,force=False):
        try:
            count = len(list1) + len(list2)
            if count < 1:
                return False
            #end if
            if self.mysqlConnect():
                if count > 2 or force:
                    #print "update ip range"
                    values1 = []
                    values2 = []
                    for ip in list1:
                        if checkIpv6(ip):
                            ip_full = fullIpv6(ip)
                            ip = easyIpv6(ip_full)
                        values1.append("'%s'" % (ip))
                    #end for
                    for ip in list2:
                        if checkIpv6(ip):
                            ip_full = fullIpv6(ip)
                            ip = easyIpv6(ip_full)
                        values2.append("'%s'" % (ip))
                    #end for
                    values1 = ','.join(values1)
                    values2 = ','.join(values2)
                    
                    if values1 != '':
                        sql = ""
                        sql = "update hostmsg_scan set `state` = '1' where `ip` in (%s) and `state` = '0'" % (values1.lower())

                        self.cursor.execute(sql)
                        self.conn.commit()
                    #end if
                    if values2 != '':
                        sql = ""
                        sql = "update hostmsg_scan set `state` = '2', port_state = '1', host_state = '1', web_state = '1', weak_state = '1' where `ip` in (%s) and `state` = '0'" % (values2.lower())
                        
                        self.cursor.execute(sql)
                        self.conn.commit()
                    #end if
                    
                    return True
                else:
                    return False
                #end if
            else:
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan_thread.update_ip_range:" + str(e) + ",task id:" + self.task_id)
            return False
        #end try
    #end def
        
    def run(self):
        try:
            list1 = []
            list2 = []
            while True:
                if self.queue.qsize() < 1:
                    print "prescan thread exit"
                    break
                #end if
                ip = self.queue.get_nowait()
                
                if not ip or ip == "":
                    print "prescan thread exit"
                    break
                #end if
                
                if self.mysqlConnect():
                    if self.checkIp(ip):
                        #flag = 1
                        print "11111111111111"
                        list1.append(ip)
                        if self.update_ip_range(list1,list2):
                            list1 = []
                            list2 = []
                        #end if
                        #self.sendMsg(ip)
                    else:
                    	print "222222222222"
                        list2.append(ip)
                        if self.update_ip_range(list1,list2):
                            list1 = []
                            list2 = []
                        #end if
                    #end if
                #end if
            #end while
            self.update_ip_range(list1, list2, True)
            self.update_ip_range(list1, list2, True)
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan_thread.run:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def


class PreScan:
    def __init__(self,task_id,type):
        try:
            self.task_id            = str(task_id)
            self.type               = type
            self.task_name          = "hostmsg_task"
            self.init_thread        = 1
            self.asset_scan_id      = 0
            self.hostmsg_table      = "hostmsg_scan"
            self.port_list_table    = "port_list_scan"
            self.conn               = ""
            self.cursor             = ""
            self.queue              = Queue()
            #self.queueLock          = threading.Lock()
            self.ip_list            = []
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.__init__:" + str(e) + ",task id:" + str(task_id))
        #end try
    #end def
    
    def mysqlConnect(self):
        try:
            
            if self.conn == '' or self.cursor == '':
                self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:PreScan.py, PreScan.mysqlConnect:" + str(e) + ",task id:" + str(self.task_id))
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
            logging.getLogger().error("File:PreScan.py, PreScan.mysqlClose:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def insert_ip(self,ip,isIp):
        try:
            self.mysqlConnect()
            current_time = time.strftime("%Y-%m-%d %X",time.localtime())
            ip = ip.lower()
            if checkIpv6(ip):
                ip_full = fullIpv6(ip)
                ip = easyIpv6(ip_full)
            if isIp:
                sql = "insert into hostmsg_scan (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values ('%s','%s','%s','0','0','0','0','0','%s','%s')" % (0,"hostmsg_task",ip,current_time,0)
            else:
                sql = "insert into hostmsg_scan (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values ('%s','%s','%s','1','0','0','0','0','%s','%s')" % (0,"hostmsg_task",ip,current_time,0)
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.insert_ip:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + str(ip))
        #end try
    #end def
    
    def insert_ip_range(self,list,force=False):
        try:
            if len(list) < 1:
                return False
            #end if
            if self.mysqlConnect():
                current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                if len(list) > 1000 or force:
                    values1 = []
                    for ip in list:
                        values1.append("('%s','%s','%s','0','0','0','0','0','%s','%s')" % (0,"hostmsg_task",ip.lower(),current_time,0))
                    #end for
                    values1 = ','.join(values1)
                    
                    sql = "insert into hostmsg_scan (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values %s" % (values1)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    return True
                else:
                    return False
                #end if
            else:
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.insert_ip_range:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def init(self):
        try:
            if self.mysqlConnect():
                sql = "select `target` from `hostmsg_task`"
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                target = res['target']
                targetList = target.split(',')
                
                if self.update_hostmsg_table() and self.update_port_list_table():
                    sql = "select `ip` from hostmsg_scan"
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchall()
                    for r in res:
                        if checkIpv6(r['ip']):
                            self.ip_list.append(fullIpv6(r['ip']))
                        else:
                            self.ip_list.append(r['ip'])
                        #end if
                    #end for
                  
                    list = []
                    for url in targetList:
                        #check ipv4 or ipv6
                        ipv4_enable = checkIpv4(url)
                        ipv6_enable = checkIpv6(url)
                        if ipv4_enable or ipv6_enable:
                            ip_full = url
                            if ipv6_enable:
                                ip_full = fullIpv6(url)
                            #end if
                            if ip_full in self.ip_list:
                                continue
                            else:
                                self.ip_list.append(ip_full)
                            #end if
                            list.append(url)
                            if self.insert_ip_range(list):
                                list = []
                            #end if

                            continue
                        #end if
                        #check ipv4 range or ipv6 range
             
                        ipv4_range_enable = checkIpv4Range(url)
                        ipv6_range_enable = checkIpv6Range(url)
                        if ipv4_range_enable or ipv6_range_enable:
                            url_list = url.split("-")
                            ip_list = []
                            if ipv6_range_enable:
                                if checkIpv6(url_list[1]):
                                    ip_list = getIpv6Range(url_list[0], url_list[1])
                                else:
                                    last_colon_index = 0
                                    url_end = ''
                                    for i in range(len(url_list[0])):
                                        if url_list[0][i] == ':':
                                            last_colon_index = i
                                    url_end = url_list[0][:last_colon_index+1] + url_list[1]
                                    ip_list = getIpv6Range(url_list[0], url_end)
                            else:
                                ip_list = getIpv4Range(url_list[0], url_list[1])
                            #end if
                            for ip in ip_list:
                                ip_full = ip
                                if ipv6_range_enable:
                                    ip_full = fullIpv6(ip)
                                    ip = easyIpv6(ip_full)
                                #end if
                                if ip_full in self.ip_list:
                                    continue
                                else:
                                    self.ip_list.append(ip_full)
                                #end if

                                list.append(ip)
                                if self.insert_ip_range(list):
                                    list = []
                                #end if
                            #end for

                            continue
                        #end if
                    #end for
                    self.insert_ip_range(list, True)
                #end if
            else:
                logging.getLogger().error("File:PreScan.py, PreScan.init: mysql connect error ,task id:" + str(self.task_id))
            #end if
            self.mysqlClose()
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.init:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def
    
    def update_hostmsg_table(self):
        try:
            self.mysqlConnect()
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
                sql += "`host_name` varchar(128) DEFAULT '',"
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
    
    def update_port_list_table(self):
        try:
            self.mysqlConnect()
            if table_exists(self.port_list_table):
                sql = "truncate table " + self.port_list_table
            else:
                sql = "create table " + self.port_list_table + "("
                sql += "`id` int(11) NOT NULL auto_increment,"
                sql += "`ip` varchar(45) default NULL,"
                sql += "`state` varchar(50) default NULL,"
                sql += "port int(10) default NULL,"
                sql += "proto varchar(10) default NULL,"
                sql += "service varchar(255) default NULL,"
                sql += "version varchar(255) default NULL,"
                sql += "`asset_scan_id` int(11) default 0,"
                sql += "PRIMARY KEY  (`id`),"
                sql += "KEY `asset_scan_id` (`asset_scan_id`),"
                sql += "KEY `ip` (`ip`)"
                sql += ")ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8"
            #end if
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.update_port_list_table:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try 
    #end def
    
    def main(self):
        try:
            self.mysqlConnect()
            
            hostmsg_table = table_exists(self.hostmsg_table)
            
            port_list_table = table_exists(self.port_list_table)
               
            if hostmsg_table and port_list_table:
                
                sql = ""
                sql = "select `ip` from %s where `state` = '0'" % (self.hostmsg_table)
                self.cursor.execute(sql)
                self.conn.commit()
                ret = self.cursor.fetchall()
                if ret and len(ret) > 0:
                    for row in ret:
                        ip = row['ip']
                        print ip
                        self.queue.put(ip)
                    #end for
                #end if
                  
                self.init_thread = 30
                
                list = []
                for i in range(self.init_thread):
                    temp = PreScan_thread(self.queue,self.task_id,self.hostmsg_table,self.asset_scan_id)
                    list.append(temp)
                #end for
                
                for i in range(len(list)):
                    list[i].start()
                #end for
                
                for i in range(len(list)):
                    list[i].join()
                #end for
            #end if
            sql = ""
            sql = "update hostmsg_task set `state` = '1'"     
            self.cursor.execute(sql)
            self.conn.commit()
            self.mysqlClose()
        except Exception,e:
            logging.getLogger().error("File:PreScan.py, PreScan.main:" + str(e) + ",task id:" + str(self.task_id))
        #end try    
    #end def
#end class

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        if len(sys.argv) == 1: 
            cmd = "/usr/bin/python /var/waf/PreScan.py 115# init"
            res = checkProcess(cmd)
            if res == False:
                logging.getLogger().error("File:PreScan.py, __main__: Process: %s is exist" % (cmd))
                sys.exit(0)
            #end if
            
            prescan = PreScan("115","init")
            prescan.init()
            prescan.main()
            syslog_vul_begin("115", prescan.task_name.encode("utf8"))
        elif len(sys.argv) == 2:
            task_id = sys.argv[1].replace("#", "")
            prescan = PreScan(task_id,'')
            prescan.main()
        else:
            print "args error!"
        #end if
    except Exception,e:
        logging.getLogger().error("File:PreScan.py, __main__:" + str(e) + ",task id:115")
    #end try
#end if

