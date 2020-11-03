#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import atexit
import logging
import thread
import threading
import time
from Queue import Queue
from lib.common import *
#from send_udp import send_udp_thread

class ScanHostMsg_thread(threading.Thread):
    def __init__(self, queue, task_id, task_name , ports , timeout, asset_scan_id):
        try:
            threading.Thread.__init__(self)
            self.queue = queue
            self.task_id = str(task_id)
            self.task_name = task_name
            self.hostmsg_table = "hostmsg_scan"
            self.portlist_table = "port_list_scan"
            self.ports = ports
            self.timeout = timeout
            self.asset_scan_id = asset_scan_id
            self.conn = ""
            self.cursor = ""
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.__init__:" + str(e) + ",task id:" + str(task_id) + ",ports:" + str(ports) + ",timeout:" + str(timeout))
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
                    logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg.mysqlConnect reconnect:" + str(e) + ",task id:" + str(self.task_id))

            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.mysqlConnect:" + str(e) + ",task id:" + str(self.task_id))
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
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.mysqlClose:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def getOs(self,ip,timeout,iface):
        logging.getLogger().debug("File:ScanHostMsg.py, ScanHostMsg_thread.getOs start,task id:%s , ip : %s" % (self.task_id,ip))
        msg_dict = dict()
        msg_dict['flag'] = False
        msg_dict['os'] = ''
        msg_dict['runningos'] = ''
        msg_dict['osversion'] = ''
        msg_dict['macaddress'] = ''
        msg_dict['hostname'] = ''
        msg_dict['motherboard'] = ''
        msg_dict['devicetype'] = ''
        msg_dict['networkdistance'] = ''
        try:
            namp_type = ""
            if checkIpv6(ip):
                namp_type = " -6"
                return msg_dict
            #end if
            if iface == '':
                cmd = "nmap%s -O %s -P0 --host-timeout %ss " % (namp_type, ip,str(timeout))
            else:
                cmd = "nmap%s -O %s -P0 --host-timeout %ss -e %s" % (namp_type, ip,str(timeout),iface)
            #end if
            lines = vulscan_popen(cmd)
            
            if lines and len(lines) > 0:
                for row in lines:
                    row = row.replace("\n","")
                    if row.find("Device type") >= 0 and row.find(":") >= 0:
                        temp = row.split(":")
                        if len(temp) >= 2:
                            msg_dict['devicetype'] = temp[1].strip()
                        #end if
                    #end if
                    if row.find("Running") >= 0 and row.find(":") >= 0:
                        temp = row.split(":")
                        if len(temp) >= 2:
                            msg_dict['runningos'] = temp[1].strip()
                        #end if
                    #end if
                    if row.find("OS details") >= 0 or row.find("Aggressive OS guesses") >= 0:
                        temp = row.split(":")
                        if len(temp) >= 2:
                            msg_dict['os'] = temp[1].strip()
                            msg_dict['osversion'] = msg_dict['os']                            
                        #end if
                    #end if
                    if row.find("MAC Address") >= 0 and row.find(":") >= 0:
                        temp = row.split(":")
                        if len(temp) >= 4:
                            macaddr = ":".join(row.split(":")[1:]).strip()
                            msg_dict['macaddress']=macaddr.split(' ')[0]
                            msg_dict['hostname']=macaddr.split('(')[1].split(')')[0]
                        #end if  

                    #end if
                    if row.find("Network Distance") >= 0 and row.find(":") >= 0:
                        temp = row.split(":")
                        if len(temp) >= 2:
                            msg_dict['networkdistance'] = row.split(":")[1].strip()
                        #end if
                    #end if
                #end for
                msg_dict['flag'] = True
            #end if
            return msg_dict
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.getOs:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + str(ip) + ",timeout:" + str(timeout))
            return msg_dict
        #end try
    #end def
    
    def getUdpPorts(self,ip,ports,timeout,iface):
        logging.getLogger().debug("File:ScanHostMsg.py, ScanHostMsg_thread.getUdpPorts start,task id:%s , ip : %s" % (self.task_id,ip))
        port_list = []
        try:
            namp_type = ""
            if checkIpv6(ip):
                return []
                namp_type = " -6"
            #end if
            if iface == '':
                cmd = "nmap%s -sU %s -p %s -P0 --host-timeout %ss " % (namp_type,ip,str(ports),str(timeout))
            else:
                cmd = "nmap%s -sU %s -p %s -P0 --host-timeout %ss -e %s" % (namp_type,ip,str(ports),str(timeout),iface)
            #print cmd
            lines = vulscan_popen(cmd)
            state_num = 0
            service_num = 0
            if lines and len(lines) > 0:
                for row in lines:
                    row = row.replace("\n","")
                    if row.find("PORT") >= 0 and row.find("STATE") >= 0 and row.find("SERVICE") >= 0:
                        state_num = row.find("STATE")
                        service_num = row.find("SERVICE")
                    #end if
                    if row.find("/udp") >= 0 and row.find("closed") < 0:
                        port_dict = dict()
                        port_dict['port'] = row.split("/")[0]
                        port_dict['proto'] = "udp"
                        if service_num > len(row):
                            port_dict['state'] = row[state_num:].strip()
                        else:
                            port_dict['state'] = row[state_num:service_num - 1].strip()
                        #end if
                        if service_num > len(row):
                            port_dict['service'] = ""
                        else:
                            port_dict['service'] = row[service_num:].strip()
                        #end if
                        port_dict['version'] = ''
                        port_list.append(port_dict)
                    #end if
                #end for
            #end if
            
            return port_list
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.getUdpPorts:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + str(ip) + ",ports:" + str(ports))
            return port_list
        #end try
    #end def
    
    def getPorts(self,ip,ports,timeout,iface):
        logging.getLogger().debug("File:ScanHostMsg.py, ScanHostMsg_thread.getPorts start,task id:%s , ip : %s" % (self.task_id,ip))
        port_list = []
        try:
            namp_type = ""
            if checkIpv6(ip):
                namp_type = " -6"
            #end if
            if iface == '':
                cmd = "nmap%s -sV %s -p %s -P0 --host-timeout %ss " % (namp_type,ip,str(ports),str(timeout))
            else:
                cmd = "nmap%s -sV %s -p %s -P0 --host-timeout %ss -e %s" % (namp_type,ip,str(ports),str(timeout),iface)
            #print cmd
            lines = vulscan_popen(cmd)
            state_num = 0
            service_num = 0
            version_num = 0
            if lines and len(lines) > 0:
                for row in lines:
                    row = row.replace("\n","")
                    if row.find("PORT") >= 0 and row.find("STATE") >= 0 and row.find("SERVICE") >= 0 and row.find("VERSION") >= 0:
                        state_num = row.find("STATE")
                        service_num = row.find("SERVICE")
                        version_num = row.find("VERSION")
                    #end if
                    
                    if row.find("/tcp") >= 0 and row.find("closed") < 0:
                        port_dict = dict()
                        port_dict['port'] = row.split("/")[0]
                        port_dict['proto'] = "tcp"
                        if service_num > len(row):
                            port_dict['state'] = row[state_num:].strip()
                        else:
                            port_dict['state'] = row[state_num:service_num - 1].strip()
                        #end if
                        if service_num > len(row):
                            port_dict['service'] = ""
                        else:
                            if version_num > len(row):
                                port_dict['service'] = row[service_num:].strip()
                            else:
                                port_dict['service'] = row[service_num:version_num - 1].strip()
                            #end if
                        #end if
                        
                        if version_num > len(row):
                            port_dict['version'] = ""
                        else:
                            port_dict['version'] = row[version_num:].strip()
                        #end if
                        
                        port_list.append(port_dict)
                    #end if
                #end for
            #end if
            
            return port_list
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.getPorts:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + str(ip) + ",ports:" + str(ports) + ",timeout:" + str(timeout))
            return port_list
        #end try
    #end def
    
    def main(self):
        try:

            logging.getLogger("init ScanHostMsg_thread main ")

            
            while True:
                if self.queue.qsize() < 1:
                    break
                #end if
                ip = self.queue.get_nowait()
                if not ip or ip == "":
                    break
                #end if
                logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.main: start to scan ip ,task id:%s , ip : %s" % (self.task_id,ip))
                
                conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                cursor = conn.cursor(MySQLdb.cursors.DictCursor)
                
                iface = getIfaceByRoute(ip)
                
                os_msg = self.getOs(ip, 60, iface)
                port_msg = self.getPorts(ip, self.ports, self.timeout, iface)
                
                
                #update os msg
                #print os_msg['macaddress'],os_msg['os'],os_msg['runningos'],os_msg['motherboard'],os_msg['devicetype'],os_msg['networkdistance']
                '''
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "update " + self.hostmsg_table + " set `mac_address` = %s , `real_address` = '' , `os` = %s , `mother_board` = %s , `device_type` = %s , `net_distance` = %s , `web_server` = '' where `ip` = %s and `asset_scan_id` = '"+str(self.asset_scan_id)+"'"
                else:
                    sql = "update " + self.hostmsg_table + " set `mac_address` = %s , `real_address` = '' , `os` = %s , `mother_board` = %s , `device_type` = %s , `net_distance` = %s , `web_server` = '' where `ip` = %s"
                #end if
                cursor.execute(sql,(os_msg['macaddress'],os_msg['os'],os_msg['motherboard'],os_msg['devicetype'],os_msg['networkdistance'],ip))
                conn.commit()
                '''
                sql = ""

                sql = "update " + self.hostmsg_table + " set `real_address` = '' , `mother_board` = %s , `device_type` = %s , `net_distance` = %s , `host_name` = '' where `ip` = %s"
                #end if
                cursor.execute(sql,(os_msg['motherboard'],os_msg['devicetype'],os_msg['networkdistance'],ip))
                conn.commit()
                
                sql = ""
                sql = "update " + self.hostmsg_table + " set mac_address = %s where ip = %s and mac_address = ''"
                #end if
                cursor.execute(sql,(os_msg['macaddress'],ip))
                conn.commit()
                
                sql = ""
                sql = "update " + self.hostmsg_table + " set os = %s where ip = %s and os = ''"
                #end if
                cursor.execute(sql,(os_msg['os'],ip))
                conn.commit()

                sql = ""
                sql = "update " + self.hostmsg_table + " set host_name = %s where ip = %s and host_name = ''"
                cursor.execute(sql,(os_msg['hostname'],ip))
                conn.commit()
                
                #update port msg
                if port_msg and len(port_msg) > 0:
                    for port_item in port_msg:
                        port = port_item['port']
                        proto = port_item['proto']
                        state = port_item['state']
                        service = port_item['service']
                        version = port_item['version']
                        
                        #print port,proto,state,service,version
                        sql = ""
                        sql = "select `id` from %s where `ip` = '%s' and `port` = '%s' " % (self.portlist_table,ip,port)

                        cursor.execute(sql)
                        conn.commit()
                        ret = cursor.fetchone()
                        if ret and len(ret) > 0:
                            sql = "update " + self.portlist_table + " set `proto` = %s , `state` = %s , `service` = %s , `version` = %s where `id` = %s"
                            cursor.execute(sql,(proto,state,service,version,str(ret['id'])))
                            conn.commit()
                        else:
                            sql = "insert into " + self.portlist_table + " (`ip`,`port`,`proto`,`state`,`service`,`version`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s,%s)"
                            cursor.execute(sql,(ip,port,proto,state,service,version,self.asset_scan_id))
                            conn.commit()
                        #end if
                    #end for
                #end if
                
                upd_port_msg = self.getUdpPorts(ip, self.ports, self.timeout, iface)
                if upd_port_msg and len(upd_port_msg) > 0:
                    for port_item in upd_port_msg:
                        port = port_item['port']
                        proto = port_item['proto']
                        state = port_item['state']
                        service = port_item['service']
                        version = port_item['version']
                        
                        #print port,proto,state,service,version
                        sql = ""
                        sql = "select `id` from %s where `ip` = '%s' and `port` = '%s' " % (self.portlist_table,ip,port)

                        cursor.execute(sql)
                        conn.commit()
                        ret = cursor.fetchone()
                        if ret and len(ret) > 0:
                            sql = "update " + self.portlist_table + " set `proto` = %s , `state` = %s , `service` = %s , `version` = %s where `id` = %s"
                            cursor.execute(sql,(proto,state,service,version,str(ret['id'])))
                            conn.commit()
                        else:
                            sql = "insert into " + self.portlist_table + " (`ip`,`port`,`proto`,`state`,`service`,`version`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s,%s)"
                            cursor.execute(sql,(ip,port,proto,state,service,version,self.asset_scan_id))
                            conn.commit()
                        #end if
                    #end for
                #end if
                
                
                current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                sql = ""
                sql = "update hostmsg_scan set `port_state` = '1' where `ip` = '%s'" % (ip)

                cursor.execute(sql)
                conn.commit()
                #sql = "update hostmsg_%s set `end_time` = '%s' where `ip` = '%s' and `host_state` = '1' and `web_state` = '1' and `weak_state` = '1'" % (self.task_id,current_time,ip)
                #self.cursor.execute(sql)
                #self.conn.commit()

                sql = ""
            	sql = "update hostmsg_task set `state` = '2'"       
            	cursor.execute(sql)
            	conn.commit()    
                
                cursor.close()
                conn.close()
                
            #end while
            
            #self.mysqlClose()
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.main:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def

    def run(self):
        try:
            logging.getLogger().debug("File:ScanHostMsg.py, ScanHostMsg_thread.run: thread start ,task id:%s" % (self.task_id))
            self.main()
            logging.getLogger().debug("File:ScanHostMsg.py, ScanHostMsg_thread.run: thread end ,task id:%s" % (self.task_id))
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg_thread.run:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def
#end class

class ScanHostMsg:
    def __init__(self,task_id):
        try:
            self.task_id = str(task_id)
            self.state = 2
            self.port_enable = 1
            self.port_state = 0
            self.taskname = ""
            self.conn = ""
            self.cursor = ""
            self.target = Queue()
            self.targetCount = 0
            self.timeout = "5"
            self.ports = "21,22,23,3389,3306"
            self.thread = 5
            self.hostmsg_table = "hostmsg_scan"
            self.asset_scan_id = 0
            
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg.__init__:" + str(e) + ",task id:" + str(task_id))
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
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg.mysqlConnect:" + str(e) + ",task id:" + str(self.task_id))
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
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg.mysqlClose:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def init(self):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            #sql = "select t.task_name as task_name,t.asset_scan_id as asset_scan_id,t.state as state,t.port_enable as port_enable,t.port_state as port_state,t.port_timeout as timeout,p.ports as ports,t.port_thread as thread from task_manage t,port_manage p where t.port_policy=p.id and t.id='" + self.task_id + "' "
            #cursor.execute(sql)
            #conn.commit()
            #ret = cursor.fetchone()
            logging.getLogger().error("File:ScanHostMsg.py, init: ret12424242424:")

            self.state = "3"
            self.port_enable = 1
            self.port_state = 0
            self.taskname = "hostmsg_task"
            self.timeout = "2"
            self.ports = "23,21,80,8080,3389,139,3306,135,1433,22,1,5,7,9,11,13,17,18,19,20,25,31,53,67,37,39,42,43,49,50,63,68,69,70,71,72,73,79,88,95,101,102,105,107,109,110,111,113,115,117"
            self.thread = 5
            self.asset_scan_id = 0
            port_count = 0
            portlist = self.ports.split(",")
            for port_item in portlist:
                if port_item.find("-") >= 0:
                    port_count += (int(port_item.split("-")[1]) - int(port_item.split("-")[0]))
                else:
                    port_count += 1
                #end if
            #end for
            self.timeout = self.timeout * port_count
            if self.timeout > 600:
                self.timeout = 600
            #end if

            if self.port_enable == 1 and self.port_state == 0:
                cursor.close()
                conn.close()
                return True
            else:
                cursor.close()
                conn.close()
                return False
            #end if

        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg.init:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try    
    #end def
    
    def main(self):
        try:
            logging.getLogger().error("File:ScanHostMsg.py, main: main start ,task id:" + str(task_id))
            if self.init():
                while True:

                    conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                    cursor = conn.cursor(MySQLdb.cursors.DictCursor)     
                    prescan_state = 1
                    sql = ""
                    sql = "select `ip` from hostmsg_scan where `state` = '1' and `port_state` <> '1'"

                    cursor.execute(sql)
                    conn.commit()
                    ret = cursor.fetchall()
                    logging.getLogger().error("File:ScanHostMsg.py, main:ip:"+str(ret))
                    cursor.close()
                    conn.close()
                
                    if ret and len(ret) > 0:
                        for row in ret:
                            self.target.put(row['ip'])
                        #end for
                        if self.target.qsize() > 0:
                            list = []
                    
                            i = 0
                            for i in range(self.thread):
                                temp = ScanHostMsg_thread(self.target,self.task_id,self.taskname,self.ports,self.timeout,self.asset_scan_id)
                                list.append(temp)
                            #end for
                    
                            i = 0
                            for i in range(len(list)):
                                list[i].start()
                            #end for
                    
                            i = 0
                            for i in range(len(list)):
                                list[i].join()
                            #end for
                        #end if
                    #end if
                    if prescan_state == 1:
                        break
                    else:
                        time.sleep(5)
                        continue
                    #end if
                #end while
            #end if
            #self.end()
            #self.mysqlClose()
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsg.py, ScanHostMsg.main:" + str(e) + ",task id:" + str(self.task_id))
            #self.end()
        #end try    
    #end def
#end class

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        if len(sys.argv) == 2:
            task_id = sys.argv[1].replace("#","")
            
            cmd = "/usr/bin/python /var/waf/ScanHostMsg.py %s#" % (task_id)
            res = checkProcess(cmd)
            if res == False:
                logging.getLogger().error("File:ScanHostMsg.py, __main__: Process: %s is exist" % (cmd))
                sys.exit(0)
            #end if
            
            scanHostMsg = ScanHostMsg(task_id)
            scanHostMsg.main()
        else:
            print "args error!"
        #end if
    except Exception,e:
        logging.getLogger().error("File:ScanHostMsg.py, __main__:" + str(e) + ",task id:" + str(task_id))
    #end try
#end if

